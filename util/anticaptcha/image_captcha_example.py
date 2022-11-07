import base64

from util.anticaptcha. imagecaptcha import *
from services.constants import API2
from base64 import  b64decode

def anticaptcha_solver(API,src):
    solver = imagecaptcha()
    solver.set_verbose(1)
    solver.set_key(API)
    # src = "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"
    captcha_text = solver.solve_and_return_solution(src)
    if captcha_text != 0:
        print("captcha text " + captcha_text)


        return captcha_text
    else:
        print("task finished with error " + solver.error_code)
        return solver.error_code




