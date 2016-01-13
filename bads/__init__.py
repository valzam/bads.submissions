from flask import Flask

# Create application
DATABASE = "bads/db/bads.db"
DEBUG = True
SECRET_KEY = "badsswtsubs"
USERNAME = "admin"
PASSWORD = "default"
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config.from_object(__name__)

import bads.views

if __name__ == "__main__":
    app.run()
