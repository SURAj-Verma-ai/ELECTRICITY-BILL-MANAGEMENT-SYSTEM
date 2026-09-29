import os
import re
import sqlite3
import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from flask import Flask, request, session, jsonify, send_from_directory, abort
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_TIME_LIMIT'] = None

DB_NAME = "ebill.db"
UNIT_RATE = 7.0
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
DIST_DIR = os.path.join(app.static_folder, 'dist')

METER_RE = re.compile(r'^[A-Za-z0-9\-]{1,32}$')
MONTH_RE = re.compile(r'^\d{4}-\d{2}$')
CATEGORY_WHITELIST = {'Power Interruption', 'Meter Fault', 'Billing', 'Other'}
STATUS_WHITELIST = {'Pending', 'In Progress', 'Resolved'}

csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour", "50 per minute"])

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler("logs/ebms.log", maxBytes=1_000_000, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.before_request
def log_request():
    logger.info(f"[REQUEST] {request.method} {request.path} | IP: {request.remote_addr}")


def get_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"[DB_ERROR] Failed to connect to {DB_NAME}: {str(e)}")
        raise


def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                meter_no TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consumer_id INTEGER,
                month TEXT NOT NULL,
                units INTEGER NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'Unpaid',
                FOREIGN KEY (consumer_id) REFERENCES consumers (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                consumer_id INTEGER,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (consumer_id) REFERENCES consumers (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()


def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    with get_db() as conn:
        conn.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))
        conn.commit()


init_db()


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify(error="unauthorized"), 401
        return f(*args, **kwargs)
    return decorated


def row_to_dict(row):
    return dict(row) if row else None


def clean_text(value, max_len=200):
    if not isinstance(value, str):
        return ''
    return value.strip()[:max_len]


# ---------- API ----------

@app.route('/api/csrf-token')
def csrf_token():
    from flask_wtf.csrf import generate_csrf
    return jsonify(csrf_token=generate_csrf())


@app.route('/api/session')
def api_session():
    return jsonify(is_admin=bool(session.get('is_admin')))


@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def api_login():
    data = request.get_json(silent=True) or {}
    username = clean_text(data.get('username', ''), 80)
    password = data.get('password', '')
    if not isinstance(password, str):
        password = ''
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['is_admin'] = True
        logger.info(f"[LOGIN] Admin login successful: {username}")
        return jsonify(ok=True)
    logger.warning(f"[LOGIN_FAILED] Invalid credentials for username: {username}")
    return jsonify(ok=False, error="Invalid username or password"), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('is_admin', None)
    return jsonify(ok=True)


@app.route('/api/admin/dashboard')
@admin_required
def api_admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    consumers = [row_to_dict(r) for r in cursor.execute("SELECT * FROM consumers ORDER BY id DESC").fetchall()]
    bills = [row_to_dict(r) for r in cursor.execute("""
        SELECT bills.id, consumers.name, consumers.meter_no, bills.month, bills.units, bills.amount, bills.status
        FROM bills JOIN consumers ON bills.consumer_id = consumers.id
        ORDER BY bills.id DESC
    """).fetchall()]
    complaints = [row_to_dict(r) for r in cursor.execute("""
        SELECT complaints.id, consumers.name, complaints.category, complaints.description, complaints.status
        FROM complaints JOIN consumers ON complaints.consumer_id = consumers.id
        ORDER BY complaints.id DESC
    """).fetchall()]
    conn.close()
    active_tab = get_setting('admin_active_tab', 'tab-add')
    if active_tab not in ('tab-add', 'tab-bill', 'tab-data'):
        active_tab = 'tab-add'
    return jsonify(consumers=consumers, bills=bills, complaints=complaints, active_tab=active_tab)


@app.route('/api/admin/tab', methods=['POST'])
@admin_required
def api_admin_tab():
    data = request.get_json(silent=True) or {}
    tab_id = data.get('tab_id', '')
    if tab_id in ('tab-add', 'tab-bill', 'tab-data'):
        set_setting('admin_active_tab', tab_id)
    return jsonify(ok=True)


@app.route('/api/admin/consumers', methods=['POST'])
@admin_required
@limiter.limit("20 per minute")
def api_add_consumer():
    data = request.get_json(silent=True) or {}
    name = clean_text(data.get('name', ''), 120)
    meter_no = clean_text(data.get('meter_no', ''), 32)
    address = clean_text(data.get('address', ''), 200)

    if not (name and meter_no and address) or not METER_RE.match(meter_no):
        return jsonify(error="Invalid consumer details"), 400

    conn = get_db()
    try:
        conn.execute("INSERT INTO consumers (name, meter_no, address) VALUES (?, ?, ?)", (name, meter_no, address))
        conn.commit()
        logger.info(f"[ADMIN] New consumer added: {meter_no}")
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify(error="Meter number already exists"), 409
    conn.close()
    return jsonify(ok=True)


