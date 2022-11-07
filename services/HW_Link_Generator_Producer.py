import base64
import sys
import time

import boto3

from repository.question_repository import QuestionRepository
from services.constants import HWifyURL, site_key_verify_human, API2, ACCESS_KEY_ID, SECRET_ACCESS_KEY
from util.anticaptcha.image_captcha_example import anticaptcha_solver
from util.browser_driver import BrowserDriver
from util.img_downloader import store_img
from util.mysql_db_manager import MySqlDBManager
from bs4 import BeautifulSoup as B

from util.slack import Slack

question_repository = QuestionRepository()
mysql_db_manager = MySqlDBManager('admin',
                                  'QuizPlus123',
                                  'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                  'chegg_general_crawler',
                                  '3306')
s3 = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY
)

class HW_Link_Generator_Producer:

    def _start_crawling(self,process_id):
        driver = BrowserDriver().driver
        driver.get("https://homeworkify.net/")
        time.sleep(3)
        questions = question_repository.get_first_not_answer_retrived_k_questions(mysql_db_manager,process_id, 500)


        for question in questions:
            #Slack().send_message_to_slack("PRODUCER", "Producer made "+str(question_repository.get_produced_count(mysql_db_manager))+" questions waiting for consumer")
            while True:
                if question_repository.get_produced_count(mysql_db_manager)>20:
                    print()
                    continue

                try:
                    homework_id, endpoint, sid = self.getQuestionInformation(driver, question.chegg_id)

                except Exception as e:
                    time.sleep(1)
                    homework_id = None
                    print(e)

                if homework_id is None:
                    print("Error retriving Question:"+question.chegg_id)
                    time.sleep(1)
                    continue
                if  "Not Found Question" == homework_id:
                    print("No Answer:"+str( question.chegg_id))
                    question_repository.update_HW_has_answer_state(mysql_db_manager,question.id,"NO_ANSWER")
                    break
                if  "storytelling-number-one-skill-improve" not in endpoint:
                    time.sleep(1)
                    continue

                try:
                    imgSRC, captcha_id, captcha_session = self.getRecaptchaIformation(driver)
                    if captcha_id is None:
                        time.sleep(1)
                        continue
                    captchaSolution = self.solveRecptcha(imgSRC)
                    token = self.getRecpatchaToken(driver, captchaSolution, captcha_id, captcha_session, sid,imgSRC)
                    if len(token) > 0:
                        final_url = endpoint + "?hw-id=" + homework_id + "&token=" + token
                        question_repository.update_generated_url_answer(mysql_db_manager, question.id, final_url)
                        print("Process ID:" + str(process_id) + "-" + final_url)
                        break
                except Exception as e:
                    time.sleep(1)
                    print(e)






    def getRecpatchaToken(self,driver, imgSolution,captcha_id,captcha_session,sid,imgSrc):
        for i in range(1,2):
            code=("const results=await "
                 "fetch(\"https://homeworkify.net/wp-admin/admin-ajax.php\", {\n"
                 + "  \"headers\": {\n"
                 + "    \"accept\": \"*/*\",\n"
                 + "    \"accept-language\": \"en-US,en;q=0.9\",\n"
                 + "    \"content-type\": \"application/x-www-form-urlencoded; charset=UTF-8\",\n"
                 + "    \"sec-ch-ua\": \"\\\"Google Chrome\\\";v=\\\"107\\\", \\\"Chromium\\\";v=\\\"107\\\", \\\"Not=A?Brand\\\";v=\\\"24\\\"\",\n"
                 + "    \"sec-ch-ua-mobile\": \"?0\",\n"
                 + "    \"sec-ch-ua-platform\": \"\\\"macOS\\\"\",\n"
                 + "    \"sec-fetch-dest\": \"empty\",\n"
                 + "    \"sec-fetch-mode\": \"cors\",\n"
                 + "    \"sec-fetch-site\": \"same-origin\",\n"
                 + "    \"x-requested-with\": \"XMLHttpRequest\"\n"
                 + "  },\n"
                 + "  \"referrer\": \"https://homeworkify.net/\",\n"
                 + "  \"referrerPolicy\": \"strict-origin-when-cross-origin\",\n"
                 + "  \"body\": \"action=verify_captcha_challenge&user_input=SOLUTION&captcha_id=CAPTCHAID&captcha_session=SESSION_CAPTCHA&sid=HASHSID\",\n"
                 + "  \"method\": \"POST\",\n"
                 + "  \"m    ode\": \"cors\",\n"
                 + "  \"credentials\": \"include\"\n"
                 + "});"
                   "  let data = await results.json();"
                   " return data;").\
                replace("SOLUTION", str(imgSolution)).\
                replace("CAPTCHAID", str(captcha_id)).\
                replace("SESSION_CAPTCHA", str(captcha_session)) .\
                replace("HASHSID", str(sid));
            #print(code)

            result = driver.execute_script(code);
            token = ""
            print(result)
            sucess = result.get("success")
            print("sucess:" + str(sucess))
            if sucess:

                token = result.get("token")
                store_img(s3,captcha_id,imgSolution,imgSrc)
                # fh = open("images/" + str(captcha_id)+"_"+ str(imgSolution) + ".png", "wb")
                # fh.write(base64.b64decode(imgSrc))
                # fh.close()
                return token

        return ""


    def solveRecptcha(self,imgSRC):
        solution = anticaptcha_solver(API2, imgSRC).upper()
        print("solution = " + solution)
        return solution





    def getRecaptchaIformation(self, driver):
        result = driver.execute_script(
            ("const results=await "
                            "fetch(\"https://homeworkify.net/wp-admin/admin-ajax.php\", {\n"
                + "  \"headers\": {\n"
                + "    \"accept\": \"*/*\",\n"
                + "    \"accept-language\": \"en-US,en;q=0.9\",\n"
                + "    \"content-type\": \"application/x-www-form-urlencoded; charset=UTF-8\",\n"
                + "    \"sec-ch-ua\": \"\\\"Google Chrome\\\";v=\\\"107\\\", \\\"Chromium\\\";v=\\\"107\\\", \\\"Not=A?Brand\\\";v=\\\"24\\\"\",\n"
                + "    \"sec-ch-ua-mobile\": \"?0\",\n"
                + "    \"sec-ch-ua-platform\": \"\\\"Windows\\\"\",\n"
                + "    \"sec-fetch-dest\": \"empty\",\n"
                + "    \"sec-fetch-mode\": \"cors\",\n"
                + "    \"sec-fetch-site\": \"same-origin\",\n"
                + "    \"x-requested-with\": \"XMLHttpRequest\"\n"
                + "  },\n"
                + "  \"referrer\": \"https://homeworkify.net/\",\n"
                + "  \"referrerPolicy\": \"strict-origin-when-cross-origin\",\n"
                + "  \"body\": \"action=get_captcha_challenge\",\n"
                + "  \"method\": \"POST\",\n"
                + "  \"mode\": \"cors\",\n"
                + "  \"credentials\": \"include\"\n"
                + "});"
               "  let data = await results.json();"
               " return data;"));
        imgHTML = result.get('img')
        #print(imgHTML)
        soupObject=B(imgHTML)
        imgSrc=soupObject.img.attrs.get("src")[len("data:image/jpeg;base64,"):]
        captcha_id = result.get('captcha_id')
        captcha_session = result.get('captcha_session')
        time.sleep(1)
        return imgSrc, captcha_id, captcha_session



    def getQuestionInformation(self,driver,question_id):
        result = driver.execute_script(
            ("const results=await fetch(\"https://homeworkify.net/wp-admin/admin-ajax.php\", {\n"
            + "            \"headers\": {\n"
            + "                \"accept\": \"*/*\",\n"
            + "                \"accept-language\": \"en-US,en;q=0.9\",\n"
            + "                \"content-type\": \"application/x-www-form-urlencoded; charset=UTF-8\",\n"
            + "                \"sec-ch-ua\": \"\\\"Google Chrome\\\";v=\\\"107\\\", \\\"Chromium\\\";v=\\\"107\\\", \\\"Not=A?Brand\\\";v=\\\"24\\\"\",\n"
            + "                \"sec-ch-ua-mobile\": \"?0\",\n"
            + "                \"sec-ch-ua-platform\": \"\\\"macOS\\\"\",\n"
            + "                \"sec-fetch-dest\": \"empty\",\n"
            + "                \"sec-fetch-mode\": \"cors\",\n"
            + "                \"sec-fetch-site\": \"same-origin\",\n"
            + "                \"x-requested-with\": \"XMLHttpRequest\"\n"
            + "            },\n"
            + "            \"referrer\": \"https://homeworkify.net/\",\n"
            + "            \"referrerPolicy\": \"strict-origin-when-cross-origin\",\n"
            + "            \"body\": \"action=hwsearchmain&search=https%3A%2F%2Fwww.chegg.com%2Fhomework-help%2Fquestions-and-answers%2Fplanning-QUESTIONID\",\n"
            + "            \"method\": \"POST\",\n"
            + "            \"mode\": \"cors\",\n"
            + "            \"credentials\": \"include\"\n"
            + "        }).then((response) =>{ return response.json()}).catch((error) =>{return error;});  "
              " return results;").replace("QUESTIONID", question_id));
             # "  let data = await results.json();"

        if  result.get('data') is not None and "No solution found" in result.get('data'):

            return "Not Found Question","",""

        print(result)

        homework_id = result.get('id')
        endpoint = result.get('endpoint')
        sid = result.get('hash')
        time.sleep(1)
        return homework_id,endpoint,sid


