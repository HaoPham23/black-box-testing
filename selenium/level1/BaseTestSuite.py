from selenium import webdriver
import json

class BaseTestSuite():
    def __init__(self, data_path):
        self.first_run = True
        self.read_data(data_path)

    def read_data(self, data_path):
        self.data = None
        try:
            with open(data_path, encoding='UTF-8') as f:
                self.data = json.load(f)
        except Exception as e:
            print(e)
            
    def setup_method(self, method):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.vars = {}
    
    def teardown_method(self, method):
        self.driver.quit()