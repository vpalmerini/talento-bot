import requests
from datetime import datetime, timedelta
from .models import Hunter, Company

file_token = open('token.txt', 'r')
token = file_token.readline()

file_key = open('key.txt', 'r')
key = file_key.readline()

board_id = '5bdb65794ac71e0cc84ec17b'
api_url = 'https://api.trello.com/1'

smtp_host = 'br84.hostgator.com.br'
smtp_port = 26

# board labels
status_labels = {
	'IT': {
		'id': '5bdb6579a724a908c0b057dd',
		'idBoard': board_id,
		'name': 'Empresa Interessada',
		'color': 'purple',
	},
	'PL': {
		'id': '5bedd6c41c344e3b9fe97dd2',
		'idBoard': board_id,
		'name': 'Carta Proposta Enviada',
		'color': 'pink',
	},
	'CL': {
		'id': '5bedd6c1facc3a5c40b3c380',
		'idBoard': board_id,
		'name': 'Empresa Fechada',
		'color': 'lime',
	},
	'SG': {
		'id': '5bdb6579a724a908c0b057d6',
		'idBoard': board_id,
		'name': 'Contrato Assinado',
		'color': 'orange',
	}, 
	'DC': {
		'id': '5bdb6579a724a908c0b057df',
		'idBoard': board_id,
		'name': 'Empresa Não Interessada',
		'color': 'blue',
	},
	'PD': {
		'id': '5bedd6c76796866dcad2f697',
		'idBoard': board_id,
		'name': 'Patrocínio Pago',
		'color': 'black',
	},
}
contact_labels = {
	'updated': {
		'id': '5bdb6579a724a908c0b057d8', 
		'idBoard': board_id, 
		'name': 'Atualizado', 
		'color': 'green',
	},
	'attention': {
		'id': '5bdb6579a724a908c0b057d7',
		'idBoard': board_id,
		'name': 'Atenção',
		'color': 'yellow',
	},
	'urgent': {
		'id': '5bdb6579a724a908c0b057d9',
		'idBoard': board_id,
		'name': 'Urgente',
		'color': 'red',
	},
}

# deadline variables
ATTENTION_DEADLINE = 1
URGENT_DEADLINE = 2

# def get_webhook_id(key, token):

# 	url = 'https://api.trello.com/1/members/me/tokens?webhooks=true&key={}&token={}'.format(key,token)
# 	response = requests.get(url)


def update_db():
	""" includes all hunters and companies in trello
		board and updates their information into db
	"""

	lists = get_nested_objects('boards', board_id, 'lists').json()
	cards = get_nested_objects('lists', lists[0]['id'], 'cards').json()
	# the list of emails is in the first list
	emails = [cards[i]['name'] for i in range(len(lists)-1)]

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
			c.category = card['desc']
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
	body = "<h4>Já faz muito tempo desde que a empresa " + company.name + " respondeu sobre a sua participação na Talento 2019.<br>Por favor entre em contato novamente para ober uma resposta.</h4><br><br>Gratos,<br>Organização Talento 2019."
	msg.attach(MIMEText(body, 'html'))

	# email sending
	with SMTP(smtp_host, smtp_port) as server:
		server.starttls()
		server.login(msg['From'], password)
		server.sendmail(msg['From'], msg['To'], msg.as_string())

def update_status_labels(company):
	# company card
	card = get_nested_objects('cards', company.card_id).json()

	status_list = [
		Company.PAID,
		Company.DECLINED,
		Company.SIGNED,
		Company.CLOSED,
		Company.PLSENT,
		Company.INTERESTED,
		Company.CONTACTED,
	]
	for status in status_list:
		if status_labels[status] in card['labels'] and company.status != status:
			company.status = status
			company.set_last_activity()
			if status == Company.CLOSED:
				company.month_closed = datetime.now().month
			for label in card['labels']:
				if label != status_labels[status] and label not in contact_labels.values():
					remove_label(card['id'], label['id'])
			break

def update_contact_labels(company):
	# company card
	card = get_nested_objects('cards', company.card_id).json()

	# updated
	if company.inactive_time.days < ATTENTION_DEADLINE:
		for label in card['labels']:
			if label == contact_labels['attention'] or label == contact_labels['urgent']:
				remove_label(card['id'], label['id'])
		if contact_labels['updated'] not in card['labels']:
			post_label(card['id'], contact_labels['updated'])

	# attention
	elif company.inactive_time.days < URGENT_DEADLINE:
		for label in card['labels']:
			if label == contact_labels['updated'] or label == contact_labels['urgent']:
				remove_label(card['id'], label['id'])
		if contact_labels['attention'] not in card['labels']:
			post_label(card['id'], contact_labels['attention'])

	# urgent
	else:
		for label in card['labels']:
			if label == contact_labels['attention'] or label == contact_labels['updated']:
				remove_label(card['id'], label['id'])
		if contact_labels['urgent'] not in card['labels']:
			post_label(card['id'], contact_labels['urgent'])

def get_nested_objects(ext_object, object_id, nested_object=''):

	url = '{}/{}/{}/{}'.format(api_url, ext_object, object_id, nested_object)
	
	querystring = {
		'key':key, 
		'token':token,
	}
	
	response = requests.get(url, params=querystring)

	return response


def post_label(card_id, label):

	url = '{}/cards/{}/labels'.format(api_url, card_id)
	
	querystring = {
		'key':key, 
		'token':token,
	}

	querystring.update(label)

	response = requests.post(url, params=querystring)

def remove_label(card_id, label_id):

	url = '{}/cards/{}/idLabels/{}'.format(api_url, card_id, label_id)

	querystring = {
		'key':key,
		'token':token,
	}

	requests.delete(url, params=querystring)