from .. import config
from . import notify, sitegen, outreach, whatsapp, meta
if config.IS_TERMUX:
    from . import android
else:
    try:
        from . import pc
    except Exception:
        pass
