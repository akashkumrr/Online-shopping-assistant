import requests
from bs4 import BeautifulSoup
import time
import re
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def trim_currency_symbol(price):    
	trim = re.compile(r'[^\d.]+')   
	result = trim.sub('', price)
	result2 = re.findall("\d+",result)[0]
	return result2


def price_snapdeal(product_url, headers):

	print("\nSearching in snapdeal")
	URL = product_url
	
	# sending the get request
	try:
		webpage = requests.get(URL, headers=headers) 
	except Exception as e:
		print('Could not load the webpage', e)
		return 'ERROR... '

	soup = BeautifulSoup(webpage.content, "lxml")
	price = soup.find("span", {"class" : 'payBlkBig'}).get_text()

	return price

def price_shopclues(product_url, headers):

	print('\nSearching in shopclues')
	
	URL  =product_url
	# sending the get request
	try:
		webpage = requests.get(URL, headers=headers) 
	except Exception as e:
		print('could not load web page')
		return "ERROR"
	
	soup = BeautifulSoup(webpage.content, "lxml")
	price=soup.find("span",{'class':'f_price'}).get_text()

	price = int(trim_currency_symbol(price))

	return price


def price_amazon(product_url, headers):

	print("\nSearching in amazon")
	
	options = Options()
	options.headless = True 
	URL =product_url
	# for Turning of warnings in console selenium INFO:CONSOLE off
	options.add_experimental_option('excludeSwitches', ['enable-logging'])  

	# Selenium driver here
	driveradress = "F:/#Coding Projects/OnlineShopping v1.2/Online_Shopping/chromedriver"
	driver = webdriver.Chrome(executable_path = driveradress, options = options)
	driver.get(URL)

	html =  driver.page_source

	soup = BeautifulSoup(html,'html.parser') 
	price_element1 = soup.find('span',{'id':'priceblock_dealprice'})
	price_element2 = soup.find('span',{'id':'priceblock_ourprice'})
	if(price_element1==None):
		price = price_element2.get_text()
	else:
		price = price_element1.get_text()
	
	product_price = trim_currency_symbol(price)	
	
	driver.close()
	return product_price

def price_flipkart(product_url):


	options = Options()
	options.headless = True 
	URL =product_url
	# for Turning of warnings in console selenium INFO:CONSOLE off
	options.add_experimental_option('excludeSwitches', ['enable-logging'])  

	# Selenium driver here
	driveradress = "F:/#Coding Projects/OnlineShopping v1.2/Online_Shopping/chromedriver"
	driver = webdriver.Chrome(executable_path = driveradress, options = options)
	driver.get(URL)

	html =  driver.page_source

	print("\nSearching in flipkart")


	soup = BeautifulSoup(html,'lxml') 
	price = soup.find('div',{'class':'_30jeq3 _16Jk6d'}).get_text()
	
	product_price = trim_currency_symbol(price)	

	driver.close()

	return product_price


def fetch_price(website_name,link):

	HEADERS = ({'User-Agent':
				'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
				'Accept-Language': 'en-US, en;q=0.5'})


	if(website_name=="flipkart"):
		return price_flipkart(link)
	if(website_name=="amazon"):
		return price_amazon(link,HEADERS)
	if(website_name=="snapdeal"):
		return price_snapdeal(link,HEADERS)
	if(website_name=="shopclues"):
		return price_shopclues(link,HEADERS)	


#fetch_price('amazon',"https://www.amazon.in//Omega-Watches-John-Goldberger/dp/888943127X/ref=sr_1_3?dchild=1&keywords=omega+watch&qid=1621487343&sr=8-3")