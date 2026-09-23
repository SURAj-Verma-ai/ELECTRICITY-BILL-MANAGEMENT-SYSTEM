import os
import sqlite3
import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DB_NAME = "ebill.db"
UNIT_RATE = 7.0
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

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
        logger.debug(f"[DB] Connected to {DB_NAME}")
        return conn
    except Exception as e:
        logger.error(f"[DB_ERROR] Failed to connect to {DB_NAME}: {str(e)}")
        raise

def init_db():
    try:
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
            logger.info("[DB] Database initialized successfully")
    except Exception as e:
        logger.error(f"[DB_ERROR] Failed to initialize database: {str(e)}")
        raise

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

@app.route('/')
def home():
    try:
        logger.info("[HOME] Rendering home page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"[HOME_ERROR] Failed to render home page: {str(e)}")
        return f"Error loading home page: {str(e)}", 500

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            logger.warning(f"[AUTH] Blocked unauthenticated access to {request.path}")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session.get('is_admin'):
            return redirect(url_for('admin'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['is_admin'] = True
                logger.info(f"[LOGIN] Admin login successful: {username}")
                return redirect(url_for('admin'))
            else:
                logger.warning(f"[LOGIN_FAILED] Invalid credentials for username: {username}")
                return render_template('login.html', error="Invalid username or password")

        logger.info("[LOGIN] Login page accessed")
        return render_template('login.html')
    except Exception as e:
        logger.error(f"[LOGIN_ERROR] Failed to process login: {str(e)}")
        return f"Error loading login page: {str(e)}", 500

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    logger.info("[LOGOUT] Admin logged out")
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    try:
        logger.info("[ADMIN] Admin page accessed")
        conn = get_db()
        cursor = conn.cursor()

        if request.method == 'POST':
            if 'add_consumer' in request.form:
                name = request.form.get('name', '').strip()
                meter_no = request.form.get('meter_no', '').strip()
                address = request.form.get('address', '').strip()

                if name and meter_no and address:
                    try:
                        cursor.execute("INSERT INTO consumers (name, meter_no, address) VALUES (?, ?, ?)",
                                       (name, meter_no, address))
                        conn.commit()
                        logger.info(f"[ADMIN] New consumer added: {meter_no}")
                    except sqlite3.IntegrityError as e:
                        logger.warning(f"[ADMIN_ERROR] Duplicate meter number: {meter_no}")

            if 'generate_bill' in request.form:
                consumer_id_raw = request.form.get('consumer_id')
                month = request.form.get('month', '').strip()
                units_raw = request.form.get('units')

                if consumer_id_raw and month and units_raw is not None:
                    try:
                        consumer_id = int(consumer_id_raw)
                        units = max(0, int(units_raw))
                        total_amount = round(units * UNIT_RATE, 2)
                        cursor.execute("INSERT INTO bills (consumer_id, month, units, amount, status) VALUES (?, ?, ?, ?, 'Unpaid')",
                                       (consumer_id, month, units, total_amount))
                        conn.commit()
                        logger.info(f"[ADMIN] Bill generated for consumer {consumer_id}: {month} - {units} units - Rs {total_amount}")
                    except (ValueError, TypeError) as e:
                        logger.error(f"[ADMIN_ERROR] Invalid bill data: {str(e)}")

        consumers = cursor.execute("SELECT * FROM consumers ORDER BY id DESC").fetchall()
        bills = cursor.execute("""
            SELECT bills.id, consumers.name, consumers.meter_no, bills.month, bills.units, bills.amount, bills.status
            FROM bills
            JOIN consumers ON bills.consumer_id = consumers.id
            ORDER BY bills.id DESC
        """).fetchall()
        complaints = cursor.execute("""
            SELECT complaints.id, consumers.name, complaints.category, complaints.description, complaints.status
            FROM complaints
            JOIN consumers ON complaints.consumer_id = consumers.id
            ORDER BY complaints.id DESC
        """).fetchall()

        conn.close()

        active_tab = get_setting('admin_active_tab', 'tab-add')
        if active_tab not in ('tab-add', 'tab-bill', 'tab-data'):
            active_tab = 'tab-add'

        logger.debug(f"[ADMIN] Loaded {len(consumers)} consumers, {len(bills)} bills, {len(complaints)} complaints")
        return render_template('admin.html', consumers=consumers, bills=bills, complaints=complaints, active_tab=active_tab)
    except Exception as e:
        logger.error(f"[ADMIN_ERROR] {str(e)}")
        return f"Error loading admin page: {str(e)}", 500

@app.route('/admin/set_tab/<string:tab_id>', methods=['POST'])
@admin_required
def admin_set_tab(tab_id):
    if tab_id in ('tab-add', 'tab-bill', 'tab-data'):
        set_setting('admin_active_tab', tab_id)
    return '', 204

@app.route('/update_complaint/<int:complaint_id>/<string:new_status>')
@admin_required
def update_complaint(complaint_id, new_status):
    valid_statuses = ['Pending', 'In Progress', 'Resolved']
    if new_status in valid_statuses:
        conn = get_db()
        conn.execute("UPDATE complaints SET status = ? WHERE id = ?", (new_status, complaint_id))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/consumer', methods=['GET', 'POST'])
def consumer():
    consumer_data = None
    bills = []
    searched = False
    meter_no = ""

    if request.method == 'POST':
        searched = True
        meter_no = request.form.get('meter_no', '').strip()

        conn = get_db()
        cursor = conn.cursor()
        consumer_data = cursor.execute(
            "SELECT * FROM consumers WHERE UPPER(TRIM(meter_no)) = UPPER(?)", 
            (meter_no,)
        ).fetchone()

        if consumer_data:
            bills = cursor.execute(
                "SELECT * FROM bills WHERE consumer_id = ? ORDER BY id DESC", 
                (consumer_data['id'],)
            ).fetchall()

        conn.close()

    return render_template('consumer.html', consumer=consumer_data, bills=bills, searched=searched, meter_no=meter_no)

@app.route('/pay_bill/<int:bill_id>')
def pay_bill(bill_id):
    conn = get_db()
    conn.execute("UPDATE bills SET status = 'Paid' WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('consumer'))

@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    user_complaints = []
    message = None
    meter_no = ""

    if request.method == 'POST':
        meter_no = request.form.get('meter_no', '').strip()
        category = request.form.get('category')
        description = request.form.get('description', '').strip()

        conn = get_db()
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM consumers WHERE UPPER(TRIM(meter_no)) = UPPER(?)", 
            (meter_no,)
        ).fetchone()

        if user:
            cursor.execute(
                "INSERT INTO complaints (consumer_id, category, description, status) VALUES (?, ?, ?, 'Pending')",
                (user['id'], category, description)
            )
            conn.commit()
            message = "Complaint registered successfully! Our team will look into it."

            user_complaints = cursor.execute(
                "SELECT * FROM complaints WHERE consumer_id = ? ORDER BY id DESC", 
                (user['id'],)
            ).fetchall()
        else:
            message = f"No consumer found with meter number '{meter_no}'."

        conn.close()

    return render_template('complaints.html', complaints=user_complaints, message=message, meter_no=meter_no)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)