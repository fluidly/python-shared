from fluidly.structlog.base_logger import get_logger


def test_get_logger():
    logger = get_logger()
    assert logger is not None
    logger.info('test logger')
