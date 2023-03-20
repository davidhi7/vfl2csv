import logging

logger = logging.getLogger(__name__)


class TextMap(dict):
    # Only invoked if the key is not found. In this case, return the key.
    def __getattr__(self, item: str):
        logger.warning(f'Missing text value for key {item}')
        return item

    def get_replace(self, key: str, replacement: any):
        return self[key].replace('{}', str(replacement))
