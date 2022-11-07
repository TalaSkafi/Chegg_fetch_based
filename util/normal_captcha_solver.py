import os

from twocaptcha import TwoCaptcha

from services.constants import API


def normal_captcha_solver(image):
    api_key = os.getenv('APIKEY_2CAPTCHA', API)

    solver = TwoCaptcha(api_key)

    try:
        result = solver.normal(image)
    except Exception as e:
        print(str(e))
    else:
        result = str(list(result.values())[1])
        return result
