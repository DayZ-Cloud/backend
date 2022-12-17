import base64


def encryptor(password: str):
    password = password.encode("UTF-8")
    return base64.b64encode(password)


def decryptor(password):
    return base64.b64decode(str(password))
