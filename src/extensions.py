"""Flask add-ons that get created here, not inside app.py.

Why: both app.py and the route files under src/api/ need to use the same
`limiter` object. If it were created inside app.py, importing it into a
route file would try to import app.py, which imports the route file...
and Python gets stuck in a circle. Creating it in its own file with no
other project imports breaks that circle.
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Counts requests per visitor (by IP address) so a route can say "only
# 5 tries per minute from the same visitor". In development this count is
# just kept in memory. For production with more than one server process,
# set RATELIMIT_STORAGE_URL in .env (e.g. to Redis) so every process shares
# the same count, see app.py for where that setting is read.
limiter = Limiter(key_func=get_remote_address)
