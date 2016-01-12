import csv
import sqlite3
db =  sqlite3.connect("db/bads.db")

with open('testset.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    for row in reader:
        db.execute("insert into actuals (Customer_ID,Churn) values (?,?)",[row[1],row[2]])
    db.commit()
