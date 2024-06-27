import logging

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="logs/error.log",
)
logger = logging.getLogger(__name__)
