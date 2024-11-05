class Proxy:

    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def to_json(self):
        proxy = {
            "user": self.user,
            "pass": self.password,
            "host": self.host,
            "port": str(self.port),
        }
        return None  # TODO: temporary solution
