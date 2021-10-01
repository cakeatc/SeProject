from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
import pickle
import numpy as np
from model_util import make_prediction
import os
import pandas as pd

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'car_sen'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def home_page():
    return "<p>This is home page</p>"

@app.route('/api/login',methods=['POST'])
@cross_origin()
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        conn = mysql.get_db().cursor()
        login_query = "SELECT * FROM user WHERE email = '"+email+"'"
        conn.execute(login_query)
        row_headers=[x[0] for x in conn.description] 
        data = conn.fetchall()
        response =[]
        for result in data:
            response.append(dict(zip(row_headers,result)))
        mysql.get_db().commit()
        conn.close()
        response = response[0]
        if response['password'] == password:
            return jsonify(
            {
                "response": response
            }
        )
        else:
            return jsonify(
            {
                "response": None,
                "error": "The password you've entered is incorrect"
            }
        )
    except:
        return jsonify(
            {
                "response": None,
                "error": "The email you've entered is incorrect"
            }
        ) 

def getAddedUser(email,password):
    conn = mysql.get_db().cursor()
    login_query = "SELECT * FROM user WHERE email = '"+email+"'"
    conn.execute(login_query)
    row_headers=[x[0] for x in conn.description] 
    data = conn.fetchall()
    response =[]
    for result in data:
        response.append(dict(zip(row_headers,result)))
    mysql.get_db().commit()
    conn.close()
    response = response[0]
    if response['password'] == password:
        return jsonify(
        {
            "response": response
        }
    )
    else:
        return jsonify(
        {
            "response": "Error cannot find user"
        }
    )

@app.route('/api/register',methods=['POST'])
@cross_origin()
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    conn = mysql.get_db().cursor()
    login_query = "SELECT * FROM user WHERE email = '"+email+"'"
    conn.execute(login_query)
    mysql.get_db().commit()
    if len(conn.fetchall()) > 0:
        return jsonify(
            {
                "response": None,
                "error": "The account you've entered already exists."
            }
        )
    else:
        register_query = """
            INSERT INTO `user` (`email`, `password`)
            values ('"""+email+"""','"""+password+"""')
        """
        conn.execute(register_query)
        mysql.get_db().commit()
        conn.close()
        return getAddedUser(email,password)

@app.route('/api/predict/<args>',methods=['GET'])
@cross_origin()
def predict(args):
    result = make_prediction(np.fromstring(args,dtype=int,sep=','))
    keys = {'MPV (Multi-purpose vehicle)':'MVP',
    'Eco car':'Eco car',
    'Sedans':'Sedan',
    'SUVs (Sport Utility Vechicle)':'SUV',
    'Pickup Trucks':'Pickup truck',
    'nan':'nan',
    'Hatchbacks':'Hatchback'}
    cars = getCarsByPredict(keys[result])
    return jsonify(
        {
            "result": result,
            "cars": cars
        }
    )

@app.route('/api/getCars',methods=['GET'])
@cross_origin()
def getAllCars():
    conn = mysql.get_db().cursor()
    car_query = "SELECT * FROM car_detail"
    conn.execute(car_query)
    row_headers=[x[0] for x in conn.description] 
    data = conn.fetchall()
    response =[]
    for result in data:
        response.append(dict(zip(row_headers,result)))
    mysql.get_db().commit()
    conn.close()
    return jsonify(
        {
            "cars": response
        }
    )

@app.route('/api/getCars/<args>',methods=['GET'])
@cross_origin()
def getCarsByPredict(args):
    conn = mysql.get_db().cursor()
    car_query = "SELECT * FROM car_detail WHERE type = '"+args+"'"
    print(car_query)
    conn.execute(car_query)
    row_headers=[x[0] for x in conn.description] 
    data = conn.fetchall()
    response =[]
    for result in data:
        response.append(dict(zip(row_headers,result)))
    mysql.get_db().commit()
    conn.close()
    return response

@app.route('/api/setFavCars/<user_id>/<car_id>',methods=['GET'])
@cross_origin()
def setFavCar(user_id,car_id):
    conn = mysql.get_db().cursor()
    car_query = """
        INSERT INTO `favorite_car` (`user_id`, `car_id`, `active`)
        values ('"""+user_id+"""','"""+car_id+"""', TRUE) ON DUPLICATE KEY UPDATE `active` = NOT active
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
@cross_origin()
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