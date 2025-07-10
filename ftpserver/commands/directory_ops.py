import os
import shutil
from ftpserver.utils.filesystem import resolve_path, list_dir, change_directory

class PwdCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        return f'257 "{session.cwd}" is the current directory\r\n'

class CwdCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
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
        if not session.logged_in:
            return "530 Not logged in\r\n"
        try:
            path = resolve_path(session.cwd, args[0] if args else ".")
            files = list_dir(path)
            data = "\r\n".join(files) + "\r\n"
            return f"150 Here comes the directory listing\r\n{data}226 Directory send OK\r\n"
        except Exception:
            return "550 Failed to list directory\r\n"

class NlstCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        try:
            path = resolve_path(session.cwd, args[0] if args else ".")
            files = list_dir(path)
            data = "\r\n".join(f for f in files if not f.startswith('.')) + "\r\n"
            return f"150 Here comes the name list\r\n{data}226 Transfer complete\r\n"
        except Exception:
            return "550 Failed to list directory\r\n"

class MkdirCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing directory name\r\n"
        try:
            dir_path = resolve_path(session.cwd, args[0])
            os.makedirs(dir_path, exist_ok=False)
            return f'257 "{args[0]}" directory created\r\n'
        except FileExistsError:
            return "550 Directory already exists\r\n"
        except Exception as e:
            return f"550 Failed to create directory: {e}\r\n"

class RmdirCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing directory name\r\n"
        try:
            dir_path = resolve_path(session.cwd, args[0])
            os.rmdir(dir_path)
            return "250 Directory removed\r\n"
        except FileNotFoundError:
            return "550 Directory not found\r\n"
        except OSError:
            return "550 Directory not empty or cannot be removed\r\n"
        except Exception as e:
            return f"550 Failed to remove directory: {e}\r\n"

class RmRecursiveCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing directory name\r\n"
        try:
            dir_path = resolve_path(session.cwd, args[0])
            shutil.rmtree(dir_path)
            return "250 Directory and contents removed\r\n"
        except FileNotFoundError:
            return "550 Directory not found\r\n"
        except Exception as e:
            return f"550 Failed to remove directory recursively: {e}\r\n"

class LsLongCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        import stat, time
        try:
            path = resolve_path(session.cwd, args[0] if args else ".")
            files = os.listdir(path)
            lines = []
            for f in files:
                fp = os.path.join(path, f)
                st = os.stat(fp)
                perms = stat.filemode(st.st_mode)
                nlink = st.st_nlink
                owner = st.st_uid if hasattr(st, 'st_uid') else 0
                group = st.st_gid if hasattr(st, 'st_gid') else 0
                size = st.st_size
                mtime = time.strftime('%b %d %H:%M', time.localtime(st.st_mtime))
                lines.append(f"{perms} {nlink} {owner} {group} {size} {mtime} {f}")
            data = "\r\n".join(lines) + "\r\n"
            return f"150 Here comes the directory listing\r\n{data}226 Directory send OK\r\n"
        except Exception as e:
            return f"550 Failed to list directory: {e}\r\n"
