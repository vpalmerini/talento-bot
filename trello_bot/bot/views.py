from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Company, Hunter
from .commands import *
import requests
import json
import time
import schedule

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
			print(data)

			# companies_not_hunted = get_nested_objects('boards',board_id,'cards')
			# print('Nº de empresas a serem captadas:', len(companies_not_hunted))

			# n_companies_hunted = Company.objects.count()
			# print('Nº de empresas que estão sendo captadas:', companies_hunted)

			# get board labels
			labels_response = get_nested_objects('boards',board_id, 'labels')
			labels = json.loads(labels_response.text)

			# get board lists
			lists_response = get_nested_objects('boards',board_id,'lists')
			lists = json.loads(lists_response.text)

			for list_obj in lists:
				list_obj_id = list_obj['id']

				if list_obj['name'] == 'Empresas':
					continue
				
				else:
					cards_response = get_nested_objects('lists', list_obj_id, 'cards')
					cards = json.loads(cards_response.text)

					for card_obj in cards:
						update_card_labels(card_obj,labels)
					
		except Exception as e:
			raise e

	return HttpResponse(status=200)



def polling():

	url = "{}/boards/{}".format(api_url,board_id)

	querystring = {
			"actions":"all",
			"boardStars":"none",
			"cards":"none",
			"card_pluginData":"false",
			"checklists":"none",
			"customFields":"false",
			"fields":"name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames",
			"lists":"open",
			"members":"none",
			"memberships":"none",
			"membersInvited":"none",
			"membersInvited_fields":"all",
			"pluginData":"false",
			"organization":"false",
			"organization_pluginData":"false",
			"myPrefs":"false",
			"tags":"false",
			"key":key,
			"token":token}

	response = requests.get(url, params=querystring)

	requests.post('https://50d6a238.ngrok.io/{}'.format(token), data=response.text)


schedule.every(1).minutes.do(polling)

while True:
    schedule.run_pending()
    time.sleep(1)
