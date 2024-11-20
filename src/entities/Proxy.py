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
        if self.user == None or self.password == None or self.host == None or self.port == None:
            proxy = None
        return proxy  # TODO: temporary solution
