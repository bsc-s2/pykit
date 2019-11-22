class InvalidServerStatus(Exception):
    pass


class ServerStatus():
    INIT = "init"
    NORMAL = 'normal'
    FAILED = 'failed'
    DELETING = 'deleting'
    DELETED = 'deleted'
    ARCHIVE_ONLINE = 'archive_online'
    ARCHIVE_OFFLINE = 'archive_offline'

    @classmethod
    def def_status(cls):
        return cls.INIT

    @classmethod
    def all_status(cls):
        return [
            cls.INIT,
            cls.NORMAL,
            cls.FAILED,
            cls.DELETING,
            cls.DELETED,
            cls.ARCHIVE_ONLINE,
            cls.ARCHIVE_OFFLINE,
        ]
