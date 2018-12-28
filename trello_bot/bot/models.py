from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .commands import *

class Hunter(models.Model):

	email = models.EmailField(max_length=100, primary_key=True)
	name = models.CharField(max_length=100)
	list_id = models.CharField(max_length=100, null=True)

	def contact_count(self):
		return len(Company.objects.filter(hunter=self))

	def closed_count(self):
		return len(Company.objects.filter(hunter=self, status='CL'))

	def __str__(self):
		return self.name


class Company(models.Model):

	name = models.CharField(max_length=100, primary_key=True)
	card_id = models.CharField(max_length=100, null=True)

	FINANCIAL = 'FN'
	CONSULTING = 'CS'
	INDUSTRY = 'ID'

	CATEGORY_CHOICES = (
		(FINANCIAL,'Financial'),
		(CONSULTING,'Consulting'),
		(INDUSTRY,'Industry'),
	)

	category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)

	CONTACTED = 'CT'
	INTERESTED = 'IT'
	PLSENT = 'PL'
	CLOSED = 'CL'
	SIGNED = 'SG'
	DECLINED = 'DC'
	PAID = 'PD'

	STATUS_CHOICES = (
		(CONTACTED, 'Contacted'),
		(INTERESTED,'Interested'),
		(PLSENT, 'Proposal Letter Sent'),
		(DECLINED, 'Declined'),
		(CLOSED, 'Closed'),
		(SIGNED, 'Signed'),
		(PAID, 'Paid'),
	)

	status = models.CharField(
		max_length=2,
		choices=STATUS_CHOICES,
		blank=True,
		default=CONTACTED,
	)
	last_activity = models.DateTimeField(default=timezone.now)
	hunter = models.ForeignKey('Hunter', on_delete=models.CASCADE)
	month_closed = models.IntegerField(
		validators = [MinValueValidator(1), MaxValueValidator(12)],
		null = True,
		blank = True,
	)

	def inactive_time(self):
		return timezone.now() - self.last_activity

	def set_last_activity(self):
		self.last_activity = timezone.now()

	def needs_reminder(self): 
		return not (
			any( self.status == i for i in [Company.DECLINED, Company.SIGNED, Company.PAID] )
			or ( self.inactive_time().days < 12 )
		)

	def email_reminder(self):
		""" sends email to the hunter responsible for a company
			that has not answered in a while
		"""
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
		from smtplib import SMTP

		# email credentials
		from_adress = 'captacao@mte.org.br'
		with open('password.txt', 'r') as pswd_file:
			password = pswd_file.readline()

		# message building
		msg = MIMEMultipart()
		msg['From'] = from_adress
		msg['To'] = self.hunter.email
		msg['Subject'] = "Você precisa entrar em contato com a empresa " + self.name + "!"
		body = "<h4>Já faz muito tempo desde que a empresa " + self.name + " respondeu sobre a sua participação na Talento 2019.<br>Por favor entre em contato novamente para ober uma resposta.</h4><br><br>Gratos,<br>Organização Talento 2019."
		msg.attach(MIMEText(body, 'html'))

		# email sending
		with SMTP(smtp_host, smtp_port) as server:
			server.starttls()
			server.login(msg['From'], password)
			server.sendmail(msg['From'], msg['To'], msg.as_string())

	def update_status_labels(self):
		# company card
		card = get_nested_objects('cards', self.card_id).json()

		status_list = [
			Company.PAID,
			Company.DECLINED,
			Company.SIGNED,
			Company.CLOSED,
			Company.PLSENT,
			Company.INTERESTED,
			Company.CONTACTED,
		]
		for status in status_list:
			if status_labels[status] in card['labels'] and self.status != status:
				self.status = status
				self.set_last_activity()
				if status == Company.CLOSED:
					self.month_closed = timezone.now().month
				for label in card['labels']:
					if label != status_labels[status] and label not in contact_labels.values():
						remove_label(card['id'], label['id'])
				break

	def update_contact_labels(self):
		# company card
		card = get_nested_objects('cards', self.card_id).json()

		# updated
		if self.inactive_time().days < ATTENTION_DEADLINE:
			for label in card['labels']:
				if label == contact_labels['attention'] or label == contact_labels['urgent']:
					remove_label(card['id'], label['id'])
			if contact_labels['updated'] not in card['labels']:
				post_label(card['id'], contact_labels['updated'])

		# attention
		elif self.inactive_time().days < URGENT_DEADLINE:
			for label in card['labels']:
				if label == contact_labels['updated'] or label == contact_labels['urgent']:
					remove_label(card['id'], label['id'])
			if contact_labels['attention'] not in card['labels']:
				post_label(card['id'], contact_labels['attention'])

		# urgent
		else:
			for label in card['labels']:
				if label == contact_labels['attention'] or label == contact_labels['updated']:
					remove_label(card['id'], label['id'])
			if contact_labels['urgent'] not in card['labels']:
				post_label(card['id'], contact_labels['urgent'])

	def __str__(self):
		return self.name
