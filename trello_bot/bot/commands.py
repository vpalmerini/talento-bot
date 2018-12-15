import requests
import time
from .models import Hunter, Company

file_token = open('token.txt', 'r')
token = file_token.read()

file_key = open('key.txt', 'r')
key = file_key.read()

board_id = '5bdb65794ac71e0cc84ec17b'
api_url = 'https://api.trello.com/1'

# deadline variables
ATENTION_DEADLINE = 7
URGENT_DEADLINE = 12

def update_db():
	""" includes all hunters and companies in the trello
		board and updates thier information in the db
	"""

	lists = get_nested_objects('boards', board_id, 'lists').json()
	cards = get_nested_objects('lists', lists[0]['id'], 'cards').json()
	# the list of emails are in the first list
	emails = []
	for i in range(len(lists)-1):
		emails.append(cards[i]['name'])

	# updating hunters
	for list, email in zip(lists[1:], emails):
		try:
			h = Hunter.objects.get(email=email)
		except:
			h = Hunter(email=email, name=list['name'], list_id=list['id'])
		h.save()
		cards = get_nested_objects('lists', list['id'], 'cards').json()

		# updating companies
		for card in cards:
			try:
				c = Company.objects.get(name=card['name'])
			except:
				c = Company(name=card['name'], card_id=card['id'], category=card['desc'], hunter=h)
			c.save()

def email_reminder(company):
	""" sends email to the hunter responsible for a company
		that has not answered in a while
	"""
	
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from smtplib import SMTP

	# email credentials
	from_adress = 'captacao@mte.org.br'
	with open('password.txt', 'r') as pswd_file:
		password = pswd_file.readline()

	# message building
	msg = MIMEMultipart()
	msg['From'] = from_adress
	msg['To'] = company.hunter.email
	msg['Subject'] = "Você precisa entrar em contato com a empresa " + company.name + "!"
	body = "Já faz muito tempo desde que a empresa " + company.name + " respondeu sobre a sua participação na Talento 2019.<br>Por favor entre em contato novamente para ober uma resposta.<br><br>Gratos,<br>Organização Talento 2019."
	msg.attach(MIMEText(body, 'html'))

	# email sending
	with SMTP('br84.hostgator.com.br', 26) as server:
		server.starttls()
		server.login(msg['From'], password)
		server.sendmail(msg['From'], msg['To'], msg.as_string())

def update_card_labels(card_obj, labels):

	updated_label = {
			'id': '5bdb6579a724a908c0b057d8', 
			'idBoard': '5bdb65794ac71e0cc84ec17b', 
			'name': 'Atualizado', 
			'color': 'green'
	}

	atention_label = {
			'id':'5bdb6579a724a908c0b057d7',
			'idBoard':'5bdb65794ac71e0cc84ec17b',
			'name':'Atenção',
			'color':'yellow'
	}

	urgent_label = {
			'id':'5bdb6579a724a908c0b057d9',
			'idBoard':'5bdb65794ac71e0cc84ec17b',
			'name':'Urgente',
			'color':'red'
	}

	card_id = card_obj['id']
	card_labels = card_obj['labels']
	card_date = card_obj['dateLastActivity']
	card_date_day = format_date(card_date)

	now = time.asctime()
	now = time.strptime(now)
	now = time.strftime('%d/%m/%Y', now)
	now = now.split('/')
	now_day = int(now[0])

	time_inert = now_day - card_date_day

	not_in = True

	# updated
	if (time_inert < ATENTION_DEADLINE):
		for label in card_labels:
			if label['name'] == 'Atualizado':
				not_in = False
				break
		if not_in:
			post_label('cards',card_id,updated_label)

	# atention
	elif (time_inert < URGENT_DEADLINE):
		not_in = True
		for label in card_labels:
			if label['name'] == 'Atenção':
				not_in = False
				break
		if not_in:
			post_label('cards',card_id,atention_label)

	# urgent
	else:
		not_in = True
		for label in card_labels:
			if label['name'] == 'Urgente':
				not_in = False
				break
		if not_in:
			post_label('cards',card_id,urgent_label)



def get_nested_objects(ext_object, object_id, nested_object):

	url = '{}/{}/{}/{}'.format(api_url,ext_object,object_id,nested_object)
	
	querystring = {
		'key':key, 
		'token':token
	}
	
	response = requests.get(url, params=querystring)

	return response


def post_label(ext_object, object_id, label):

	url = '{}/{}/{}/{}'.format(api_url,ext_object,object_id,'labels')
	
	querystring = {
		'key':key, 
		'token':token
	}

	querystring.update(label)

	response = requests.post(url, params=querystring)


def format_date(date):

	date = time.strptime(date[:19], "%Y-%m-%dT%H:%M:%S")
	date = time.strftime("%d/%m/%Y", date)
	date = date.split('/')
	date = int(date[0])

	return date
