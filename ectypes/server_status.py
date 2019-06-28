class InvalidServerStatus(Exception):
    pass


class ServerStatus():
    INIT = "init"
    NORMAL = 'normal'
    FAILED = 'failed'
    DELETING = 'deleting'
    DELETED = 'deleted'

    @classmethod
    def def_status(cls):
        return cls.INIT,

    @classmethod
    def all_status(cls):
        return [
            cls.INIT,
            cls.NORMAL,
            cls.FAILED,
            cls.DELETING,
            cls.DELETED,
        ]
