# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

from .core import add

logging.getLogger(__name__).addHandler(NullHandler())
