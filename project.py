import pyrebase
from product_search import get_products
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
from time import gmtime, strftime
app = Flask(__name__)
app.config['SECRET_KEY'] = '\x8f{1O\x00\x0b\x17\xda\xfd\xf1\x8d\xf4\xe5A\xbb\xa2(|\xfb\x93q\xcf\x0fb'
user_table_name = ''

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

#*************************************CHATBOT**************************************************
#Imports
import nltk
from nltk.stem.lancaster import LancasterStemmer

import numpy as np
import tflearn
import tensorflow as tf
from tensorflow.python.framework import ops

import random
import json
import pickle

from flask import Flask, redirect, url_for, request, render_template

stemmer = LancasterStemmer()
ignore = ['?','.','&','!']  

#Loading Data
with open("intents.json") as file:
    data = json.load(file)
  
try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
        
except:
     #Initializing empty lists
    words = []
    labels = []
    docs_x = []
    docs_y = []

    #Looping through our data
    for intent in data['intents']:
        for pattern in intent['patterns']:
            pattern = pattern.lower()
            #Creating a list of words
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])
    
        if intent['tag'] not in labels:
            labels.append(intent['tag'])
  
    words = [stemmer.stem(w.lower()) for w in words if w not in ignore]
    words = sorted(list(set(words)))
    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]
    for x,doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        training.append(bag)
        output.append(output_row)
    
    #Converting training data into NumPy arrays
    training = np.array(training)
    output = np.array(output)

    #Saving data to disk
    with open("data.pickle","wb") as f:
        pickle.dump((words, labels, training, output),f)
 
