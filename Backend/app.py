from flask import Flask, request
from flaskext.mysql import MySQL
import pickle
import numpy as np
from model_util import make_prediction
import os
import pandas as pd

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'car_sen'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def hello_world():
    return "<p>Hello world</p>"

@app.route('/api',methods=['GET'])
def api():
    result = make_prediction()
    print(result)
    write = "<p>The result of this prediction is "+ result +"</p>"
    return write

@app.route('/populate',methods=['GET'])
def populateDb():
    data = ""
    conn = mysql.get_db().cursor()
    user_query = "INSERT INTO user (email,password) SELECT 'superuser','123' WHERE NOT EXISTS (SELECT 1 FROM user WHERE email = 'superuser')"
    conn.execute(user_query)
    
    car_query = "INSERT INTO cardetail (brand,model_name,year,type,cc,price) SELECT "
    car_data = pd.read_excel('model/Cardetail.xlsx',index_col=0,dtype={'Model name': str,'Year':str,'CC':str,'price':str})
    for index, row in car_data.iterrows():
        conn.execute(car_query + "'"+str(index)+"','"+str(row['Model name'])+"','"+str(row['Year'])+"','"+str(row['Type'])+"','"+str(row['CC'])+"','"+str(row['Price'])+
        "' WHERE NOT EXISTS (SELECT 1 FROM cardetail WHERE model_name = '"+str(row['Model name'])+"' AND year = '"+str(row['Year'])+"' )")

    mysql.get_db().commit()
    conn.close()
    return 'success'

if __name__ == '__main__':
    app.run(port=5000, debug=True)