import pickle
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_folder = os.path.join(BASE_DIR,'Backend/model/')
model_file = os.path.join(model_folder,'model.sav')

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
        #   print(maxval)
        #   print(self.data[j]['y'])
    return str(self.data[maxind]['y'])
  def fit(self,X,y):
    for i in range(len(X)):
      self.data.append({'X':np.array(X.iloc[i,:]),'y':np.array(y.iloc[i])})


class CustomUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module == "__main__":
            module = "model_util"
        return super().find_class(module, name)

with open('model/model.pkl','rb') as f:
    unpickler = CustomUnpickler(f)
    loaded_model = unpickler.load()

def make_prediction(data_input):
    result = loaded_model.predict([data_input])
    return result

