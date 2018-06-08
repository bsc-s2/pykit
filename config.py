
import logging
import uuid

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
iostat_stat_path     = _get('iostat_stat_path', '/tmp/pykit-iostat')
zk_acl               = _get('zk_acl')                   # (('xp', '123', 'cdrwa'), ('foo', 'bar', 'rw'))
zk_auth              = _get('zk_auth')                  # ('digest', 'xp', '123')
zk_hosts             = _get('zk_hosts', '127.0.0.1:2181')
zk_lock_dir          = _get('zk_lock_dir', 'lock/')
zk_node_id           = _get('zk_node_id', '%012x' % uuid.getnode())
zk_record_dir        = _get('zk_record_dir', 'record/')
zk_tx_dir            = _get('zk_tx_dir', 'tx/')
zk_seq_dir           = _get('zk_seq_dir', 'seq/')
rp_cli_nwr           = _get('rp_cli_nwr', (3, 2, 2))
rp_cli_ak_sk         = _get('rp_cli_ak_sk', ('access_key', 'secret_key'))
