import logging
import os

# Resolve the backend directory (two levels up from this file: utils/ -> src/ -> backend/)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

class Logger:
    @staticmethod
    def get_logger():
        logger = logging.getLogger("AppLogger")
        if not logger.handlers:
            log_dir = os.path.join(BACKEND_DIR, "logs")
            os.makedirs(log_dir, exist_ok=True)
            handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger