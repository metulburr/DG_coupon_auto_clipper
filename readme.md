###what does it do
This program logs into all your Dollar General accounts and auto clips all digital coupons to be added to your account. 

###how to run
this program requires a little modification (currently) to run on different users computers

1) You need to install python2.x to run the source code
https://www.python.org/

2) You need to install selenium, a 3rd party library of python
https://pypi.python.org/pypi/selenium

3) You need to download the webdriver 
Chrome: You need to install chrome as well as download their webdriver at
https://chromedriver.storage.googleapis.com/index.html
PhantomJS: This is a headless version doing it in the background instead, the driver is at
http://phantomjs.org/download.html

~~
4-A)The source code needs to be changed to accomodate changes:
Change the path to the path on your computer where you chrome webdriver resides
https://github.com/metulburr/DG_coupon_auto_clipper/blob/master/coupons.py#L13
same with phantomjs below that to the proper path to that webdriver if using headless
~~
Now just give the argument -c {PATH} for chrome and -p {PATH} for phantom

4-B)The list of accounts needs to be changed to your true DG accounts|passwords shown in the format of this example in that name. The file needs to reside in the same directory as the source code, with that filename. 
https://github.com/metulburr/DG_coupon_auto_clipper/blob/master/coupons.txt

5) execution:
open a command prompt/terminal and execute
```
python coupons.py
```
where python is your python executable and coupons.py is the location of the file.

EXAMPLE:
```
metulburr@ubuntu:~$ python coupons.py 
logging into BLEEP@BLEEP.com
Scrolling 261 coupons into view()
clipped all coupons on BLEEP@BLEEP.com
logging into BLEEP2@BLEEP.com
Scrolling 261 coupons into view()
clipped all coupons on BLEEP2@BLEEP.com
logging into BLEEP3@BLEEP.com
Scrolling 261 coupons into view()
clipped all coupons on BLEEP3@BLEEP.com

```

###arguments
```
metulburr@ubuntu:~$ python coupons.py -h
usage: coupons.py [-h] [-b] [-m MULTIPLY] [-i INPUT] [-c CHROME] [-p PHANTOM]
                  [-s] [-f [FIND [FIND ...]]]

python2.x: this program loads a file in the same directory in which loads an
unlimited list of emails and passwords separated each account by a new line
and the email and password seperated by | character example format is as the
following: email1@gmail.com|my_password email2@yahoo.com|my_password
email3@yandex.com|my_password #email4@yandex.com|my_password this line is
ignored starting with # email5@yandex.com|my_password

optional arguments:
  -h, --help            show this help message and exit
  -b, --headless        Run in headless mode (in the background)
  -m MULTIPLY, --multiply MULTIPLY
                        time delay multiplier in seconds for loading between
                        web pages, default is 1, to double is 2, etc.
  -i INPUT, --input INPUT
                        use this input file of accounts instead of the default
                        coupons.txt
  -c CHROME, --chrome CHROME
                        custom chrome webdriver path
  -p PHANTOM, --phantom PHANTOM
                        custom phantomjs webdriver path for headless
  -s, --skip            skip over accounts with no coupons left to clip. This
                        is fast but can result in breakage
  -f [FIND [FIND ...]], --find [FIND [FIND ...]]
                        search for coupon(s) if used or clipped. FIND can be
                        any number of keywords to make hits

```

###base requirements
python2.x
selenium
webdrivers for either chrome or phantomJS
a little modification to the files

###future plans
No future modifications currently planned as this is a personal script. The more people that use it and disperse it the more they change their code to break this script. Of course i will try to mod it each time they change their HTML. 




