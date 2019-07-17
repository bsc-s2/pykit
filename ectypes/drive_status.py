class InvalidDriveStatus(Exception):
    pass


class DriveStatus():
    NORMAL = 'normal'
    READONLY = 'readonly'
    FAILED = 'failed'
    DELETING = 'deleting'
    DELETED = 'deleted'

    @classmethod
    def def_status(cls):
        return cls.READONLY

    @classmethod
    def all_status(cls):
        return [
            cls.NORMAL,
            cls.READONLY,
            cls.FAILED,
            cls.DELETING,
            cls.DELETED,
        ]
