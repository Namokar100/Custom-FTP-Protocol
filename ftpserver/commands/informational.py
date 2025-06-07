class NoopCommand:
    def handle(self, args, session):
        return "200 NOOP ok\r\n"
