
class IDBase(object):

    _tostr_fmt = '{item_1}-{item_2:0>3}'

    def __str__(self):
        return self._tostr_fmt.format(**{k: str(v) for k, v in self._asdict().items()})

    def tostr(self):
        return str(self)
