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
            return "user: missing username"
        session.username = args[0]
        session.logged_in = False
        session._user_db = load_users()
        if session.username in session._user_db:
            return "user accepted"
        else:
            return "user: unknown user"

class PassCommand:
    def handle(self, args, session):
        if not session.username:
            return "pass: login with USER first"
        if not args:
            return "pass: missing password"
        expected_password = session._user_db.get(session.username)
        if expected_password and args[0] == expected_password:
            session.logged_in = True
            return "user logged in"
        else:
            session.logged_in = False
            return "pass: incorrect password"

class QuitCommand:
    def handle(self, args, session):
        return "goodbye"