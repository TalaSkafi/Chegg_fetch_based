import os
import sys

from twocaptcha import TwoCaptcha

from services.constants import API


def hcaptcha_solver(site_key, url):
    api_key = os.getenv('APIKEY_2CAPTCHA', API)
    solver = TwoCaptcha(api_key)

    try:
        result = solver.hcaptcha(
            sitekey=site_key,
            url='https://homeworkify.net/',
        )

    except Exception as e:
        sys.exit(e)

    else:
        result = str(list(result.values())[1])
        # print(result)

        return result
