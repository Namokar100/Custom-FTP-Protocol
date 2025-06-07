from ftpserver.utils.filesystem import resolve_path, list_dir, change_directory

class PwdCommand:
    def handle(self, args, session):
        return f'257 "{session.cwd}" is the current directory\r\n'

class CwdCommand:
    def handle(self, args, session):
        if not args:
            return "501 Missing directory path\r\n"
        try:
            session.cwd = change_directory(session.cwd, args[0])
            return "250 Directory successfully changed\r\n"
        except NotADirectoryError:
            return "550 Not a directory\r\n"
        except ValueError:
            return "550 Access denied\r\n"

class ListCommand:
    def handle(self, args, session):
        try:
            path = resolve_path(session.cwd, args[0] if args else ".")
            files = list_dir(path)
            data = "\r\n".join(files) + "\r\n"
            return f"150 Here comes the directory listing\r\n{data}226 Directory send OK\r\n"
        except Exception:
            return "550 Failed to list directory\r\n"

class NlstCommand:
    def handle(self, args, session):
        try:
            path = resolve_path(session.cwd, args[0] if args else ".")
            files = list_dir(path)
            data = "\r\n".join(f for f in files if not f.startswith('.')) + "\r\n"
            return f"150 Here comes the name list\r\n{data}226 Transfer complete\r\n"
        except Exception:
            return "550 Failed to list directory\r\n"
