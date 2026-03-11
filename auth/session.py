import datetime


class Session:

    def __init__(self, token, username, duration_minutes):

        self.token = token
        self.username = username

        self.created_at = datetime.datetime.now()
        self.expires_at = self.created_at + datetime.timedelta(minutes=duration_minutes)

        self.active = True