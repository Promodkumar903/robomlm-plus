# app/ui/discovery/__init__.py

from .discovery_page import *
from .universal_scanner import *
from .scanners.stock_scanner import *
from .scanners.equity_scanner import *
from .scanners.index_scanner import *
from .scanners.commodity_scanner import *
from .scanners.crypto_scanner import *
from .scanners.fx_scanner import *
from .favorites import *


from .discovery_page import __all__ as _discovery_all
from .universal_scanner import __all__ as _universal_all
from .scanners.stock_scanner import __all__ as _stock_all
from .scanners.equity_scanner import __all__ as _equity_all
from .scanners.index_scanner import __all__ as _index_all
from .scanners.commodity_scanner import __all__ as _commodity_all
from .scanners.crypto_scanner import __all__ as _crypto_all
from .scanners.fx_scanner import __all__ as _fx_all
from .favorites import __all__ as _favorites_all


__all__ = [
    *_discovery_all,
    *_universal_all,
    *_stock_all,
    *_equity_all,
    *_index_all,
    *_commodity_all,
    *_crypto_all,
    *_fx_all,
    *_favorites_all,
]


del _discovery_all
del _universal_all
del _stock_all
del _equity_all
del _index_all
del _commodity_all
del _crypto_all
del _fx_all
del _favorites_all