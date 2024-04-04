import logging

from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)


class ExcpetionHandler:
    def handle_http_excpetion(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPError as e:
                logger.error(f"HTTPError: {e}")

        return wrapper




