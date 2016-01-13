from __future__ import division
from flask import current_app as app
import sqlite3
import pandas as pd
from bads import app

def read_predictions(file):
    preds = []
    ids = []

    for line in file:
        # Skip if the user included the csv heading
        if "Customer_ID" in line:
            continue

        # Split csv lines
        l = line.split(",")
        if len(l) > 1:
            ids.append(l[0])
            preds.append(float(l[1]))

    # Check for correct parsing
    if len(preds) is 0 or len(ids) is 0:
        return None

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
        ids.append(str(row[0]))
        churn.append(row[1])

    # Convert to pandas series
    actuals_pd = pd.Series(churn, index=ids)
    return actuals_pd

def calculate_score(file,identifier):
    db =  sqlite3.connect(app.config["DATABASE"])

    actuals = get_actuals()
    preds = read_predictions(file)

    # Check if the csv has been parsed correctly
    if preds is None:
        return None,"There was a problem parsing the csv. Please make sure it is in the correct format"

    a_df = pd.DataFrame(actuals, columns=["Actual"])
    p_df = pd.DataFrame(preds, columns=["Prediction"])

    df = a_df.join(p_df,how="inner")

    score,used_preds = lift_score(df)

    db.execute("insert into submissions (lift_score,identifier) values (?,?)",[score,identifier])
    db.commit()

    # Get the top 10 predictions for illustration purposes
    top_used_preds = []
    for i in range(1,10):
        row =used_preds.iloc[i]
        top_used_preds.append({"id":used_preds.index.tolist()[i],"actual":row[0], "prediction":row[1]})
    return score,top_used_preds

def lift_score(df):
    """
    Calculate the lift score:
    (Prescision_top10)/(Prescision_random)
    Random Change: 2500/27500 = ~0.09
    """
    random_chance = 0.09
    df.sort_values("Prediction",ascending=False,inplace=True)
    df_top10 = df[:2750]

    pred_acu = (len(df_top10[df_top10["Actual"] == "leave"]) / len(df_top10))
    rand_acu = (len(df[df["Actual"] == "leave"]) / len(df))
    score = pred_acu / rand_acu

    return score,df_top10
