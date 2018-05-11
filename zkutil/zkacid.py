import logging

from kazoo.exceptions import BadVersionError

from .zkconf import kazoo_client_ext

logger = logging.getLogger(__name__)


def cas_loop(zkclient, path, json=True):

    zkclient, owning_zk = kazoo_client_ext(zkclient, json=json)

    sess = {}

    def _update(val):
        sess['val'] = val

    try:
        while True:

            val, zstat = zkclient.get(path)

            if 'val' in sess:
                del sess['val']

            yield val, _update

            if 'val' not in sess:
                # user does not call set_val(), nothing to set to zk
                return

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
