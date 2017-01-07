#!/usr/bin/python env

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
import os
import sys

#the file in which contains a list of emails and their passwords for logins
ACCOUNT_FILE = 'coupons.txt' 

#local path to the webdriver to run selenium
CHROMEPATH = "/home/metulburr/chromedriver" #chrome driver
PHANTOMPATH = '/home/metulburr/phantomjs' #headless driver

MULT = 1 #delay multiplier in seconds
RED='\033[0;31m'
GREEN='\033[1;32m'
NOCOLOR='\033[0m'
HEADLESS = False #do in background

HELP = '''
python2.x: this program loads a file in the same directory named {}
in which loads an unlimited list of emails and passwords separated each account by a new line
and the email and password seperated by | character
example format is as the following:
email1@gmail.com|my_password
email2@yahoo.com|my_password
email3@yandex.com|my_password
#email4@yandex.com|my_password this line is ignored starting with #
email5@yandex.com|my_password'''.format(ACCOUNT_FILE)

def setup():
    '''
    setup webdriver and create browser with Chrome
    '''
    #https://chromedriver.storage.googleapis.com/index.html
    #https://chromedriver.storage.googleapis.com/index.html?path=2.25/ ##latest
    chromedriver = CHROMEPATH
    os.environ["webdriver.chrome.driver"] = CHROMEPATH
    browser = webdriver.Chrome(chromedriver)
    browser.set_window_position(0,0)
    return browser
    
def setup_headless():
    '''
    setup webdriver and create browser via headless
    '''
    #http://phantomjs.org/download.html
    browser = webdriver.PhantomJS(PHANTOMPATH)
    return browser

def login(browser, u, p):
    '''
    login to account
    '''
    browser.get("https://dg.coupons.com/signin/") 
    time.sleep(1 * MULT) 
    username = browser.find_element_by_id("email")
    password = browser.find_element_by_id("password")
    username.send_keys(u)
    password.send_keys(p)
    login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
    login_attempt.submit()
    
def check_login_success(source, browser):
    '''not working, commented out'''
    output = browser.execute_script("document.getElementsByClassName('forgot-password-link')[0].click()")
    print(output)
    #print('Failed to login, will plan to bypass')
    #time.sleep(300)
    
def get_btns(browser):
    '''
    return a list of buttons from span tag class name to add coupon
    '''
    return browser.find_elements_by_class_name('add-text')

def make_all_btns_visable(browser):
    '''
    another anti-bot hurdle
    show all buttons by scrolling down
    otherwise they do not show all coupons
    '''
    count = 0
    for _ in range(100):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1 * MULT)
        #browser.FindElement(By.XPath("//div[@class='pod ci-grid recommended desktop ']//div[@class='media']//div[@class='media-body']//div[@class='badge']//span[@class='add-text']")).Click()
        clip_btns = get_btns(browser)
        #print('Scrolling {} buttons into view'.format(len(clip_btns)))
        sys.stdout.write("\rScrolling {} coupons into view".format(len(clip_btns)))
        sys.stdout.flush()
        if count >= len(clip_btns): #if count bypasses then we are at the bottom of the page, stop scrolling
            break
        else:
            count = len(clip_btns)
    print()
    return len(clip_btns)

def clip_all_btns(browser, number_of_coupons, username):
    '''
    clip ALL available coupons
    '''
    browser.execute_script("document.getElementsByClassName('badge')[0].click()")
    time.sleep(2 * MULT) #allow time to load javascript of checkbox (first click only)
    browser.execute_script("document.getElementsByClassName('close-btn')[0].click()")
    for i in range(number_of_coupons): #now we are verified, clip all coupons
        browser.execute_script("document.getElementsByClassName('badge')[{}].click()".format(i))
    print('{}clipped all coupons on {}{}'.format(GREEN, username, NOCOLOR))

def load_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError:
        print('\n{}Error: Failed loading {}{}'.format(RED, filename, NOCOLOR))
        print(HELP)
        sys.exit()

def execute():
    print('logging into {}'.format(username))
    try:
        if HEADLESS:
            browser = setup_headless()
        else:
            browser = setup()
        login(browser, username,password)

        time.sleep(3 * MULT) 
        browser.get('https://dg.coupons.com/coupons/')
        time.sleep(3 * MULT)

        count = make_all_btns_visable(browser)
        clip_all_btns(browser, count, username)
        browser.quit()
    except WebDriverException: #clipping failed due to not logging in (this site appears to log in even if not)
        print('{}Failed login to {}{}'.format(RED, username, NOCOLOR))


if __name__ == '__main__':
    lines = load_file(ACCOUNT_FILE)
    try:
        for line in lines:
            if not line.startswith('#'): #ignore commented out lines
                try: 
                    username, password = line.split('|')
                except ValueError: #bypass blank lines
                    continue
                password = password.rstrip()
                execute()
    except KeyboardInterrupt:
        print()
        sys.exit()
    print('Done!')


