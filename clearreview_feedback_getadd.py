from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
import time
from selenium.webdriver.support.ui import Select
from http.server import HTTPServer, BaseHTTPRequestHandler
import simplejson

# requires pip simplejson, selenium and DesiredCapabilities

def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

def get_feedback():

    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'main-nav__link__feedback')))
    l.click();

    time.sleep(4)

    browser_log = driver.get_log('performance') 
    events = [process_browser_log_entry(entry) for entry in browser_log]
    events = [event for event in events if 'Network.response' in event['method'] and 'params' in event and 'response' in event['params'] and 'https://oneadvanced.clearreview.com/api/1.0/feedback/?recipient=' in event['params']['response']['url']]

    return driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': events[0]["params"]["requestId"]})

def add_feedback(f):
    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'main-nav__link__feedback')))
    l.click();
    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'feedback-list__give-feedback-button')))
    l.click();

    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'id_search_feedback_for_field')))
    l.send_keys(f['name'])
    time.sleep(1)
    l.send_keys(Keys.RETURN);
    
    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'give-feedback-form__positive-feedback__input')))
    l.send_keys('Hackathon2022: ' + f['pos'])
    
    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'give-feedback-form__constructive-feedback__input')))
    l.send_keys('Hackathon2022: ' + f['neg'])
    
    l = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, 'give-feedback-form__core-value__input')))
    l.click()
    l.send_keys(Keys.DOWN)
    l.send_keys(Keys.RETURN)
    
    l = driver.find_element_by_xpath('//*[@id="give-feedback-form"]/div[4]/button[1]')
    l.click()
    # send # browser

caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium") 
chrome_options.add_argument("--remote-debugging-port=9292")
driver = webdriver.Chrome(executable_path="./chromedriver.exe", options=chrome_options, desired_capabilities=caps)

driver.get('https://oneadvanced.clearreview.com/webapp/#/')

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        f = get_feedback()
        self.wfile.write(str(f['body']).encode("utf-8"))
        self.wfile.close()
        
    def do_POST(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        data = simplejson.loads(self.data_string)
        self.send_response(200)
        add_feedback(data)


server = HTTPServer(('', 8091), RequestHandler)
server.serve_forever()