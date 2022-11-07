import base64
import re
import boto3

from services.constants import ACCESS_KEY_ID, SECRET_ACCESS_KEY, BUCKET_NAME


def store_img(s3,captcha_id,imgSolution,imgSrc):
    path="images/" + str(captcha_id) + "_" + str(imgSolution) + ".png"
    fh = open(path, "wb")
    fh.write(base64.b64decode(imgSrc))
    s3.upload_file(path, BUCKET_NAME, path)
    fh.close()

