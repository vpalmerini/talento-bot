import requests
import json

with open('data.json', 'r') as file:
    # data is a mapping variable that holds information about:
        # access key to the Trello API
        # access token to the board
        # the id of the board modified
        # the url to access the api
        # the email adress that sends notifications
        # the password to login with this email
        # the host domain of the smtp
        # the port to be used to send emails
        # the labels regarding each of status of the company hunting
        # the labels that mark whether or not the contact is updated
    data = json.load(file)


def generic_request(ext_object, object_id, nested_object):
    url = '{}/{}/{}/{}'.format(data['api_url'], ext_object,
                               object_id, nested_object)
    querystring = {
        'key': data['key'],
        'token': data['token'],
    }
    return url, querystring


def get_nested_objects(ext_object, object_id, nested_object=''):
    url, querystring = generic_request(ext_object, object_id, nested_object)
    response = requests.get(url, params=querystring)
    return response


def post_label(card_id, label):
    url, querystring = generic_request('cards', card_id, 'labels')
    querystring.update(label)
    response = requests.post(url, params=querystring)


def remove_label(card_id, label_id):
    url, querystring = generic_request('cards', card_id, 'idLabels')
    url = ''.join([url, '/{}'.format(label_id)])
    requests.delete(url, params=querystring)
