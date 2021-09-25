from flask import Flask, request
from flaskext.mysql import MySQL
import pickle
import numpy as np
from model_util import make_prediction
import os

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
    query_item = "INSERT INTO user (email,password) VALUE ('guy','123456')"
    conn.execute(query_item)
    mysql.get_db().commit()
    conn.close()
    return 'success'

if __name__ == '__main__':
    app.run(port=5000, debug=True)