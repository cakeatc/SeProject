from flask import Flask
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_folder = os.path.join(BASE_DIR,'Backend/model/')
model_file = os.path.join(model_folder,'model.sav')

# Import CosineSimModel
class CosineSimModel:
  def __init__(self):
    self.data = []
  def predict(self,X):
    maxind = 0
    maxval = 0
    for i in X:
      for j in range(len(self.data)):
        tempY = self.data[j]['X'].reshape(1,-1)
        cs = cosine_similarity(X,tempY)
        if cs > maxval:
          maxval = cs
          maxind = j
          print(maxval)
          print(self.data[j]['y'])
    return str(self.data[maxind]['y'])
  def fit(self,X,y):
    for i in range(len(X)):
      self.data.append({'X':np.array(X.iloc[i,:]),'y':np.array(y.iloc[i])})

def make_prediction():
    loaded_model = pickle.load(open('model/model.pkl', 'rb'))
    result = loaded_model.predict([[1,1,1,4,2,3,1,1,0,5]])
    print(result)
    return ""


app = Flask(__name__)

if __name__ == '__main__':
    pickle.load('model/model.pkl')
    app.run(port=5000)

@app.route("/")
def hello_world():
    return "<p>Hello world</p>"

@app.route('/api',methods=['GET'])
def api():
    # temp = make_prediction()
    # print(temp)
    write = "<p>This is api</p>"
    return write