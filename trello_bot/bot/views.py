from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .commands import *
from .models import Company, Hunter
import time
import schedule

@csrf_exempt
def main(request):

	# if request.method == 'POST':
	# 	try:
	# 		# get board labels
	# 		labels = get_nested_objects('boards',board_id, 'labels').json()

	# 		# get board lists
	# 		lists = get_nested_objects('boards',board_id,'lists').json()

	# 		for list_obj in lists[1:]:
	# 			list_obj_id = list_obj['id']
	# 			cards = get_nested_objects('lists', list_obj_id, 'cards').json()
	# 			for card_obj in cards:
	# 				update_card_labels(card_obj, labels)
					
	# 	except Exception as e:
	# 		raise e

	schedule.every(1).minutes.do(polling)
	# schedule.every().day.at("12:00").do(polling)

	while True:
	    schedule.run_pending()
	    time.sleep(1)

	return HttpResponse(status=200)


def dash(request):
	context = {
		'hunters': {},
		'doughnut': {},
	}
	hunters = Hunter.objects.all()
	for i in range(len(hunters)):
		context['hunters'][i+1] = hunters[i]

	context['doughnut']['data'] = [
		len(Company.objects.filter(category='FN')),
		len(Company.objects.filter(category='CS')),
		len(Company.objects.filter(category='ID')),
	]

	context['total_closed'] = len(Company.objects.filter(status='CL'))
 
	return render(request, 'bot/dash.html', context)


def polling():

	url = 'https://trello.com/b/KFOrbNWy/talento-2019-captação.json'
	querystring = {
		"actions": "all",
		"boardStars": "none",
		"cards": "none",
		"card_pluginData": "false",
		"checklists": "none",
		"customFields": "false",
		"fields": "name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames",
		"lists": "open",
		"members": "none",
		"memberships": "none",
		"membersInvited": "none",
		"membersInvited_fields": "all",
		"pluginData": "false",
		"organization": "false",
		"organization_pluginData": "false",
		"myPrefs": "false",
		"tags": "false",
		"key": key,
		"token": token,
	}
	response = requests.get(url, params=querystring)
	requests.post('https://d31715c0.ngrok.io/{}'.format(token), data=response.text)

	update_db()
	for company in Company.objects.all():
		company.update_status_labels()
		company.update_contact_labels()
		# commented out to avoid spamming
		# if company.needs_reminder():
			# company.email_reminder()
