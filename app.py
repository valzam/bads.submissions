import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from werkzeug import secure_filename
import lift_score as ls


# Create application
DATABASE = "db/bads.db"
DEBUG = True
SECRET_KEY = "badsswtsubs"
USERNAME = "admin"
PASSWORD = "default"
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config.from_object(__name__)

# Helper functions
def connect_db():
    return sqlite3.connect(app.config["DATABASE"])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Middleware
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g,"db",None)
    if db is not None:
        db.close()

# Routes
@app.route("/", methods=["GET","POST"])
def show_main():
    cur = g.db.execute("select * from submissions order by lift_score desc limit 20")
    submissions = [dict(date=row[0],score=row[1]) for row in cur.fetchall()]

    if request.method == "POST":
        file = request.files['file']
        filename = secure_filename(file.filename)
        if not allowed_file(file.filename):
            flash("Upload failed -- Make sure to only upload .csv files!",'danger')
            return redirect(url_for('show_main'))

        if file:
            predictions_pd, predictions = ls.read_predictions(file)
            score = ls.calculate_score(predictions_pd,actuals)

            return render_template('main.html',submissions=submissions,predictions=predictions,score=score)

        else:
            flash("Something went wrong",'danger')
            return redirect(url_for('show_main'))

    else:
     return render_template("main.html",submissions=submissions)


if __name__ == "__main__":
    app.run()
