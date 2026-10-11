# squeeze/__init__.py

from . import squeeze
from .psq import main as cli
from .pusq import main as ucli

compress = squeeze.compress

uncompress = squeeze.uncompress