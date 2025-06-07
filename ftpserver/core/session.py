class FTPSession:
    def __init__(self):
        self.username = None
        self.logged_in = False
        self.cwd = "/"  # Start in root
        self.transfer_type = "A"  # ASCII mode by default
