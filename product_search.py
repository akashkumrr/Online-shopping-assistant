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


def snapdeal(product_dict, product_name, headers):

	print("\nSearching in snapdeal")
	URL = "https://www.snapdeal.com/search?noOfResults=20&keyword="+product_name
	website = 'snapdeal'

	# sending the get request
	try:
		webpage = requests.get(URL, headers=headers) 
	except Exception as e:
		print('Could not load the webpage', e)
		return product_dict

	soup = BeautifulSoup(webpage.content, "lxml")

	# fetching all the product attributes
	title = soup.find_all("p", attrs={"class": 'product-title'})
	price = soup.find_all("span", {"class" : 'lfloat product-price'})
	image_src = soup.find_all("img", {"class" : 'product-image', "src":True})
	hyperlink = soup.find_all("div", {"class" : 'product-desc-rating'})
	
	# incase no product is found / invalid product name
	if not title:                       
		print('No product found on snapdeal! try again')
		return product_dict

	# defining the lists to be added in the dictionary
	product_names = []
	product_prices = []
	image_url = []
	product_url = []

	# iterating through loops to all the product values
	for product in title:
		product_names.append(product.get_text())

	for product in price:
		product_prices.append(product['data-price'])

	for image in image_src:
		image_url.append(image['src'])

	for tag in hyperlink:
		url = tag.find('a',{'class':'dp-widget-link'})
		product_url.append(url['href'])

	# defining the numer of products to be added to the dict
	iterator = min(4, len(product_names))

	for i in range(iterator):

		product_title = product_names[i]
		product_price = trim_currency_symbol(product_prices[i])
		product_image = image_url[i]
		product_src = product_url[i]

		# adding into the dictionary
		product_dict['title'].append(product_title)
		product_dict['price'].append(product_price)
		product_dict['url'].append(product_image)
		product_dict['hyperlink'].append(product_src)
		product_dict['website'].append(website)

		print('Title :' , product_title)
		print('Price :', product_price)
		# print('Image url :', product_image)
		# print('Product url :', product_src)

	return product_dict


def amazon(product_dict, product_name, headers):

	print("\nSearching in amazon")
	URL ='https://www.amazon.in/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords='+product_name
	website = 'amazon'

	# sending the get request
	try:
		webpage = requests.get(URL, headers=headers)
	except Exception as e:
		print('Could not load the webpage', e)
		return product_dict

	soup = BeautifulSoup(webpage.text,'html.parser') 

	# fetching all the product attributes
	title = soup.find_all('a',class_='a-link-normal a-text-normal') 
	price = soup.find_all('span',class_='a-price-whole') 
	image_src = soup.find_all('img',class_='s-image')
	hyperlink = soup.find_all('a',class_='a-link-normal s-no-outline')

	# incase no product is found / invalid product name
	if not title:                   
		print('No product found on amazon! try again')
		return product_dict

	# defining the lists to be added in the dictionary
	product_names = []
	product_prices = []
	image_url = []
	product_url = []

	for image in image_src:
		image_url.append(image['src'])

	base_product_url = 'https://www.amazon.in/'
	for product in hyperlink:
		product_url.append(base_product_url+product['href'])

	# defining the numer of products to be added to the dict
	iterator = min(4, len(image_url))
	
	for i in range(iterator):

		# string contains newline character('\n') at ends. REMOVING IT
		product_title = title[i].getText() 
		product_title = product_title.strip('\n')   
		product_price = price[i].getText()
		product_price = trim_currency_symbol(product_price.strip('\n'))
		product_image = image_url[i]
		product_src = product_url[i]

		# adding into the dictionary
		product_dict['title'].append(product_title)
		product_dict['price'].append(product_price)
		product_dict['url'].append(product_image)
		product_dict['hyperlink'].append(product_src)
		product_dict['website'].append(website)

		print('Title :' , product_title)
		print('Price :', product_price)
		# print('Image url :', product_image)
		# print('Product url :', product_src)

	return product_dict


def shopclues(product_dict, product_name, headers):

	print('\nSearching in shopclues')
	product_name = product_name.replace(" ", "%20")
	URL  ='https://www.shopclues.com/search?q='+ product_name +'&sc_z=4444&z=0&count=9&user_id=&user_segment=default'
	website = 'shopclues'
	
	# sending the get request
	try:
		webpage = requests.get(URL, headers=headers) 
	except Exception as e:
		print('could not load web page')
		return product_dict
	
	soup = BeautifulSoup(webpage.content, "lxml")

	# Request product columns
	containers=soup.find_all("div",{"class":"column col3 search_blocks"})
   
	counter = 0
	for container in containers:

		# getting title of product
		title=container.find("h2").get_text()
		product_dict['title'].append(title)
		print("Title :", title)

		# getting price of product
		price=container.find("span",{'class':'p_price'}).get_text()

		# there's comma in the price string, remove it and then convert it into string
		price = int(trim_currency_symbol(price[1:]))
		product_dict['price'].append(price)
		print("Price :", price)

		# getting image of product
		image_src = container.find("img")['src']
		product_dict['url'].append(image_src)
		# print("Image url :", image_src)

		# getting link of product
		hyperlink = "https:"+container.find('a')['href']
		product_dict['hyperlink'].append(hyperlink)
		# print("Product url :", hyperlink)

		product_dict['website'].append(website)
		
		# For getting top 2 best search
		counter += 1;
		if counter == 4:
			break
	
	# Checking if any product was found
	if counter == 0:
		print("No product found in shopclues! try again")
		return product_dict

	return product_dict


