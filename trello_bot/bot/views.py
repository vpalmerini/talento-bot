from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .commands import *
import time

@csrf_exempt
def main(request):

	if request.method == 'POST':
		try:
			body_unicode = request.body.decode('utf-8')
			data = json.loads(body_unicode)

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


