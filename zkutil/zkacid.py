import logging

from kazoo.client import KazooClient
from kazoo.exceptions import BadVersionError

from pykit import utfjson

from .zkconf import ZKConf

logger = logging.getLogger(__name__)


def cas_loop(zkclient, path, json=True):

    zkconf = None
    if isinstance(zkclient, str):
        zkconf = ZKConf(hosts=zkclient)

    if isinstance(zkclient, dict):
        zkconf = ZKConf(**zkclient)

    if isinstance(zkclient, ZKConf):
        zkconf = zkclient

    owning_zk = False

    if zkconf is not None:
        zkclient = KazooClient(zkconf.hosts())
        zkclient.start()
        owning_zk = True
        auth = zkconf.kazoo_auth()
        if auth is not None:
            zkclient.add_auth(*auth)

    sess = {}

    def _update(val):
        sess['val'] = val

    try:
        while True:

            val, zstat = zkclient.get(path)
            if json:
                val = utfjson.load(val)

            if 'val' in sess:
                del sess['val']

            yield val, _update

            if 'val' not in sess:
                # user does not call set_val(), nothing to set to zk
                return

            if json:
                sess['val'] = utfjson.dump(sess['val'])

            try:
                zkclient.set(path, sess['val'],
                             version=zstat.version)

            except BadVersionError as e:
                logger.info(repr(e) + ' concurrent updated to ' + repr(path))
            else:
                return
    finally:
        if owning_zk:
            try:
                zkclient.stop()
            except Exception as e:
                logger.info(repr(e) + ' while stop owning zkclient')
