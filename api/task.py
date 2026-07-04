from celery import shared_task
import requests

@shared_task
def email_delegate():
    response = requests.get(url="https://esta-sensate-unquickly.ngrok-free.dev/sd/")
    print(f"Email delegate task executed with status code {response.status_code}.")
    