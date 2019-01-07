from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .trello_requests import data, get_nested_objects
from .models import Company, Hunter
import requests
import time
import schedule


def update_db():
    """ includes all hunters and companies in trello
            board and updates their information into db
    """
    # board lists
    lists = get_nested_objects('boards', data['board_id'], 'lists').json()
    # cards of list of emails
    cards = get_nested_objects('lists', lists[0]['id'], 'cards').json()
    emails = [cards[i]['name'] for i in range(len(lists)-1)]

    # updating hunters
    for list, email in zip(lists[1:], emails):
        try:
            h = Hunter.objects.get(email=email)
        except:
            h = Hunter(email=email)
        h.name = list['name']
        h.list_id = list['id']
        h.save()

        # updating companies
        cards = get_nested_objects('lists', list['id'], 'cards').json()
        for card in cards:
            try:
                c = Company.objects.get(name=card['name'])
            except:
                c = Company(name=card['name'])
            c.card_id = card['id']
            c.category = card['desc']
            c.hunter = h
            c.category = card['desc']
            c.save()


@csrf_exempt
def main(request):

    schedule.every(1).minutes.do(polling)
    # schedule.every().day.at("12:00").do(polling)

    while True:
        schedule.run_pending()
        time.sleep(1)

    return HttpResponse(status=200)


def dashboard(request):
    """ rendering of the dashboard """
    context = {}
    # hunters data
    hunters = sorted(Hunter.objects.all(),
                     key=lambda x: x.closed_count,
                     reverse=True)
    context['hunters'] = {i+1: hunters[i] for i in range(len(hunters))}
    # category data
    context['doughnut'] = [Company.objects.filter(category=i).count()
                           for i in Company.category_list]
    # month closed data
    context['bar'] = [Company.objects.filter(month_closed=i).count()
                      for i in range(1, 13)]
    # total closed data
    closed_list = [Company.objects.filter(status=i).count()
                   for i in Company.status_list[-3:]]
    context['total_closed'] = sum(closed_list)

    return render(request, 'bot/dashboard.html', context)


def polling():
    """ detects changes in the trello board and
            executes the necessary actions
    """
    update_db()
    for company in Company.objects.all():
        company.update_status_labels()
        company.update_contact_labels()
        # commented out to avoid spamming
        # if company.needs_reminder:
            # company.email_reminder()
