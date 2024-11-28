class Proxy:

    def __init__(self, user, password, host, port):
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def to_json(self):
        proxy = {}
        if self.user:
            proxy["user"] = self.user
        if self.password:
            proxy["pass"] = self.password
        if self.host:
            proxy["host"] = self.host
        if self.port:
            proxy["port"] = str(self.port)
        return proxy
