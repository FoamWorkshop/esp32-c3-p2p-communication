try:
    import ujson as json
except Exception:
    import json


def mac_bytes_to_str(mac_bytes):
    if mac_bytes is None:
        return None
    try:
        return ':'.join('{:02x}'.format(b) for b in mac_bytes)
    except Exception:
        return str(mac_bytes)


def mac_str_to_bytes(mac_str):
    if mac_str is None:
        return None
    parts = mac_str.split(':')
    return bytes(int(p, 16) for p in parts)


TYPE_HELLO = 'HELLO'
TYPE_ACCEPTED = 'ACCEPTED'


class Message:
    def __init__(self, type_, sender=None, payload=None):
        self.type = type_
        self.sender = sender
        self.payload = payload or {}

    def to_bytes(self):
        obj = {'type': self.type, 'sender': self.sender, 'payload': self.payload}
        return json.dumps(obj).encode('utf-8')

    @staticmethod
    def from_bytes(b):
        try:
            obj = json.loads(b.decode('utf-8'))
            return Message(obj.get('type'), obj.get('sender'), obj.get('payload'))
        except Exception:
            return None


class Hello(Message):
    def __init__(self, sender=None):
        super().__init__(TYPE_HELLO, sender, {})


class Accepted(Message):
    def __init__(self, sender=None, original_type=None):
        payload = {'original_type': original_type}
        super().__init__(TYPE_ACCEPTED, sender, payload)
