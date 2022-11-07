import sys
import time

from repository.question_repository import QuestionRepository
from services.constants import HWifyURL, site_key_verify_human, API2
from util.anticaptcha.image_captcha_example import anticaptcha_solver
from util.browser_driver import BrowserDriver
from util.mysql_db_manager import MySqlDBManager
from bs4 import BeautifulSoup as B

from util.slack import Slack

question_repository = QuestionRepository()


class HW_Link_Generator_Consumer:

    def _start_crawling(self, process_id):
        driver = BrowserDriver().driver
        driver.get("https://creativeworks.lol/storytelling-number-one-skill-improve/")
        time.sleep(5)
        while True:
            # if "have permission to access this resource" not in driver.page_source:
            #     print("not found permision")
            #     time.sleep(2)
            #     continue

            mysql_db_manager = MySqlDBManager('admin',
                                              'QuizPlus123',
                                              'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                              'chegg_general_crawler',
                                              '3306')
            count = 0
            start = time.time()
            questions = question_repository.get_top_k_not_crawled_HW_URL(mysql_db_manager, process_id, 1000)
            mysql_db_manager.close_connection()
            if questions is None:
                print("No questions yet")
                Slack().send_message_to_slack("CONSUMER", "Consumer is waiting for questions from producer...")
                time.sleep(5)
                continue

            for question in questions:
                firstURL_Part = question.HW_answer_URL.partition("?")[0]
                restURL = question.HW_answer_URL.replace(firstURL_Part + "?", "")
                print(restURL)
                HTML_answer = self.fetch_answer_html(driver, question.HW_answer_URL, restURL)
                if "Enable JavaScript and cookies to continue" in HTML_answer:
                    driver.execute_script("location.reload(true);")
                    driver.get("https://creativeworks.lol/storytelling-number-one-skill-improve/")
                    time.sleep(5)
                    break
                print(HTML_answer)
                question_repository.update_question_by_answer_html(mysql_db_manager, question.id, HTML_answer)
                count += 1
                if count == 10:
                    end = time.time()
                    Slack().send_message_to_slack("CONSUMER", "10 answers added in: " + str(end - start) + " , we have  "
                                                  + str(question_repository.get_crawled_count(mysql_db_manager))
                                                  + "  answered questions and we have  "
                                                  + str(question_repository.get_produced_count(mysql_db_manager))
                                                  + "  questions produced waiting for answers")

                    count = 0
                    start = time.time()

    def fetch_answer_html(self, driver, URL, PART_URL):
        print(("const results=await "
               "fetch(\"https://creativeworks.lol/storytelling-number-one-skill-improve/\", {\n"
               + "  \"headers\": {\n"
               + "    \"accept\": \"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\",\n"
               + "    \"accept-language\": \"en-US,en;q=0.9\",\n"
               + "    \"cache-control\": \"max-age=0\",\n"
               + "    \"content-type\": \"application/x-www-form-urlencoded\",\n"
               + "    \"sec-ch-ua\": \"\\\"Google Chrome\\\";v=\\\"107\\\", \\\"Chromium\\\";v=\\\"107\\\", \\\"Not=A?Brand\\\";v=\\\"24\\\"\",\n"
               + "    \"sec-ch-ua-mobile\": \"?0\",\n"
               + "    \"sec-ch-ua-platform\": \"\\\"macOS\\\"\",\n"
               + "    \"sec-fetch-dest\": \"document\",\n"
               + "    \"sec-fetch-mode\": \"navigate\",\n"
               + "    \"sec-fetch-site\": \"same-origin\",\n"
               + "    \"upgrade-insecure-requests\": \"1\"\n"
               + "  },\n"
               + "  \"referrer\": \"FULL_URL\",\n"
               + "  \"referrerPolicy\": \"strict-origin-when-cross-origin\",\n"
               + "  \"body\": \"PART_URL\",\n"
               + "  \"method\": \"POST\",\n"
               + "  \"mode\": \"cors\",\n"
               + "  \"credentials\": \"include\"\n"
               + "});"
                 "  let data = await results.text();"
                 " return data;")
              .replace("FULL_URL", str(URL))
              .replace("PART_URL", str(PART_URL)))
        result = driver.execute_script(
            ("const results=await "
             "fetch(\"https://creativeworks.lol/storytelling-number-one-skill-improve/\", {\n"
             + "  \"headers\": {\n"
             + "    \"accept\": \"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\",\n"
             + "    \"accept-language\": \"en-US,en;q=0.9\",\n"
             + "    \"cache-control\": \"max-age=0\",\n"
             + "    \"content-type\": \"application/x-www-form-urlencoded\",\n"
             + "    \"sec-ch-ua\": \"\\\"Google Chrome\\\";v=\\\"107\\\", \\\"Chromium\\\";v=\\\"107\\\", \\\"Not=A?Brand\\\";v=\\\"24\\\"\",\n"
             + "    \"sec-ch-ua-mobile\": \"?0\",\n"
             + "    \"sec-ch-ua-platform\": \"\\\"macOS\\\"\",\n"
             + "    \"sec-fetch-dest\": \"document\",\n"
             + "    \"sec-fetch-mode\": \"navigate\",\n"
             + "    \"sec-fetch-site\": \"same-origin\",\n"
             + "    \"upgrade-insecure-requests\": \"1\"\n"
             + "  },\n"
             + "  \"referrer\": \"FULL_URL\",\n"
             + "  \"referrerPolicy\": \"strict-origin-when-cross-origin\",\n"
             + "  \"body\": \"PART_URL\",\n"
             + "  \"method\": \"POST\",\n"
             + "  \"mode\": \"cors\",\n"
             + "  \"credentials\": \"include\"\n"
             + "});"
               "  let data = await results.text();"
               " return data;")
                .replace("FULL_URL", str(URL))
                .replace("PART_URL", str(PART_URL)));

        return result
