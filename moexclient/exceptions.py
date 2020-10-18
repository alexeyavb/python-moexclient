class MoexError(Exception):
    pass


class MoexCommandError(MoexError):
    pass


class MoexValueError(MoexError):
    pass
