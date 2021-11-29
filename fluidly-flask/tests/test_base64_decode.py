import base64
import json

from fluidly.flask.utils import base64_decode


def test_decode_bytestring():
    obj = {"foo": "bar"}
    payload = base64.b64encode(json.dumps(obj).encode("utf-8"))

    assert json.loads(base64_decode(payload)) == obj


def test_decode_string():
    obj = {"foo": "bar"}
    payload = base64.b64encode(json.dumps(obj).encode("utf-8")).decode("utf-8")

    assert json.loads(base64_decode(payload)) == obj
