import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash, jsonify
from werkzeug import secure_filename
import lift_score as ls
import pandas as pd
from bads import app

# Helper functions
def connect_db():
    return sqlite3.connect(app.config["DATABASE"])

def allowed_file(filename):
    '''
    Checks if the file has an allowed format
    '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config["ALLOWED_EXTENSIONS"]

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
    if request.method == "POST":
        identifier = request.form["identifier"]
        print request.form
        file = request.files['file']
        filename = secure_filename(file.filename)
        if not allowed_file(file.filename):
            flash("Upload failed -- Make sure to only upload .csv files!",'danger')
            return redirect(url_for('show_main'))

        if file:
            score,used_preds = ls.calculate_score(file,identifier)

            # Error checking
            if score is None:
                flash(used_preds,'danger')
                return redirect(url_for('show_main'))

            cur = g.db.execute("select * from submissions order by lift_score desc limit 20")
            submissions = [dict(date=row[0],score=row[1],identifier=row[2]) for row in cur.fetchall()]
            return render_template('main.html',submissions=submissions,predictions=used_preds,score=score)

        else:
            flash("Something went wrong",'danger')
            return redirect(url_for('show_main'))

    else:
        cur = g.db.execute("select * from submissions order by lift_score desc limit 20")
        submissions = [dict(date=row[0],score=row[1],identifier=row[2]) for row in cur.fetchall()]
        return render_template("main.html",submissions=submissions)
