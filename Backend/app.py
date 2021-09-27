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

@app.route('/api/login',methods=['get'])
def login():
    email = 'superuser1'#request.form.get('email')
    password = 'password' #request.form.get('password')
    conn = mysql.get_db().cursor()
    car_query = "SELECT * FROM user WHERE email = '"+email+"'"
    conn.execute(car_query)
    row_headers=[x[0] for x in conn.description] 
    data = conn.fetchall()
    response =[]
    for result in data:
        response.append(dict(zip(row_headers,result)))
    
    print(response)
    #if response[0]['email'] == email and response[0]['password'] == password:


    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "response": response
        }
    )

@app.route('/api/register',methods=['post'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    conn = mysql.get_db().cursor()
    car_query = """
        INSERT INTO `user` (`email`, `password`)
        values ('"""+email+"""','"""+password+"""')
    """
    conn.execute(car_query)
    
    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "response": "Successfully added"
        }
    )

@app.route('/api/predict/<args>',methods=['GET'])
def predict(args):
    result = make_prediction(np.fromstring(args,dtype=int,sep=','))
    return jsonify(
        {
            "result": result
        }
    )

@app.route('/api/getCars',methods=['GET'])
def getAllCars():
    conn = mysql.get_db().cursor()
    car_query = "SELECT * FROM car_detail"
    conn.execute(car_query)
    response = conn.fetchall()
    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "cars": response
        }
    )

@app.route('/api/setFavCars/<user_id>/<car_id>',methods=['GET'])
def setFavCar(user_id,car_id):
    conn = mysql.get_db().cursor()
    car_query = """
        INSERT INTO `favorite_car` (`user_id`, `car_id`, `active`)
        values ('"""+user_id+"""','"""+car_id+"""', 'TRUE') ON DUPLICATE KEY UPDATE `active` = NOT active
    """
    conn.execute(car_query)
    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "response": "Successfully added"
        }
    )

@app.route('/api/getFavCars/<user_id>/<car_id>',methods=['GET'])
def getFavCar(user_id,car_id):
    conn = mysql.get_db().cursor()
    car_query = "SELECT * FROM favorite_car WHERE '"+user_id+"','"+car_id+"'"
    conn.execute(car_query)
    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "response": "Successfully added"
        }
    )

@app.route('/populate',methods=['GET'])
def populateDb():
    conn = mysql.get_db().cursor()
    user_query = "INSERT INTO user (email,password) SELECT 'superuser','123' WHERE NOT EXISTS (SELECT 1 FROM user WHERE email = 'superuser')"
    conn.execute(user_query)
    
    car_query = "INSERT INTO car_detail (brand,model_name,year,type,cc,price) SELECT "
    car_data = pd.read_excel('model/Cardetail.xlsx',index_col=0,dtype={'Model name': str,'Year':str,'CC':str,'price':str})
    for index, row in car_data.iterrows():
        conn.execute(car_query + "'"+str(index)+"','"+str(row['Model name'])+"','"+str(row['Year'])+"','"+str(row['Type'])+"','"+str(row['CC'])+"','"+str(row['Price'])+
        "' WHERE NOT EXISTS (SELECT 1 FROM car_detail WHERE model_name = '"+str(row['Model name'])+"' AND year = '"+str(row['Year'])+"' )")

    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "response": "Database population successful"
        }
    )

@app.route('/generateTable',methods=['GET'])
def generateDbTable():
    create_user_table_query = """CREATE TABLE IF NOT EXISTS `user` (
        `user_id` INT NOT NULL AUTO_INCREMENT,
        `email` VARCHAR(50) NOT NULL UNIQUE,
        `password` VARCHAR(50) NOT NULL,
        PRIMARY KEY (`user_id`));"""
    create_car_detail_table_query = """CREATE TABLE IF NOT EXISTS `car_detail` (
        `car_id` INT NOT NULL AUTO_INCREMENT,
        `brand` VARCHAR(20) NOT NULL,
        `model_name` VARCHAR(70) NOT NULL,
        `year` VARCHAR(8),`type` VARCHAR(20),
        `cc` VARCHAR(20),`price` DOUBLE,
        PRIMARY KEY (`car_id`));"""
    create_favorite_car_table_query = """CREATE TABLE `favorite_car` (
	    `user_id` INT NOT NULL,
	    `car_id` INT NOT NULL,
	    `active` BOOLEAN NOT NULL DEFAULT FALSE,
	    PRIMARY KEY (`user_id`,`car_id`));"""
   
    conn = mysql.get_db().cursor()
    conn.execute(create_user_table_query)
    conn.execute(create_car_detail_table_query)
    conn.execute(create_favorite_car_table_query)
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