def flipkart(product_dict, product_name):

	# For headless
	print('\nSearching in flipkart')
	options = Options()
	options.headless = True 
	URL = "https://www.flipkart.com/search?q="+product_name+"&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off"
	website = 'flipkart'

	# for Turning of warnings in console selenium INFO:CONSOLE off
	options.add_experimental_option('excludeSwitches', ['enable-logging'])  

	# Selenium driver here
	driveradress = "F:/#Coding Projects/OnlineShopping v1.2/SanyamFinalProject/FinalProject/chromedriver"
	#driveradress = "/usr/bin/chromedriver"

	driver = webdriver.Chrome(executable_path = driveradress, options = options)
	#driver = webdriver.Chrome(options = options)
	driver.get(URL)

	try:
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[(@class='s1Q9rs') or (@class='_4rR01T') or (@class='IRpwTa')]")))
		
		# the usual items
		name = driver.find_elements_by_class_name("s1Q9rs")
		price = driver.find_elements_by_class_name("_30jeq3")
		imgs = driver.find_elements_by_class_name('_396cs4._3exPp9')
		hyperlinks = driver.find_elements_by_xpath("//a[@class = 's1Q9rs']")

		# laptops,tablet and other related items with horizontal description included
		lap_name = driver.find_elements_by_class_name("_4rR01T")
		lap_price = driver.find_elements_by_xpath("//*[@class='_25b18c']/div[@class='_30jeq3 _1_WHN1']")
		lap_imgs = driver.find_elements_by_class_name('_396cs4._3exPp9')
		lap_hyperlinks = driver.find_elements_by_xpath("//*[@class='_1fQZEK']")

		# t-shirts,jeans and related items with cards like display
		jeans_name = driver.find_elements_by_xpath("//*[@class='IRpwTa']")
		jeans_price = driver.find_elements_by_xpath("//*[@class='_25b18c']/div[@class='_30jeq3']")
		jeans_imgs = driver.find_elements_by_class_name('_2r_T1I')
		jeans_hyperlinks = driver.find_elements_by_xpath("//*[@class='IRpwTa']")

		# in case no product is found / invalid product name
		if ( not name and not lap_name and not jeans_name):
			print("No product found on flipkart! try again")
			return product_dict

		# iterating through all product values
		if len(name) != 0:
			iterator = min(4,len(name))
			for i in range(iterator):                
				print("Title :", name[i].get_attribute("title"))
				print("Price :", trim_currency_symbol(price[i].text))
				# print("Image url :",  imgs[i].get_attribute('src'))
				# print("Product url :", hyperlinks[i].get_attribute('href'))

				product_dict['title'].append(name[i].get_attribute("title"))
				product_dict['price'].append(trim_currency_symbol(price[i].text))
				product_dict['url'].append(imgs[i].get_attribute('src'))
				product_dict['hyperlink'].append(hyperlinks[i].get_attribute('href'))
				product_dict['website'].append(website)

		if len(lap_name) != 0:
			iterator = min(4,len(lap_name))
			for i in range(iterator):
				print("Title :", lap_name[i].text)
				print("Price :", trim_currency_symbol(lap_price[i].text))
				# print("Image url :", lap_imgs[i].get_attribute('src'))
				# print("Product url :", lap_hyperlinks[i].get_attribute('href'))

				product_dict['title'].append(lap_name[i].text)
				product_dict['price'].append(trim_currency_symbol(lap_price[i].text))
				product_dict['url'].append(lap_imgs[i].get_attribute('src'))
				product_dict['hyperlink'].append(lap_hyperlinks[i].get_attribute('href'))
				product_dict['website'].append(website)

		if len(jeans_name) != 0:
			iterator = min(4,len(jeans_name))           
			for i in range(iterator):
				print("Title :", jeans_name[i].get_attribute("title"))
				print("Price :", trim_currency_symbol(jeans_price[i].text))
				# print("Image url :", jeans_imgs[i].get_attribute('src'))           
				# print("Product url :", jeans_hyperlinks[i].get_attribute('href'))

				product_dict['title'].append(jeans_name[i].get_attribute("title"))
				product_dict['price'].append(trim_currency_symbol(jeans_price[i].text))
				product_dict['url'].append(jeans_imgs[i].get_attribute('src'))
				product_dict['hyperlink'].append(jeans_hyperlinks[i].get_attribute('href'))
				product_dict['website'].append(website)

	except Exception as mainException:
		print("Exception main : "+str(mainException))
		print("Something went wrong captain O_x .......")

	return product_dict

def get_accuracy(product_dict, search_query):

	product_dict['accuracy'] = []
	search_query = search_query.lower()

	words = search_query.split(' ')
	number_of_words = len(words)

	products_final = []
	for product in product_dict['title']:
		products_final.append(product.lower())

	for product in products_final:
		counter = 0
		for word in words:
			if word in product:
				counter+=1
		product_dict['accuracy'].append(counter/number_of_words)
			
	return product_dict

def get_products(product_name): 

	# defining dictionary to store values which is returned and passed to every function
	product_dict = {}
	product_dict['title'] = []
	product_dict['price'] = []
	product_dict['url'] = []
	product_dict['hyperlink'] = []
	product_dict['website'] = []

	# defining header for bs4
	HEADERS = ({'User-Agent':
				'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
				'Accept-Language': 'en-US, en;q=0.5'})

	product_dict = amazon(product_dict, product_name, HEADERS)
	product_dict = flipkart(product_dict, product_name)
	product_dict = shopclues(product_dict, product_name, HEADERS)
	product_dict = snapdeal(product_dict, product_name, HEADERS)
	product_dict = get_accuracy(product_dict, product_name)

	return product_dict

