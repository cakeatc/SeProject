from flask import Flask
import pickle
import numpy as np
from model_util import make_prediction
import os

app = Flask(__name__)


    
@app.route("/")
def hello_world():
    return "<p>Hello world</p>"

@app.route('/api',methods=['GET'])
def api():
    result = make_prediction()
    print(result)
    write = "<p>The result of this prediction is "+ result +"</p>"
    return write

if __name__ == '__main__':
    app.run(port=5000, debug=True)