from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json

file_token = open('token.txt', 'r')
token = file_token.read()

file_key = open('key.txt', 'r')
key = file_key.read()


@csrf_exempt
def main(request):

	print('main')

	if request.method == 'POST':
		print('post')
		try:
			body_unicode = request.body.decode('utf-8')
			data = json.loads(body_unicode)
			print(data)

		except Exception as e:
			raise e

	return HttpResponse(status=200)
