import logging

from kazoo.exceptions import BadVersionError

from pykit import txutil

from .zkconf import kazoo_client_ext

logger = logging.getLogger(__name__)


def cas_loop(zkclient, path, json=True):

    zkclient, owning_zk = kazoo_client_ext(zkclient, json=json)

    def setter(path, val, zstat):
        try:
            zkclient.set(path, val, version=zstat.version)
            return True

        except BadVersionError as e:
            logger.info(repr(e) + ' concurrent updated to ' + repr(path))
            return False

    try:
        for curr in txutil.cas_loop(zkclient.get, setter, path):
            yield curr
    finally:
        if owning_zk:
            try:
                zkclient.stop()
            except Exception as e:
                logger.info(repr(e) + ' while stop owning zkclient')