@app.route('/api/admin/bills', methods=['POST'])
@admin_required
@limiter.limit("20 per minute")
def api_generate_bill():
    data = request.get_json(silent=True) or {}
    month = clean_text(data.get('month', ''), 7)

    try:
        consumer_id = int(data.get('consumer_id'))
        units = max(0, int(data.get('units')))
    except (TypeError, ValueError):
        return jsonify(error="Invalid bill data"), 400

    if not MONTH_RE.match(month):
        return jsonify(error="Invalid month"), 400

    conn = get_db()
    exists = conn.execute("SELECT id FROM consumers WHERE id = ?", (consumer_id,)).fetchone()
    if not exists:
        conn.close()
        return jsonify(error="Consumer not found"), 404

    total_amount = round(units * UNIT_RATE, 2)
    conn.execute("INSERT INTO bills (consumer_id, month, units, amount, status) VALUES (?, ?, ?, ?, 'Unpaid')",
                 (consumer_id, month, units, total_amount))
    conn.commit()
    conn.close()
    logger.info(f"[ADMIN] Bill generated for consumer {consumer_id}: {month} - {units} units - Rs {total_amount}")
    return jsonify(ok=True)


@app.route('/api/admin/complaints/<int:complaint_id>/status', methods=['POST'])
@admin_required
def api_update_complaint(complaint_id):
    data = request.get_json(silent=True) or {}
    new_status = data.get('status', '')
    if new_status not in STATUS_WHITELIST:
        return jsonify(error="Invalid status"), 400
    conn = get_db()
    conn.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
    conn.commit()
    conn.close()
    return jsonify(ok=True)


@app.route('/api/consumer/search', methods=['POST'])
@limiter.limit("20 per minute")
def api_consumer_search():
    data = request.get_json(silent=True) or {}
    meter_no = clean_text(data.get('meter_no', ''), 32)

    conn = get_db()
    cursor = conn.cursor()
    consumer_row = cursor.execute(
        "SELECT * FROM consumers WHERE UPPER(TRIM(meter_no)) = UPPER(?)", (meter_no,)
    ).fetchone()

    bills = []
    if consumer_row:
        bills = [row_to_dict(r) for r in cursor.execute(
            "SELECT * FROM bills WHERE consumer_id = ? ORDER BY id DESC", (consumer_row['id'],)
        ).fetchall()]
    conn.close()

    return jsonify(consumer=row_to_dict(consumer_row), bills=bills, meter_no=meter_no)


@app.route('/api/consumer/pay/<int:bill_id>', methods=['POST'])
@limiter.limit("20 per minute")
def api_pay_bill(bill_id):
    conn = get_db()
    conn.execute("UPDATE bills SET status = 'Paid' WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()
    return jsonify(ok=True)


@app.route('/api/complaints', methods=['POST'])
@limiter.limit("10 per minute")
def api_complaints():
    data = request.get_json(silent=True) or {}
    meter_no = clean_text(data.get('meter_no', ''), 32)
    category = data.get('category', '')
    description = clean_text(data.get('description', ''), 1000)

    if category not in CATEGORY_WHITELIST or not description or not meter_no:
        return jsonify(error="Invalid complaint details"), 400

    conn = get_db()
    cursor = conn.cursor()
    user = cursor.execute(
        "SELECT * FROM consumers WHERE UPPER(TRIM(meter_no)) = UPPER(?)", (meter_no,)
    ).fetchone()

    if user:
        cursor.execute(
            "INSERT INTO complaints (consumer_id, category, description, status) VALUES (?, ?, ?, 'Pending')",
            (user['id'], category, description)
        )
        conn.commit()
        message = "Complaint registered successfully! Our team will look into it."
        user_complaints = [row_to_dict(r) for r in cursor.execute(
            "SELECT * FROM complaints WHERE consumer_id = ? ORDER BY id DESC", (user['id'],)
        ).fetchall()]
    else:
        message = f"No consumer found with meter number '{meter_no}'."
        user_complaints = []
    conn.close()

    return jsonify(message=message, complaints=user_complaints, meter_no=meter_no)


# ---------- SPA ----------

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def spa(path):
    if path.startswith('api/'):
        abort(404)
    full = os.path.join(DIST_DIR, path)
    if path and os.path.isfile(full):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
