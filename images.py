from os import listdir
from os.path import isfile, join
import re


class ImageBank():
   def __init__(self,path):
      self.pic = {} 
      self.path = path
      self.load(path)

   def load(self,path):
      files = [f for f in listdir(path) if isfile(join(path,f))]
      for f in files:
         if f[-3:] == 'txt':
            with open(join(path,f),'r') as txtfile:
               self.pic[f[:-4]]=txtfile.read()[:-1]

   def rescan(self):
      self.load(self.path)

class ToshiImage():
   def __init__(self,imagebank):
      self.lvl = {}
      # tama_##_name.txt
      toshis = [k for k in imagebank.keys() if re.match(r'toshi_\d\d_.+',k) ]
      for t in toshis:
         self.lvl[int(t[5:7])]={'pic':imagebank[t],'type':t[8:]}
      

pics = ImageBank('images')
toshis = ToshiImage(pics.pic)

