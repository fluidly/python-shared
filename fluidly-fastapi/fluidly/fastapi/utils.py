import base64


def base64_decode(encoded_str: bytes) -> str:
    """To make the string decodable you have to make the number of characters in the
    encoded string an integer multiple of 4. Meaning you have to divide the number of
    characters by 4 and not get a remainder.

    https://en.wikipedia.org/wiki/Base64#Output_padding
    """

    num_missed_paddings = 4 - len(encoded_str) % 4
    if num_missed_paddings != 4:
        encoded_str += b"=" * num_missed_paddings
    return base64.b64decode(encoded_str).decode("utf-8")
