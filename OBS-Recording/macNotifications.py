import os

class Notificator:
    def notify(self, title, text):
        os.system("""osascript -e 'display notification "{}" with title "{}"'""".format(text, title))

