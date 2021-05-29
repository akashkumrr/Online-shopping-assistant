import pyrebase
from product_search import get_products

from datetime import date
from time import gmtime, strftime
from price_searcher import fetch_price
import smtplib
from email.mime.text import MIMEText
import time

config = {
	"apiKey": "AIzaSyDWtrzrhh5nW8FNWayTjQw5ZhYqzvuwGF0",
    "authDomain": "onlineshopping-b7b04.firebaseapp.com",
    "databaseURL": "https://onlineshopping-b7b04-default-rtdb.firebaseio.com",
    "projectId": "onlineshopping-b7b04",
    "storageBucket": "onlineshopping-b7b04.appspot.com",
    "messagingSenderId": "186126901403",
    "appId": "1:186126901403:web:b09ca9835c54d6975ce63e",
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


def total_products_in_notification_list():
	count_products_notification_list = 0
	users = db.get()


	if not users.val():
		print("nothing")

	else:
		for user in users.each():
			print(user.key())
			notification_db = db.child(user.key()).child('Notificationlist').get()

			
			if( not notification_db.val()):
				print("no Notificationlist")
				continue


			for product in notification_db.each():
				count_products_notification_list+=1


	return count_products_notification_list
				
def notifyUserByEmail(email_id, link):
    #content = ("Price Dropped! check out the link : "+link)

    msg = MIMEText(u'<a href='+link+'>Price Dropped!</a>','html')
    msg['Subject'] = 'subject'

    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('shoppingsystem2021','smartshoppersanyam')
    mail.sendmail('shoppingsystem2021@gmail.com',email_id,msg.as_string()) 
    mail.close()
    print("Sent mail for dropped price")


def scan_prices_and_notify(simulate_drop=False):

	print("\nBot has started scanning the prices for drop!")
	users = db.get()


	if not users.val():
		print("nothing")

	else:
		for user in users.each():
			print(user.key())
			notification_db = db.child(user.key()).child('Notificationlist').get()

			
			if( not notification_db.val()):
				print("no Notificationlist")
				continue

			db4 = db.child(user.key()).child('Email_address').get()
			for mail in db4.each():
				db5 = db.child(user.key()).child('Email_address').child(mail.key()).get()
				email_id = db5.val()['email']
			
			print(email_id)


			for product in notification_db.each():
				print("#")

				db3 = db.child(user.key()).child('Notificationlist').child(product.key()).get()
				

				#print(db3.key())
				#print(db3.val())
			
				site = db3.val()['website']					
				pdt_link = db3.val()['link']	
				pdt_title = db3.val()['product_title']
				pdt_threshold = db3.val()['threshold_price'] 	

				print("Getting the price of product : "+pdt_title)

				# calling the check price function, with website and link
				fetched_price = int(fetch_price(site,pdt_link)) 
				print("Fetched_price : ",fetched_price)
				print("Threshold_price : ",pdt_threshold)

				updated_stored_prices_list = db3.val()['checked_prices_list']
				last_stored_price_update = updated_stored_prices_list[-1]
				last_stored_price_update = last_stored_price_update['scanned_price']

				if(simulate_drop==True):
					fetched_price = int(pdt_threshold) - 1
					print("SIMULATED Fetched_price, (making it <Threshold_price)  : ",fetched_price)
					# knowingly reduce the feteched price( current price ) by 1 for simulating the price drop


				#add the price into checked_prices list, if there's any update in last fetched price
				if(int(fetched_price)!=int(last_stored_price_update)):
					price_status_dict ={}
					price_status_dict['date'] = strftime("%Y-%m-%d", gmtime())
					price_status_dict['time'] = strftime("%H:%M:%S", gmtime())
					price_status_dict['scanned_price'] = fetched_price
					# adding the fetched price in the stored price list in the database

					updated_stored_prices_list.append(price_status_dict)

					db.child(user.key()).child('Notificationlist').child(product.key()).update({"checked_prices_list":updated_stored_prices_list})			

				# notify customer ONLY IF fetched_price less than threshold of product
				# but this would alert user every time, whnever price if lower! 
				if(int(fetched_price)<int(pdt_threshold)):
					notifyUserByEmail(email_id,pdt_link)


#scan_prices_and_notify()