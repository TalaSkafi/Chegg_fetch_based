import time
from random import randrange
from selenium import webdriver
import undetected_chromedriver as uc


class BrowserDriver:
    def __init__(self):
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        driver = uc.Chrome()
        # driver = webdriver.Chrome(executable_path=r"/Users/mahdiwashha/Desktop/Chegg_QA_Crawler/chromedriver1")

        time.sleep(randrange(1, 3))
        return driver

    def new_window(self):
        options = uc.ChromeOptions()
        options.add_argument("start-maximized")
        driver = uc.Chrome(options=options, version_main=106)
        return driver

    def close_driver(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.close()
