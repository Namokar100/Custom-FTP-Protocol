from ftpserver.commands import access_control, informational

class CommandDispatcher:
    def __init__(self, session):
        self.session = session
        self.commands = {
            "USER": access_control.UserCommand(),
            "PASS": access_control.PassCommand(),
            "QUIT": access_control.QuitCommand(),
            "NOOP": informational.NoopCommand(),
        }

    def dispatch(self, command_line):
        if not command_line.strip():
            return "500 Empty command\r\n"

        parts = command_line.strip().split()
        cmd = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else []

        handler = self.commands.get(cmd)
        if handler:
            return handler.handle(args, self.session)
        else:
            return "502 Command not implemented\r\n"
