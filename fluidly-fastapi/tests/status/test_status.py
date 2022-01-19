from fluidly.fastapi.constants.status import StatusEnum


def test_import_status_enum():
    assert StatusEnum is not None
