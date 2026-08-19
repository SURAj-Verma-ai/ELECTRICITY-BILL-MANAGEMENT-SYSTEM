# Logging Configuration for EBMS
import logging
import logging.config
import json
from pathlib import Path

# Create logs directory if it doesn't exist
Path('logs').mkdir(exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/error.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'access_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/access.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'loggers': {
        # Root logger
        '': {
            'level': 'INFO',
            'handlers': ['console', 'file', 'error_file']
        },
        # Application loggers
        'ebms': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'ebms.api': {
            'level': 'INFO',
            'handlers': ['access_file'],
            'propagate': False
        },
        'ebms.services': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        # Third-party loggers
        'sqlalchemy': {
            'level': 'WARNING',
            'handlers': ['file']
        },
        'celery': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        },
        'werkzeug': {
            'level': 'INFO',
            'handlers': ['access_file']
        }
    }
}


def setup_logging():
    """Configure logging for the application"""
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger('ebms')


# Initialize logger
logger = setup_logging()
