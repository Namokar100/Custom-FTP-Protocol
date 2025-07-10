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

class StorCommand:
    def handle(self, args, session):
        if not session.logged_in:
            return "530 Not logged in\r\n"
        if not args:
            return "501 Missing filename\r\n"
        try:
            file_path = resolve_path(session.cwd, args[0])
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