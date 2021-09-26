from flask import Flask, request, jsonify
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
def home_page():
    return "<p>This is home page</p>"

@app.route('/api/predict',methods=['GET'])
def predict():
    result = make_prediction("")
    return jsonify(
        {
            "result": result
        }
    )

@app.route('/populate',methods=['GET'])
def populateDb():
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
    return jsonify(
        {
            "response": "Database population successful"
        }
    )

@app.route('/generateTable',methods=['GET'])
def generateDbTable():
    create_user_table_query = "CREATE TABLE `user` (`user_id` INT NOT NULL AUTO_INCREMENT,`email` VARCHAR(50) NOT NULL UNIQUE,`password` VARCHAR(50) NOT NULL,PRIMARY KEY (`user_id`));"
    create_car_detail_table_query = "CREATE TABLE `car_detail` (`car_id` INT NOT NULL AUTO_INCREMENT,`brand` VARCHAR(20) NOT NULL,`model_name` VARCHAR(50) NOT NULL,`year` VARCHAR(8),`type` VARCHAR(20),`cc` VARCHAR(20),`price` DOUBLE,PRIMARY KEY (`car_id`));"
    create_favorite_car_table_query = "CREATE TABLE `favorite_car` (`id` INT NOT NULL AUTO_INCREMENT,`user_id` VARCHAR(20) NOT NULL,`car_id` VARCHAR(50) NOT NULL,PRIMARY KEY (`id`));"
   
    conn = mysql.get_db().cursor()
    conn.execute(create_user_table_query)
    conn.execute(create_car_detail_table_query)
    conn.execute(create_favorite_car_table_table_query)
    mysql.get_db().commit()
    conn.close()
    populateDb()
    return jsonify(
        {
            "response": "Table created sucessfully"
        }
    )


if __name__ == '__main__':
    app.run(port=5000, debug=True)