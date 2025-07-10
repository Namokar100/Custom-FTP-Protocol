import os

USER_DB_PATH = os.path.join(os.path.dirname(__file__), '../config/users.txt')

def load_users():
    users = {}
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, 'r') as f:
            for line in f:
                if ':' in line:
                    username, password = line.strip().split(':', 1)
                    users[username] = password
    return users

class UserCommand:
    def handle(self, args, session):
        if not args:
            return "501 Syntax error in parameters or arguments.\r\n"
        session.username = args[0]
        session.logged_in = False  # Reset login state on new USER
        session._user_db = load_users()
        if session.username in session._user_db:
            return "331 User name okay, need password.\r\n"
        else:
            return "530 Not logged in.\r\n"

class PassCommand:
    def handle(self, args, session):
        if not session.username:
            return "503 Bad sequence of commands.\r\n"
        if not args:
            return "501 Syntax error in parameters or arguments.\r\n"
        expected_password = session._user_db.get(session.username)
        if expected_password and args[0] == expected_password:
            session.logged_in = True
            return "230 User logged in, proceed.\r\n"
        else:
            session.logged_in = False
            return "530 Not logged in.\r\n"

class QuitCommand:
    def handle(self, args, session):
        return "221 Service closing control connection.\r\n"