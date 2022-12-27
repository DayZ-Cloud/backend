import base64

from rcon.battleye import Client
from rcon.battleye.proto import CommandRequest


def encryptor(password: str):
    password = password.encode("UTF-8")
    return base64.b64encode(password)


def decryptor(password):
    return base64.b64decode(str(password))


class customRequest(CommandRequest):
    @property
    def payload(self) -> bytes:
        """Return the payload."""
        return b''.join((
            self.seq.to_bytes(1, 'little'),
            self.command.encode()
        ))


class customClient(Client):
    def run(self, command: str, *args: str) -> str:
        """Execute a command and return the text message."""
        return self.communicate(
            customRequest.from_command(command, *args)
        ).message