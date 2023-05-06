# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

from .__version__ import __author__, __copyright__, __title__, __version__
from .core import (FeedType, Note, NoteType, SearchNoteType, SearchSortType,
                   XhsClient)
from .exception import DataFetchError, IPBlockError

logging.getLogger(__name__).addHandler(NullHandler())
