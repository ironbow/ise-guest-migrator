api_paths = {}
api_paths


class Path:
    def __init__(self, name: str, type: str, target: str, headers: object):
        self.name = name
        self.type = type
        self.target = target
        self.headers = {"ERS-Media-Type": "identity.guestuser.2.0"}

        path = {}
        path[self.name] = {
            "name": self.name,
            "type": self.type,
            "target": self.target,
            "headers": self.headers,
        }
        return path
