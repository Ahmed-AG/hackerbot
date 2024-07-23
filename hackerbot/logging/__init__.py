import logging
import os

logger: logging.Logger = logging.getLogger("hackerbot")

logger.setLevel(os.getenv("HACKERBOT_LOG_LEVEL", "INFO"))

handler = logging.StreamHandler()
handler.setLevel(os.getenv("HACKERBOT_LOG_LEVEL", "INFO"))
formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)


logger.addHandler(handler)

def set_level(level: str | int) -> None:
    """
        Set the logging level
    """
    level = level.upper() if isinstance(level, str) else level
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
