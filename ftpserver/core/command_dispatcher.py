from ftpserver.commands import access_control, informational, directory_ops, transfer_modes, file_actions

class CommandDispatcher:
    def __init__(self, session):
        self.session = session
        self.commands = {
            "USER": access_control.UserCommand(),
            "PASS": access_control.PassCommand(),
            "QUIT": access_control.QuitCommand(),
            "NOOP": informational.NoopCommand(),
            "PWD": directory_ops.PwdCommand(),
            "CD": directory_ops.CwdCommand(),
            "LS": directory_ops.ListCommand(),
            "NLST": directory_ops.NlstCommand(),
            "PORT": transfer_modes.PortCommand(),
            "PASV": transfer_modes.PasvCommand(),
            "RETR": file_actions.RetrCommand(),
            "STOR": file_actions.StorCommand(),
            "CAT": file_actions.CatCommand(),
            "MKDIR": directory_ops.MkdirCommand(),
            "RMDIR": directory_ops.RmdirCommand(),
            "RM": file_actions.RmCommand(),
            "RM-R": directory_ops.RmRecursiveCommand(),
            "CP": file_actions.CpCommand(),
            "MV": file_actions.MvCommand(),
            "LS-L": directory_ops.LsLongCommand(),
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
