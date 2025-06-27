from . import models

def test_hook(cr, registry):
    import logging
    _logger = logging.getLogger(__name__)
    _logger.warning("✅ post_init_hook çalıştı — modül aktif!")
