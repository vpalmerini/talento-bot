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


def dashboard(request):
	context = {}
	# hunters data
	hunters = sorted(Hunter.objects.all(),
					 key=lambda x: x.closed_count,
					 reverse=True)
	context['hunters'] = {i+1:hunters[i] for i in range(len(hunters))}
	# category data
	context['doughnut'] = [Company.objects.filter(category=i).count()
							for i in Company.category_list]
	# month closed data
	context['bar'] = [Company.objects.filter(month_closed=i).count()
						for i in range(1,13)]
	# total closed data
	closed_list = [Company.objects.filter(status=i).count()
					for i in Company.status_list[-3:]]
	context['total_closed'] = sum(closed_list)
 
	return render(request, 'bot/dashboard.html', context)


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
		# if company.needs_reminder:
			# company.email_reminder()
