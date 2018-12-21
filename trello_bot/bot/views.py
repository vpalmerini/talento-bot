from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .commands import *
import time
import schedule

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
			labels = get_nested_objects('boards',board_id, 'labels').json()

			# get board lists
			lists = get_nested_objects('boards',board_id,'lists').json()

			for list_obj in lists[1:]:
				list_obj_id = list_obj['id']
				cards = get_nested_objects('lists', list_obj_id, 'cards').json()
				for card_obj in cards:
					update_card_labels(card_obj, labels)
					
		except Exception as e:
			raise e

	return HttpResponse(status=200)

def dash(request):
	update_db()
	context = {
		'hunters': {},
		'doughnut': {},
	}
	hunters = Hunter.objects.all()
	context['avatar_url'] = ["{{% static 'bot/images/avatar/{}.jpg' %}}".format(str(i)) for i in range(len(hunters)+1)] # this is wrong
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
