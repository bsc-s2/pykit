class BlockStatus():
    NORMAL = 'normal'
    BROKENBLOCK = 'brokenBlock'
    BROKENCHECKSUM = 'brokenChecksum'
    BLOCKNOTFOUND = 'blockNotFound'
    CHECKSUMNOTFOUND = 'checksumNotFound'
    MIGRATE = 'migrate'
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
            cls.BROKENBLOCK,
            cls.BLOCKNOTFOUND,
            cls.BROKENCHECKSUM,
            cls.CHECKSUMNOTFOUND,
            cls.MIGRATE,
            cls.MIGRATING,
            cls.RECOVING,
        ]
