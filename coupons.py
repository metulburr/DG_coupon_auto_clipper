#!/usr/bin/python env

#http://selenium-python.readthedocs.io/locating-elements.html
from __future__ import print_function
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
import os
import sys
import argparse
import datetime
import codecs
START = datetime.datetime.now()

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
parser.add_argument('-a','--available', action='store_true', default=False,
    help='show available coupons not clipped, no clipping during process')
parser.add_argument('-u','--used', action='store_true', default=False,
    help='show used coupons')
parser.add_argument('-o','--output', default=None, 
    help='output to file')
parser.add_argument('-t','--top', type=int, 
    help='show top clipped coupons')
parser.add_argument('-m','--multiply', type=float, default=1, 
    help='time delay multiplier in seconds for loading between web pages, default is 1, to double is 2, .25 is a quarter of the speed, etc.')
parser.add_argument('-d','--delay', type=float, default=0, 
    help='delay for clipping coupons, an attempt to make sure all coupons are clipped before moving on to next account')
parser.add_argument('-i','--input', default='coupons.txt',type=str,
    help='use this input file of accounts instead of the default coupons.txt')
parser.add_argument('-c','--chrome', default="/home/metulburr/chromedriver",type=str,
    help='custom chrome webdriver path')
parser.add_argument('-p','--phantom', default="/home/metulburr/phantomjs",type=str,
    help='custom phantomjs webdriver path for headless')
parser.add_argument('-s','--skip', action='store_true', default=False,
    help='skip over accounts with no coupons left to clip. This is fast but can result in breakage')
parser.add_argument('-f','--find', nargs='*', default=None,
    help='search for coupon(s) if used or clipped. FIND can be any number of keywords to make hits')
args = vars(parser.parse_args())

#the file in which contains a list of emails and their passwords for logins
ACCOUNT_FILE = args['input']

#local path to the webdriver to run selenium
CHROMEPATH = args['chrome'] #chrome driver
PHANTOMPATH = args['phantom'] #headless driver

MULT = args['multiply'] #delay multiplier in seconds
RED='\033[0;31m'
GREEN='\033[1;32m'
INVERT='\033[1;3m'
NOCOLOR='\033[0m'
HEADLESS = args['headless'] #do in background
SKIP = args['skip']
SEARCH = args['find']
SEP = '-'*25
AVAIL = args['available']
TOP = args['top']
USED = args['used']
DELAY = args['delay']
OUTPUT = args ['output']

if OUTPUT:
    sys.stdout = codecs.open(OUTPUT,'w',encoding='utf8')
    
    
def print_color(msg, color):
    '''print in color in terminal'''
    s = '{}{}{}'.format(color, msg, NOCOLOR)
    print(s)

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
    print_color('logging into {}'.format(username), INVERT)
    try:
        if HEADLESS:
            browser = setup_headless()
        else:
            browser = setup()
        login(browser, username,password)

        time.sleep(3 * MULT) 
        if SEARCH: #only -f arg #no clipping coupons
            browser.get('https://dg.coupons.com/myCoupons/')
            time.sleep(1 * MULT) 
            
            
            coupons = browser.find_elements_by_xpath('.//div[@class="pod ci-grid activated desktop "]')
            for coupon in coupons:
                for search_str in SEARCH:
                    if search_str.lower() in coupon.text.lower():
                        print(coupon.text)
                        print(SEP)
        elif AVAIL: #show available coupons #no clipping coupons
            coupons = browser.find_elements_by_xpath('.//div[@class="pod ci-grid recommended desktop "]')
            if coupons:
                print('number of coupons available: {}'.format(len(coupons)))
                print(SEP)
            for coupon in coupons:
                print(coupon.text)
                print(SEP)
        elif TOP:#show top X coupons, used for showing lastest clipped
            browser.get('https://dg.coupons.com/myCoupons/')
            time.sleep(1 * MULT) 
            coupons = browser.find_elements_by_xpath('.//div[@class="pod ci-grid activated desktop "]')
            coupons = coupons[:TOP]
            for coupon in coupons:
                print(coupon.text)
                print(SEP)
        elif USED:#show used coupons
            browser.get('https://dg.coupons.com/myCoupons/')
            coupons = browser.find_elements_by_xpath('.//div[@class="pod ci-grid redeemed desktop "]')
            for coupon in coupons:
                print(coupon.text)
                print(SEP)
        else: #clip all coupons
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
            if DELAY:
                time.sleep(DELAY * MULT)
            print_coupon_info(browser)
            print(SEP)
            browser.quit()
    except WebDriverException: #clipping failed due to not logging in (this site appears to log in even if not)
        print_color('Failed to login to {}'.format(username), RED)
        
def get_time():
    now = datetime.datetime.now()
    elapsed_time = now - START
    t = divmod(elapsed_time.total_seconds(), 60)
    m,s = (int(t[0]), int(t[1]))
    return 'Took {} minutes and {} seconds'.format(m,s)
    
def format_time(datetime_now):
    return datetime_now.strftime("%b-%d-%Y %I:%M %p")


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
        sys.stdout.write("\r") #just remove the ^C for (cntrl + c)
        sys.stdout.flush()
        print_color('Program Aborted at {}'.format(format_time(datetime.datetime.now())), RED)
        sys.exit()
    print('Done!')
    print(get_time())
    print('Started at {}'.format(format_time(START)))
    print('Completed at {}'.format(format_time(datetime.datetime.now())))





