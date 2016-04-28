import logging

_logger = None

def get_logger():
    global _logger
    if _logger is not None:
        return _logger
    log_format = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    _logger = logging.getLogger("score_cli_logger   ")
    _logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    
    return _logger

