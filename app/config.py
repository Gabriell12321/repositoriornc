import os


class Config:
    # Secret key: try to load from file, fallback to env, then default
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        try:
            with open('ippel_secret.key', 'r', encoding='utf-8') as f:
                SECRET_KEY = f.read().strip()
        except Exception:
            SECRET_KEY = 'dev-secret-key'

    # General app settings
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB uploads
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # set True behind HTTPS
    TEMPLATES_AUTO_RELOAD = True

    # Optional: rate limit defaults used by services.rate_limit if present
    RATE_LIMIT_DEFAULTS = os.getenv('RATE_LIMIT_DEFAULTS', '200 per minute')
