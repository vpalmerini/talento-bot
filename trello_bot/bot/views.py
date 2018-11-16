from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .commands import *
import requests
import json
import time

file_token = open('token.txt', 'r')
token = file_token.read()

file_key = open('key.txt', 'r')
key = file_key.read()

board_id = '5bdb65794ac71e0cc84ec17b'
api_url = 'https://api.trello.com/1'

@csrf_exempt
def main(request):

	if request.method == 'POST':
		try:
			body_unicode = request.body.decode('utf-8')
			data = json.loads(body_unicode)

			# get board lists
			lists_response = get_nested_objects('boards',board_id,'lists')
			lists = json.loads(lists_response.text)

			for list_obj in lists:
				list_obj_id = list_obj['id']
				cards_response = get_nested_objects('lists', list_obj_id, 'cards')
				cards = json.loads(cards_response.text)

				for card_obj in cards:
					get_cards(card_obj)
					
		except Exception as e:
			raise e

	return HttpResponse(status=200)
