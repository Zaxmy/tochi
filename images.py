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

class TochiImage():
   def __init__(self,imagebank):
      self.lvl = {}
      # tama_##_name.txt
      tochis = [k for k in imagebank.keys() if re.match(r'tochi_\d\d_.+',k) ]
      for t in tochis:
         #print("Lvl %2d - %s " % (int(t[6:8]),t[9:]))
         try:
            self.lvl[int(t[6:7])]={'pic':imagebank[t],'type':t[9:]}
         except ValueError:
            print("Tochi image name wrong format [%s] not in form tochi_\\d\\d_.+ "%(t))
            exit()
      
      

pics = ImageBank('images')
tochis = TochiImage(pics.pic)

# vim: set sw=3 expandtab ts=3