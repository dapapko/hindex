import sys
import uuid
import requests
from ferBackend import FERBackend
print(sys.argv)
if len(sys.argv) != 3:
   print("You need to specify key and path to image")
   sys.exit(1) 
key, path = sys.argv[1], sys.argv[2]
print('Обработка')
backend = FERBackend(path)
backend.exec()
print(backend.output())
data = {"key":key, "result":backend.output()}
r = requests.post('http://localhost:5000/setresult', json=data)
