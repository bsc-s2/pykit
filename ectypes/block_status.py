class BlockStatus():
    NORMAL = 'normal'
    BROKEN = 'broken'
    NOTFOUND = 'notFound'
    MIGRATING = 'migrating'
    RECOVING = 'recoving'

    @classmethod
    def def_status(cls):
        return cls.NORMAL

    @classmethod
    def all_status(cls):
        return [
            cls.NORMAL,
            cls.BROKEN,
            cls.NOTFOUND,
            cls.MIGRATING,
            cls.RECOVING,
        ]
