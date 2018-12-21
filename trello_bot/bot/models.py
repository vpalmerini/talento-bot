from django.db import models


class Hunter(models.Model):

	email = models.EmailField(max_length=100, primary_key=True)
	name = models.CharField(max_length=100)
	list_id = models.CharField(max_length=100)

	def contact_count(self):
		return len(Company.objects.filter(hunter=self))

	def closed_count(self):
		return len(Company.objects.filter(hunter=self, status='CL'))

	def __str__(self):
		return self.name


class Company(models.Model):

	name = models.CharField(max_length=100, primary_key=True)
	card_id = models.CharField(max_length=100)

	FINANCIAL = 'FN'
	CONSULTING = 'CS'
	INDUSTRY = 'ID'

	CATEGORY_CHOICES = (
		(FINANCIAL,'Financial'),
		(CONSULTING,'Consulting'),
		(INDUSTRY,'Industry')
	)

	category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)

	CONTACTED = 'CT'
	INTERESTED = 'IT'
	DECLINED = 'DC'
	CLOSED = 'CL'
	SIGNED = 'SG'
	PAID = 'PD'

	STATUS_CHOICES = (
		(CONTACTED, 'Contacted'),
		(INTERESTED,'Interested'),
		(DECLINED,'Declined'),
		(CLOSED,'Closed'),
		(SIGNED,'Signed'),
		(PAID,'Paid')
	)

	status = models.CharField(max_length=2, choices=STATUS_CHOICES, blank=True)

	hunter = models.ForeignKey('Hunter', on_delete=models.CASCADE)

	def __str__(self):
		return self.name