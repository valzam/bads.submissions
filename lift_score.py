from flask import current_app as app
import sqlite3
import pandas as pd

def read_predictions(file):
    preds = []
    ids = []
    predictions = []
    for line in file:
        l = line.split(",")
        ids.append(l[0])
        preds.append(l[1])
        predictions.append(dict(id=l[0],prediction=l[1]))

    predictions_pd = pd.Series(preds, index=ids)
    return predictions_pd,predictions
def calculate_score(preds,actuals):
    db =  sqlite3.connect(app.config["DATABASE"])

    preds = preds.sort(asc=0)

    score = 1.5
    db.execute("insert into submissions (lift_score) values (?)",[score])
    db.commit()
    return score
