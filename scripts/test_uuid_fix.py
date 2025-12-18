import uuid


def generate_id():
    return uuid.uuid4()


def generate_hex():
    return uuid.uuid4().hex
