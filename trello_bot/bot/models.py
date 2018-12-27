from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta

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
		(DECLINED,'Declined'),
		(CLOSED,'Closed'),
		(SIGNED,'Signed'),
		(PAID,'Paid'),
	)

	status = models.CharField(
		max_length=2,
		choices=STATUS_CHOICES,
		blank=True,
		default=CONTACTED,
	)
	last_activity = models.DateTimeField(auto_now_add=True)
	hunter = models.ForeignKey('Hunter', on_delete=models.CASCADE)
	month_closed = models.IntegerField(
		validators = [MinValueValidator(1), MaxValueValidator(12)],
	)

	def inactive_time(self):
		return datetime.now() - self.last_activity

	def set_last_activity(self):
		self.last_activity = datetime.now()

	def needs_reminder(self): 
		return not (
			any( self.status == i for i in [DECLINED, SIGNED, PAID] )
			or ( self.inactive_time.days < 12 )
		)

	def __str__(self):
		return self.name