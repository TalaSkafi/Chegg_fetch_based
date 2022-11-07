import re
import requests
from os import environ
import threading
import time
from anycaptcha import AnycaptchaClient, ImageToTextTask
import random

def demo_imagetotext(image):
    api_key = '007a5953a34e42759fcb6e741798b86d'
    captcha_fp = image
    client = AnycaptchaClient(api_key)
    task = ImageToTextTask(captcha_fp)
    job = client.createTask(task,typecaptcha="text")
    job.join()
    result = job.get_solution_response()
    if result.find("ERROR") != -1:
        print("error ", result)
    else:
        print("success ", result)

    return result

