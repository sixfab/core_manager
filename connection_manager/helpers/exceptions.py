
class ModemNotFound(Exception):
    """Raise when the modem couldn't be detected"""

class ModemNotSupported(Exception):
    """Raise when the modem isn't supported"""

class ModemNotReachable(Exception):
    """Raise when an error occured on serial communication with modem"""


