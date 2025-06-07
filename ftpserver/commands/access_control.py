class UserCommand:
    def handle(self, args, session):
        if not args:
            return "501 Syntax error in parameters\r\n"
        session.username = args[0]
        return "331 Username ok, need password\r\n"

class PassCommand:
    def handle(self, args, session):
        if session.username:
            session.logged_in = True
            return "230 User logged in\r\n"
        else:
            return "503 Bad sequence of commands\r\n"

class QuitCommand:
    def handle(self, args, session):
        return "221 Goodbye\r\n"
