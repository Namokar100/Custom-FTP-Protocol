from ftpserver.utils.filesystem import resolve_path

class RetrCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "retr: missing file operand"
        try:
            file_path = resolve_path(session.cwd, args[0])
            with open(file_path, 'rb') as f:
                conn = session.data_channel.open()
                session.data_channel.close()
                data = f.read()
                conn.sendall(data)
                conn.close()
            return "file sent"
        except Exception as e:
            return f"retr: {e}"

import os
import shutil
import stat
import time
from ftpserver.utils.filesystem import resolve_path

class StorCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "stor: missing file operand"
        try:
            file_path = resolve_path(session.cwd, args[0])
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
            return "file stored"
        except Exception as e:
            return f"stor: {e}"
        
class CatCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "cat: missing file operand"
        try:
            file_path = resolve_path(session.cwd, args[0])
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read(4096)
            if len(data) == 4096:
                data += "\n... (truncated)"
            return data
        except Exception as e:
            return f"cat: {e}"

class RmCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "rm: missing operand"
        try:
            file_path = resolve_path(session.cwd, args[0])
            os.remove(file_path)
            return "file removed"
        except FileNotFoundError:
            return f"rm: cannot remove '{args[0]}': No such file or directory"
        except IsADirectoryError:
            return f"rm: cannot remove '{args[0]}': Is a directory"
        except Exception as e:
            return f"rm: cannot remove '{args[0]}': {e}"

class CpCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if len(args) < 2:
            return "cp: missing file operand"
        try:
            src = resolve_path(session.cwd, args[0])
            dst = resolve_path(session.cwd, args[1])
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            return "file copied"
        except FileNotFoundError:
            return f"cp: cannot stat '{args[0]}': No such file or directory"
        except Exception as e:
            return f"cp: {e}"

class MvCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if len(args) < 2:
            return "mv: missing file operand"
        try:
            src = resolve_path(session.cwd, args[0])
            dst = resolve_path(session.cwd, args[1])
            os.rename(src, dst)
            return "file moved"
        except FileNotFoundError:
            return f"mv: cannot stat '{args[0]}': No such file or directory"
        except Exception as e:
            return f"mv: {e}"

class StatCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "stat: missing operand"
        try:
            path = resolve_path(session.cwd, args[0])
            st = os.stat(path)
            perms = stat.filemode(st.st_mode)
            nlink = st.st_nlink
            owner = st.st_uid if hasattr(st, 'st_uid') else 0
            group = st.st_gid if hasattr(st, 'st_gid') else 0
            size = st.st_size
            mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))
            info = f"  File: {args[0]}\n  Type: {'Directory' if os.path.isdir(path) else 'File'}\n  Size: {size} bytes\n  Permissions: {perms}\n  Links: {nlink}\n  Owner: {owner}\n  Group: {group}\n  Modified: {mtime}"
            return info
        except Exception as e:
            return f"stat: {e}"

class TouchCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "touch: missing file operand"
        try:
            file_path = resolve_path(session.cwd, args[0])
            with open(file_path, 'a'):
                os.utime(file_path, None)
            return "file touched"
        except Exception as e:
            return f"touch: cannot touch '{args[0]}': {e}"

class EchoCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "login required"
        if not args:
            return "echo: missing arguments"
        # Support echo "hello" > a.txt
        if '>' in args:
            idx = args.index('>')
            content = ' '.join(args[:idx])
            filename = args[idx+1] if len(args) > idx+1 else None
            if not filename:
                return "echo: missing filename after >"
            try:
                file_path = resolve_path(session.cwd, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content.strip('"'))
                return "echoed to file"
            except Exception as e:
                return f"echo: cannot write to '{filename}': {e}"
        else:
            # Just echo to output
            content = ' '.join(args)
            return content.strip('"')