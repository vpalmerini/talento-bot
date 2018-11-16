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

def get_cards(card_obj):

	card_id = card_obj['id']

	card_date = card_obj['dateLastActivity']
	card_date = time.strptime(card_date[:19], "%Y-%m-%dT%H:%M:%S")
	card_date = time.strftime("%d/%m/%Y", card_date)
	card_date = card_date.split('/')
	card_date_day = int(card_date[0])

	now = time.asctime()
	now = time.strptime(now)
	now = time.strftime('%d/%m/%Y', now)
	now = now.split('/')
	now_day = int(now[0])

	time_inert = now_day - card_date_day

	post_label('cards',card_id,'green')


def get_nested_objects(ext_object, object_id, nested_object):

	url = '{}/{}/{}/{}'.format(api_url,ext_object,object_id,nested_object)
	querystring = {'key':key, 'token':token}
	response = requests.get(url, params=querystring)

	return response


def post_label(ext_object, object_id, label):

	url = '{}/{}/{}/{}'.format(api_url,ext_object,object_id,'labels')
	querystring = {
					'color':label,
				   	'key':key, 
				   	'token':token
				  }

	response = requests.post(url, params=querystring)
