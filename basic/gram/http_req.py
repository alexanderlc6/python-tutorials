import urllib.request
import json

# Get request
url = 'http://localhost:8080/NoteWebService/node.do?action=query&ID=10'

req = urllib.request.Request(url)
with urllib.request.urlopen(req) as response:
       data = response.read()
       json_data = data.decode()
       print(json_data)

       # Convert json string to Python dict(object)
       py_dict = json.loads(json_data)
       print('MemoDate:', py_dict['MDate'])

# POST request
url = 'http://localhost:8080/NoteWebService/node.do'
params_dict = { 'action': 'query', 'ID': '10'}
params_str = urllib.parse.urlencode(params_dict)
print(params_str)

params_bytes = params_str.encode()
req = urllib.request.Request(url, data = params_bytes)
with urllib.request.urlopen(req) as response:
       data = response.read()
       json_data = data.decode()
       print(json_data)