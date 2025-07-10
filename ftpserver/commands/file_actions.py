from ftpserver.utils.filesystem import resolve_path

class RetrCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename\r\n"
        try:
            file_path = resolve_path(session.cwd, args[0])
            with open(file_path, 'rb') as f:
                conn = session.data_channel.open()
                session.data_channel.close()
                data = f.read()
                conn.sendall(data)
                conn.close()
            return "226 File transfer complete\r\n"
        except Exception as e:
            return f"550 Failed to retrieve file: {e}\r\n"

import os
import shutil
import stat
import time
from ftpserver.utils.filesystem import resolve_path

class StorCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename\r\n"
        try:
            file_path = resolve_path(session.cwd, args[0])
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            conn = session.data_channel.open()
            session.data_channel.close()
            with open(file_path, 'wb') as f:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    f.write(data)
            conn.close()
            return "226 File upload complete\r\n"
        except Exception as e:
            return f"550 Failed to store file: {e}\r\n"
        
class CatCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename\r\n"
        try:
            file_path = resolve_path(session.cwd, args[0])
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read(4096)  # Limit to 4KB for safety
            # If file is longer, indicate truncation
            if len(data) == 4096:
                data += "\n... (truncated)\n"
            # FTP lines end with \r\n
            return f"150 Opening file\r\n{data}\r\n226 File display complete\r\n"
        except Exception as e:
            return f"550 Failed to display file: {e}\r\n"

class RmCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename\r\n"
        try:
            file_path = resolve_path(session.cwd, args[0])
            os.remove(file_path)
            return "250 File deleted\r\n"
        except FileNotFoundError:
            return "550 File not found\r\n"
        except IsADirectoryError:
            return "550 Path is a directory, use RMD or RM -R\r\n"
        except Exception as e:
            return f"550 Failed to delete file: {e}\r\n"

class CpCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if len(args) < 2:
            return "501 Missing source or destination\r\n"
        try:
            src = resolve_path(session.cwd, args[0])
            dst = resolve_path(session.cwd, args[1])
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return "250 Copy successful\r\n"
        except Exception as e:
            return f"550 Failed to copy: {e}\r\n"

class MvCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if len(args) < 2:
            return "501 Missing source or destination\r\n"
        try:
            src = resolve_path(session.cwd, args[0])
            dst = resolve_path(session.cwd, args[1])
            os.rename(src, dst)
            return "250 Move successful\r\n"
        except Exception as e:
            return f"550 Failed to move: {e}\r\n"

class StatCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename or directory\r\n"
        try:
            path = resolve_path(session.cwd, args[0])
            st = os.stat(path)
            perms = stat.filemode(st.st_mode)
            nlink = st.st_nlink
            owner = st.st_uid if hasattr(st, 'st_uid') else 0
            group = st.st_gid if hasattr(st, 'st_gid') else 0
            size = st.st_size
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))
            info = f"Path: {args[0]}\r\nType: {'Directory' if os.path.isdir(path) else 'File'}\r\nPermissions: {perms}\r\nLinks: {nlink}\r\nOwner: {owner}\r\nGroup: {group}\r\nSize: {size} bytes\r\nModified: {mtime}\r\n"
            return f"213-STAT info follows\r\n{info}213 End of STAT info\r\n"
        except Exception as e:
            return f"550 Failed to stat: {e}\r\n"

class TouchCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename\r\n"
        try:
            file_path = resolve_path(session.cwd, args[0])
            with open(file_path, 'a'):
                os.utime(file_path, None)
            return "250 File touched\r\n"
        except Exception as e:
            return f"550 Failed to touch file: {e}\r\n"

class EchoCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing arguments\r\n"
        # Support echo "hello" > a.txt
        if '>' in args:
            idx = args.index('>')
            content = ' '.join(args[:idx])
            filename = args[idx+1] if len(args) > idx+1 else None
            if not filename:
                return "501 Missing filename after >\r\n"
            try:
                file_path = resolve_path(session.cwd, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content.strip('"'))
                return "250 Echoed to file\r\n"
            except Exception as e:
                return f"550 Failed to echo to file: {e}\r\n"
        else:
            # Just echo to output
            content = ' '.join(args)
            return f"200 {content.strip('')}\r\n"