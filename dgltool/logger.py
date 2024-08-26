import logging

logger = logging.getLogger('dgltool')
logger.addHandler(logging.StreamHandler())

debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical


def configure(verbosity=0):
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    logger.setLevel(level)
