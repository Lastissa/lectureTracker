import requests
import threading
import random

LOGIN_URL = "http://127.0.0.1:8000/viewData/json/"

p = "allahu"

TOTAL_USERS = 720

def login_user():
    response = requests.get(
        LOGIN_URL,
        params={
            "email": "lastissa11@gmail.com",
            "password": "".join(random.sample(p, 6))
        }
    )
    if response.status_code != 401:
        print(response.status_code)
        print(response.url)
        print(response.text)
        
    else:
        print(response.status_code)
    
    

threads = []

for index in range(TOTAL_USERS):
    thread = threading.Thread(target=login_user)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()