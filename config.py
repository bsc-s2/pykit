
import logging

logger = logging.getLogger(__name__)

# try to load config from a top-level module.
try:
    import pykitconfig
except ImportError:
    pykitconfig = object()
    logger.info('pykitconfig not found by "import pykitconfig".'
                ' Using default config.'
                ' You can create file "pykitconf.py" to define default config for pykit.')


def _get(key, default=None):
    v = getattr(pykitconfig, key, default)

    logger.debug('set pykit config: {key}={v}'.format(key=key, v=v))
    return v


uid                  = _get('uid')
gid                  = _get('gid')
log_dir              = _get('log_dir')

cat_stat_dir         = _get('cat_stat_dir')
