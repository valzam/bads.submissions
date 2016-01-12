from flask import current_app as app
import sqlite3
import pandas as pd

def read_predictions(file):
    preds = []
    ids = []

    for line in file:
        # Skip if the user included the csv heading
        if "Customer_ID" in line:
            continue

        # Split csv lines
        l = line.split(",")
        ids.append(l[0])
        preds.append(float(l[1]))

    predictions_pd = pd.Series(preds, index=ids)
    return predictions_pd

def get_actuals():
    '''
    Gets the true values from the DATABASE
    and returns them as a pandas series
    '''
    db =  sqlite3.connect(app.config["DATABASE"])
    cur = db.execute("select * from actuals")
    ids = []
    churn = []
    for row in cur.fetchall():
        ids.append(row[0])
        churn.append(row[1])

    # Convert to pandas series
    actuals_pd = pd.Series(churn, index=ids)
    return actuals_pd

def calculate_score(file):
    db =  sqlite3.connect(app.config["DATABASE"])

    actuals=get_actuals()
    preds = read_predictions(file)



    a_df = pd.DataFrame(actuals, columns=["Actual"])
    p_df = pd.DataFrame(preds, columns=["Prediction"])

    print a_df[:10]
    print p_df[:10]
    df = a_df.join(p_df,how="inner")

    print df[:1000]
    score = 1.5
    db.execute("insert into submissions (lift_score) values (?)",[score])
    db.commit()
    return score
