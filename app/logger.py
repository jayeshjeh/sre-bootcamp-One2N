import logging
import os

def setup_logging(app):
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    
    if "gunicorn" in os.getenv("SERVER_SOFTWARE", "").lower():
        logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = logger.handlers
        app.logger.setLevel(level)
    else:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s")
        handler.setFormatter(fmt)
        app.logger.handlers = [handler]
        app.logger.setLevel(level)