try:
    net = tflearn.input_data(shape = [None, len(training[0])])
    net = tflearn.fully_connected(net,8)
    net = tflearn.fully_connected(net,8)
    net = tflearn.fully_connected(net,len(output[0]), activation = "softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)
    model.load('./my_model/model.tflearn')

except Exception:
    ops.reset_default_graph()

    net = tflearn.input_data(shape = [None, len(training[0])])
    net = tflearn.fully_connected(net,8)
    net = tflearn.fully_connected(net,8)
    net = tflearn.fully_connected(net,len(output[0]), activation = "softmax")
    net = tflearn.regression(net)

    model = tflearn.DNN(net)
    
    model.fit(training, output, n_epoch = 200, batch_size = 8, show_metric = True)
    model.save("my_model/model.tflearn")
    

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return np.array(bag)

#*************************************CHATBOT FLASK**************************************************
@app.route('/response',methods=['POST','GET'])
def get_bot_response():
    login_status = True
    message = request.args.get('msg')
    response = "I didn't quite get that, please try again."
        
    if message:
        message = message.lower()
        results = model.predict([bag_of_words(message,words)])
        
        if message == "quit":
            return redirect(url_for('dashboard'))
        
        result_index = np.argmax(results)
        tag = labels[result_index]
        if np.amax(results) > 0:
            if tag == "navigate_dashboard":
                if login_status == True:
                    response = "Redirecting to dashboard."
                else:
                    response = "Login to system."
            else:
                for tg in data['intents']:
                    if tg['tag'] == tag:
                        responses = tg['responses']
                        response = random.choice(responses)
        return str(response)

#*************************************CHATBOT**************************************************

def get_product_website_from_name(product_with_website):
	product = product_with_website[2:-1]
	website = ''
	for char in product:
	    if char == "'":
	        break
	    website += char
	product_title = product[len(website)+4:-1]
	return product_title, website

def retreive_wishlist_product(product_with_website, product_dict):

	product_title, website = get_product_website_from_name(product_with_website)
	index = product_dict['title'].index(product_title)
	product_price = product_dict['price'][index]
	product_url = product_dict['url'][index]
	hyperlink = product_dict['hyperlink'][index]

	data = {"product_title" : product_title, "product_price" : product_price, "image_url" : product_url, "link" : hyperlink, "website" : website}

	items = db.child(session['table']).child('Wishlist').get()
	if not items.val():
		db.child(session['table']).child('Wishlist').push(data)

	else:
		for item in items.each():
			if item.val()['product_title'] == product_title:
				message = 'Item already in your wishlist'
				return message

		db.child(session['table']).child('Wishlist').push(data)
		message = 'Product successfully added to your Wishlist'
		return message

def retreive_notificationlist_product(product_with_website, product_dict):

	product_title, website = get_product_website_from_name(product_with_website)
	index = product_dict['title'].index(product_title)

	# for threshold take input from user in html, by default it has same value as product price
	threshold_price = product_dict['price'][index]

	product_url = product_dict['url'][index]
	hyperlink = product_dict['hyperlink'][index]

	stored_prices_list=[]

	price_checked_dict = {}
	price_checked_dict['threshold_price'] = threshold_price
	price_checked_dict['date'] = strftime("%Y-%m-%d", gmtime())
	price_checked_dict['time'] = strftime("%H:%M:%S", gmtime())

	# should we store the checked prices in a list OR make another entry in table and push it????  
	stored_prices_list.append(price_checked_dict)

	data = {"product_title" : product_title, "threshold_price" : threshold_price, "image_url" : product_url, "link" : hyperlink, "website" : website, "checked_prices" : stored_prices_list}

	items = db.child(session['table']).child('Notificationlist').get()
	if not items.val():
		db.child(session['table']).child('Notificationlist').push(data)

		# push email address only one time here
		db.child(session['table']).child('Email_address').push({"email":session['email']})

	else:
		for item in items.each():
			if item.val()['product_title'] == product_title:
				message = 'Item already in your Notificationlist'
				return message

		db.child(session['table']).child('Notificationlist').push(data)

		message = 'Product successfully added to your Notificationlist'
		return message

def format_email_firebase(email):

	char = ['.','$','[',']','#','/']
	email = email.split('@')[0]
	for c in char:
		if c in email:
			email = email.replace(c, '-')
	return email

def user_history(product_with_website, product_dict):

	product_title, website = get_product_website_from_name(product_with_website)
	index = product_dict['title'].index(product_title)
	product_price = product_dict['price'][index]
	product_url = product_dict['url'][index]
	hyperlink = product_dict['hyperlink'][index]

	date_now = str(date.today())

	data = {"product_title" : product_title, "product_price" : product_price, "image_url" : product_url, "link" : hyperlink, "website" : website,
			"date" : date_now}

	items = db.child(session['table']).child('History').get()
	if not items.val():
		db.child(session['table']).child('History').push(data)

	else:
		for item in items.each():
			if item.val()['product_title'] == product_title:
				return hyperlink

		db.child(session['table']).child('History').push(data)
		return hyperlink


@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():

	if request.method == 'POST':
		email = request.form['Email']
		password = request.form['Password']

		try:
			auth.sign_in_with_email_and_password(email, password)
			user_table_name = format_email_firebase(email)
			session['id'] = 'admin'
			session['table'] = user_table_name
			session['product_dict'] = None		
			session['email'] = email	
			return redirect(url_for('dashboard'))
		except:
			error_msg = 'Invalid Username or Password'
			return render_template('login.html', err=error_msg)
	else:
		session['id'] = 'None'
		return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():

	if request.method == 'POST':
		email = request.form['Email']
		password = request.form['Password']

		try:
			auth.create_user_with_email_and_password(email, password)
			user_table_name = format_email_firebase(email)	
			session['id'] = 'admin'
			session['table'] = user_table_name	
			session['product_dict'] = None
			session['email'] = email
			return redirect(url_for('dashboard'))

		except Exception as e:
			print(e)
			error_msg = 'There is already an account registered to this Email Id'
			return render_template('register.html', err=error_msg)
	else:
		session['id'] = 'None'
		return render_template('register.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():

	if session['id'] == 'admin':
		if request.method == 'POST':
			product_name = request.form['q']
			product_dict = get_products(product_name)
			session['product_dict'] = product_dict
			return redirect(url_for('result'))
		else:
			return render_template('dashboard.html')

	else:
		return redirect(url_for('login'))

@app.route('/result', methods=['GET','POST'])
def result():

	if request.method == 'POST':
		product_with_website = request.form['action']
		product_dict = session['product_dict']

		if product_with_website.endswith(',wishlist'):
			product_with_website = product_with_website[:-9]
			message = retreive_wishlist_product(product_with_website, product_dict)
			session['message'] = message
			return redirect(url_for('wishlist', message = message))
		elif product_with_website.endswith(',buy'):
			product_with_website = product_with_website[:-4]
			link = user_history(product_with_website, product_dict)
			return redirect(link,302)
		elif product_with_website.endswith(',notify'):
			product_with_website = product_with_website[:-7]
			message = retreive_notificationlist_product(product_with_website, product_dict)
			session['message'] = message
			return redirect(url_for('notificationlist', message = message))
	else:
		if session['id'] == 'admin':
			product_dict = session['product_dict']
			return render_template('results.html', product_dict = product_dict)
		return redirect(url_for('login'))

@app.route('/wishlist')
def wishlist():

	if session['id'] == 'admin':
		message = request.args.get('message')
		if not message:
			message = ''

		product_dict_wishlist = []
		items = db.child(session['table']).child('Wishlist').get()

		if not items.val():
			message = 'Your wishlist is empty'
			return render_template('wishlist.html', message = message, product_dict = product_dict_wishlist)

		for item in items.each():
				product_dict_wishlist.append(item.val()['product_title'])
				product_dict_wishlist.append(item.val()['product_price'])
				product_dict_wishlist.append(item.val()['image_url'])
				product_dict_wishlist.append(item.val()['link'])
				product_dict_wishlist.append(item.val()['website'])

		return render_template('wishlist.html', message = message, product_dict = product_dict_wishlist)
	else:
		return redirect(url_for('login'))

@app.route('/notificationlist')
def notificationlist():

	if session['id'] == 'admin':
		message = request.args.get('message')
		if not message:
			message = ''

		product_dict_notificationlist = []
		items = db.child(session['table']).child('Notificationlist').get()

		if not items.val():
			message = 'Your notificationlist is empty'
			return render_template('notificationlist.html', message = message, product_dict = product_dict_notificationlist)

		for item in items.each():
				product_dict_notificationlist.append(item.val()['product_title'])
				product_dict_notificationlist.append(item.val()['threshold_price'])
				product_dict_notificationlist.append(item.val()['image_url'])
				product_dict_notificationlist.append(item.val()['link'])
				product_dict_notificationlist.append(item.val()['website'])
				product_dict_notificationlist.append(item.val()['checked_prices'])

		return render_template('notificationlist.html', message = message, product_dict = product_dict_notificationlist)
	else:
		return redirect(url_for('login'))

@app.route('/history')
def history():

	if session['id'] == 'admin':
		message = ''
		product_dict_history = []
		items = db.child(session['table']).child('History').get()

		if not items.val():
			message = 'You havent purchased any products yet!'
			return render_template('display.html', message = message, product_dict = product_dict_history)

		for item in items.each():
				product_dict_history.append(item.val()['product_title'])
				product_dict_history.append(item.val()['product_price'])
				product_dict_history.append(item.val()['date'])
				product_dict_history.append(item.val()['image_url'])
				product_dict_history.append(item.val()['link'])
				product_dict_history.append(item.val()['website'])

		return render_template('display.html', message = message, product_dict = product_dict_history)
	else:
		return redirect(url_for('login'))

@app.route('/logout')
def logout():
	
	session['id'] = None
	session['email'] = None
	session['table'] = None
	session['product_dict'] = None		
	return render_template('logout.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=8001,threaded=True)
