import requests

USERNAME = "AFray"

TOKEN = "97cebb3b7c27feb88b1c2f02327a165b929301d0"

RFILEPATH = f'files/path/home/{USERNAME}/website.zip'
LFILEPATH = "./website.zip"

API = f'https://www.pythonanywhere.com/api/v0/user/{USERNAME}/'


with open(LFILEPATH, 'rb') as f:
    data = f.read()

res = requests.post(API + RFILEPATH,
     files={'content': data},
     headers={'Authorization': 'Token ' + TOKEN}
 )

print(res)
print(res.text)