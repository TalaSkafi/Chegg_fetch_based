import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from repository.question_repository import QuestionRepository
from services.constants import HWifyURL, site_key_verify_human, API2
from util.anticaptcha.anycaptcha_solver import demo_imagetotext
from util.anticaptcha.image_captcha_example import anticaptcha_solver
from util.browser_driver import BrowserDriver
from util.hcaptcha_solver import hcaptcha_solver
from util.img_downloader import store_img
from util.mysql_db_manager import MySqlDBManager
from util.normal_captcha_solver import normal_captcha_solver

question_repository = QuestionRepository()
mysql_db_manager = MySqlDBManager('admin',
                                  'QuizPlus123',
                                  'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                  'chegg_general_crawler',
                                  '3306')


class HWifyCrawler:

    def _start_crawling(self,process_id):
        #
        question_repository.set_process_id(process_id)
        driver = BrowserDriver().driver
        while True:
            questions = question_repository.get_first_not_answer_retrived_k_questions(mysql_db_manager, 1000)
            try:
                for question in questions:
                    self.retrieve_answer(question, driver)
            except Exception as e:
                print(str(e))


    def retrieve_answer(self, question, driver):

        flag = 0
        Qflag = 0
        count=0
        try:
            driver.get(HWifyURL)
        except:
            sys.exit(-1)

        while count<4:
            try :
                driver.execute_script("location.reload(true);")
                wait = WebDriverWait(driver, 20)
                element = wait.until(EC.visibility_of_element_located((By.ID, 'hw-header-input')))
                element.send_keys(question.url)
                print(question.url)
                wait = WebDriverWait(driver, 20)
                element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'hw-header-button')))
                element.click()
                wait = WebDriverWait(driver, 5)
                element = wait.until(EC.visibility_of_element_located((By.XPATH,
                                                                       '//*[@id="et-boc"]/div/div/div[1]/div[2]/div/div[1]/div/div[2]/div/h2')))

                Qflag=1
                break
            except Exception as e:
                driver.execute_script("location.reload(true);")
                count += 1
        if Qflag==1:
            try:
                status = element.text
                if status == 'We have solution for your question!':  # there is an answer, so we open it and store it
                    question_repository.set_has_answer(mysql_db_manager, question)
                    count = 1
                    while count < 4:
                        self._normal_captcha_solve(driver,question)
                        try:
                            wait = WebDriverWait(driver, 4)
                            element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'complete')))
                            flag = 0
                            break

                        except Exception as e:
                            count += 1
                            if count == 4:
                                flag = 1
                            print("wrong solution")
                            driver.find_element(By.ID, 'cp-user-input').clear()
                            #sys.exit()

                    if flag == 0:  # it means I have the right solution, and I want to complete
                        try:
                            wait = WebDriverWait(driver, 10)
                            element = wait.until(EC.element_to_be_clickable((By.ID, 'view-solution')))
                            element.click()

                        except Exception as e:
                            try:
                                wait = WebDriverWait(driver, 10)
                                element = wait.until(EC.element_to_be_clickable((By.ID, 'x-view-solution')))
                                element.click()

                            except Exception as e:
                                print("Can't open solution")
                                question_repository.set_error(mysql_db_manager, question, "Can not open solution")
                                flag = 1

                        if flag == 0:
                            wait = WebDriverWait(driver, 20)
                            element = wait.until(EC.invisibility_of_element((By.ID, 'view-solution')))
                            element = wait.until(EC.invisibility_of_element((By.ID, 'x-view-solution')))
                            time.sleep(.3)
                            get_url = driver.current_url
                            time.sleep(.3)
                            if get_url.find("creativeworks") == -1:
                                print("something wrong!!")
                                time.sleep(120)
                                question_repository.set_error(mysql_db_manager, question, "something wrong")
                            else:
                                while True:
                                    try:
                                        self._store_answer(driver, question)
                                        break

                                    except Exception as e:
                                        print(
                                            "can't reach answer for some reason, if it's not verify page, it will be Adv")
                                        # print(str(e))
                                        time.sleep(.5)
                                        get_url = driver.current_url
                                        if get_url.find("creativeworks") == -1:
                                            print("it is Adv")
                                            question_repository.set_error(mysql_db_manager, question, "it is Adv")
                                            break
                                        else:
                                            try:
                                                if driver.find_element(By.ID, 'challenge-running'):
                                                    self._verify_human(driver)

                                            except Exception as e:  # if we are here, it means that we didn't face the page of verify human
                                                if driver.find_element(By.XPATH, '/html/body/h1').text == 'Forbidden':
                                                    print("Forbidden page")
                                                    break
                                                print("try")


                elif status == 'No solution found!':
                    # there is no solution
                    try:
                        question_repository.set_no_answer(mysql_db_manager, question)
                        print("there is No solution")
                    except Exception as e:
                        print(str(e))


            except Exception as e:
                print("there is an Error")
                print(str(e))
                try:
                    question_repository.set_error(mysql_db_manager, question, str(e))
                except Exception as e:
                    print(str(e))


    def _hcaptcha_solve(self, driver):
        try:
            # src = driver.find_element(By.TAG_NAME, 'iframe').get_attribute("src")
            # site_key = src.split("sitekey=")[1].split("&")[0]
            solution_code = hcaptcha_solver(site_key_verify_human, HWifyURL)
            print(solution_code)
            element = driver.find_element(By.TAG_NAME, 'iframe')
            time.sleep(1)
            driver.execute_script("arguments[0].setAttribute('data-hcaptcha-response',arguments[1])", element,
                                  solution_code)
            time.sleep(.5)
        except Exception as e:
            print(str(e))

    def _normal_captcha_solve(self, driver,question):
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'captcha-loader')))
        element.click()
        time.sleep(.3)
        src = driver.find_element(By.ID, 'captcha_challenge_img').get_attribute("src")
        # id=src[1100:1140]
        # store_img(src,id)
        src=src[23:]
        try:
            # solution=demo_imagetotext(src).upper()
            solution = anticaptcha_solver(API2,src).upper()
            print("solution = " + solution)
            element = driver.find_element(By.ID, 'cp-user-input')
            element.send_keys(solution)
            wait = WebDriverWait(driver, 5)
            element = wait.until(EC.element_to_be_clickable((By.ID, 'verify-captcha')))
            element.click()
        except Exception as e:
            question_repository.set_error(mysql_db_manager,question,"can not solve recaptcha")
            print(str(e))

    def _store_answer(self, driver, question):
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'q-a')))
        answer = element.get_attribute('innerHTML')
        print(answer)
        try:
            question_repository.set_answer(mysql_db_manager, question, answer)

        except Exception as e:
            print(str(e))

    def _verify_human(self, driver):
        count = 0
        while count < 15:
            try:
                wait = WebDriverWait(driver, 6)
                element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'big-button')))
                time.sleep(.5)
                element.click()
                break

            except Exception as e:
                driver.refresh()
                count += 1
                print("Not a button")

