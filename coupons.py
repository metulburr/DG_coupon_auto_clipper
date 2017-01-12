#!/usr/bin/python env

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
import os
import sys
import argparse

HELP = '''
python2.x: this program loads a file in the same directory
in which loads an unlimited list of emails and passwords separated each account by a new line
and the email and password seperated by | character
example format is as the following:
email1@gmail.com|my_password
email2@yahoo.com|my_password
email3@yandex.com|my_password
#email4@yandex.com|my_password this line is ignored starting with #
email5@yandex.com|my_password'''

parser = argparse.ArgumentParser(description=HELP)
parser.add_argument('-b','--headless', action='store_true', default=False,
    help='Run in headless mode (in the background)')
parser.add_argument('-m','--multiply', type=int, default=1, 
    help='time delay multiplier in seconds for loading between web pages, default is 1, to double is 2, etc.')
parser.add_argument('-i','--input', default='coupons.txt',type=str,
    help='use this input file of accounts instead of the default coupons.txt')
parser.add_argument('-c','--chrome', default="/home/metulburr/chromedriver",type=str,
    help='custom chrome webdriver path')
parser.add_argument('-p','--phantom', default="/home/metulburr/phantomjs",type=str,
    help='custom phantomjs webdriver path for headless')
parser.add_argument('-s','--skip', action='store_true', default=False,
    help='skip over accounts with no coupons left to clip')
parser.add_argument('-f','--find', nargs=1,
    help='skip over accounts with no coupons left to clip')
args = vars(parser.parse_args())

#the file in which contains a list of emails and their passwords for logins
ACCOUNT_FILE = args['input']

#local path to the webdriver to run selenium
CHROMEPATH = args['chrome'] #chrome driver
PHANTOMPATH = args['phantom'] #headless driver

MULT = args['multiply'] #delay multiplier in seconds
RED='\033[0;31m'
GREEN='\033[1;32m'
NOCOLOR='\033[0m'
HEADLESS = args['headless'] #do in background
SKIP = args['skip']
    
def print_color(msg, color):
    '''print in color in terminal'''
    print('{}{}{}'.format(color, msg, NOCOLOR))

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
    print_color('clipped all coupons on {}'.format(username), GREEN)

def load_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except IOError:
        print_color('\nError: Failed loading {}'.format(filename),RED)
        print(HELP)
        sys.exit()
        
def print_coupon_info(browser):
    '''get coupons clipped/unclipped amount'''
    browser.get('https://dg.coupons.com/dashboard/')
    elements = browser.find_elements_by_xpath('.//span[@class="number"]')
    try:
        print('coupons clipped: {}'.format(elements[0].text))
        print('coupons available: {}'.format(elements[1].text))
        if SKIP:
            if not int(elements[1].text):
                return True
    except IndexError:
        pass

def execute():
    print('logging into {}'.format(username))
    try:
        if HEADLESS:
            browser = setup_headless()
        else:
            browser = setup()
        login(browser, username,password)

        time.sleep(3 * MULT) 
        #goes to dashboard page after login https://dg.coupons.com/dashboard/
        no_coupons_available = print_coupon_info(browser)
        if SKIP:
            if no_coupons_available:
                print_color('All coupons already clipped', GREEN)
                browser.quit()
                return
        #time.sleep(3000)
        browser.get('https://dg.coupons.com/coupons/')
        time.sleep(3 * MULT)
        
        

        count = make_all_btns_visable(browser)
        clip_all_btns(browser, count, username)
        print_coupon_info(browser)
        browser.quit()
    except WebDriverException: #clipping failed due to not logging in (this site appears to log in even if not)
        print_color('Failed to login to {}'.format(username), RED)


if __name__ == '__main__':
    lines = load_file(ACCOUNT_FILE)
    try:
        for line in lines:
            if not line.startswith('#'): #ignore commented out lines
                try: 
                    splits = line.split('|')
                    username = splits[0]
                    password = splits[1]
                    #phone = splits[2]
                except ValueError: #bypass blank lines
                    continue
                password = password.rstrip()
                execute()
    except KeyboardInterrupt:
        print()
        sys.exit()
    print('Done!')





