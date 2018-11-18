from .views import *
import requests
import json
import time

file_token = open('token.txt', 'r')
token = file_token.read()

file_key = open('key.txt', 'r')
key = file_key.read()

board_id = '5bdb65794ac71e0cc84ec17b'
api_url = 'https://api.trello.com/1'

# deadline variables
ATENTION_DEADLINE = 7
URGENT_DEADLINE = 12

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
			post_label('cards',card_id,'atention_label')

	# urgent
	else:
		not_in = True
		for label in card_labels:
			if label['name'] == 'Urgente':
				not_in = False
				break
		if not_in:
			post_label('cards',card_id,'urgent_label')



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



# {'id': '5bdb662bdf70b043fffccc9f', 
# 'checkItemStates': None, 
# 'closed': False, 
# 'dateLastActivity': '2018-11-16T00:18:04.273Z',
# 'desc': '', 
# 'descData': None, 
# 'idBoard': '5bdb65794ac71e0cc84ec17b', 
# 'idList': '5bdb65912b808b813a89332a', 
# 'idMembersVoted': [], 'idShort': 12, 
# 'idAttachmentCover': None, 
# 'idLabels': ['5bdb6579a724a908c0b057dd', '5bdb6579a724a908c0b057d6', '5bdb6579a724a908c0b057d8'], 
# 'manualCoverAttachment': False, 
# 'name': 'Ericsson', 
# 'pos': 98303, 
# 'shortLink': 'qqhdxrAD', 
# 'badges': {'votes': 0, 'attachmentsByType': {'trello': {'board': 0, 'card': 0}}, 'viewingMemberVoted': False, 'subscribed': False, 'fogbugz': '', 'checkItems': 0, 'checkItemsChecked': 0, 'comments': 0, 'attachments': 0, 'description': False, 'due': None, 'dueComplete': False}, 
# 'dueComplete': False, 
# 'due': None, 
# 'idChecklists': [], 
# 'idMembers': [], 
# 'labels': [{'id': '5bdb6579a724a908c0b057dd', 'idBoard': '5bdb65794ac71e0cc84ec17b', 'name': 'Empresa Interessada', 'color': 'purple'}, {'id': '5bdb6579a724a908c0b057d6', 'idBoard': '5bdb65794ac71e0cc84ec17b', 'name': 'Contrato Assinado', 'color': 'orange'}, {'id': '5bdb6579a724a908c0b057d8', 'idBoard': '5bdb65794ac71e0cc84ec17b', 'name': 'Atualizado', 'color': 'green'}], 
# 'shortUrl': 'https://trello.com/c/qqhdxrAD', 
# 'subscribed': False, 
# 'url': 'https://trello.com/c/qqhdxrAD/12-ericsson'}


