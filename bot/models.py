from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from .trello_requests import data, get_nested_objects, post_label, remove_label


class Hunter(models.Model):

    email = models.EmailField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    list_id = models.CharField(max_length=100, null=True)

    @property
    def contact_count(self):
        return Company.objects.filter(hunter=self).count()

    @property
    def closed_count(self):
        closed_list = [Company.objects.filter(hunter=self, status=i).count()
                       for i in Company.status_list[-3:]]
        return sum(closed_list)

    def __str__(self):
        return self.name


class Company(models.Model):

    name = models.CharField(max_length=100, primary_key=True)
    card_id = models.CharField(max_length=100, null=True)

    FINANCIAL = 'FN'
    CONSULTING = 'CS'
    INDUSTRY = 'ID'

    CATEGORY_CHOICES = (
        (FINANCIAL, 'Financial'),
        (CONSULTING, 'Consulting'),
        (INDUSTRY, 'Industry'),
    )

    category_list = [
        FINANCIAL,
        CONSULTING,
        INDUSTRY,
    ]

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
        (INTERESTED, 'Interested'),
        (PLSENT, 'Proposal Letter Sent'),
        (DECLINED, 'Declined'),
        (CLOSED, 'Closed'),
        (SIGNED, 'Signed'),
        (PAID, 'Paid'),
    )

    status_list = [
        CONTACTED,
        INTERESTED,
        PLSENT,
        DECLINED,
        CLOSED,
        SIGNED,
        PAID,
    ]

    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        blank=True,
        default=CONTACTED,
    )
    last_activity = models.DateTimeField(default=timezone.now)
    hunter = models.ForeignKey('Hunter', on_delete=models.CASCADE)
    month_closed = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        null=True,
        blank=True,
    )

    # deadline variables
    ATTENTION_DEADLINE = 1
    URGENT_DEADLINE = 12

    @property
    def inactive_time(self):
        return (timezone.now() - self.last_activity)

    @property
    def needs_reminder(self):
        finished = [Company.DECLINED, Company.SIGNED, Company.PAID]
        return not (
            (self.inactive_time.days < Company.URGENT_DEADLINE)
            or any(self.status == i for i in finished)
        )

    @property
    def contact_label(self):
        if self.inactive_time.days < Company.ATTENTION_DEADLINE:
            return 'updated'
        elif self.inactive_time.days < Company.URGENT_DEADLINE:
            return 'attention'
        else:
            return 'urgent'

    def set_last_activity(self):
        self.last_activity = timezone.now()
        self.save()

    def email_reminder(self):
        """ sends email to the hunter responsible for a company
                that has not answered in a while
        """
        # email credentials
        from_adress = data['from_adress']
        password = data['password']
        smtp_host = data['smtp_host']
        smtp_port = data['smtp_port']

        # message building
        msg = MIMEMultipart()
        msg['From'] = from_adress
        msg['To'] = self.hunter.email
        msg['Subject'] = \
            "Você precisa entrar em contato com a empresa " + self.name + "!"
        body = \
            "<h4>Já faz muito tempo desde que a empresa " + self.name \
            + " respondeu sobre a sua participação na Talento 2019.<br>" \
            + "Por favor entre em contato novamente para ober uma resposta." \
            + "</h4><br><br>Gratos,<br>Organização Talento 2019."
        msg.attach(MIMEText(body, 'html'))

        # email sending
        with SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())

    def update_status_labels(self):
        # company card
        card = get_nested_objects('cards', self.card_id).json()

        contact_labels = data['contact_labels']
        status_labels = data['status_labels']

        for status in reversed(Company.status_list):
            if (status_labels[status] in card['labels']
                    and self.status != status):
                self.status = status
                self.set_last_activity()
                if status == Company.CLOSED:
                    self.month_closed = timezone.now().month
                for label in card['labels']:
                    if (label != status_labels[status]
                            and label not in contact_labels.values()):
                        remove_label(card['id'], label['id'])
                break
        self.save()

    def update_contact_labels(self):
        # company card
        card = get_nested_objects('cards', self.card_id).json()

        contact_labels = data['contact_labels']

        # removal of incorrect labels
        for label in card['labels']:
            if (label != contact_labels[self.contact_label]
                    and label in contact_labels.values()):
                remove_label(card['id'], label['id'])
        # posting right label
        if contact_labels[self.contact_label] not in card['labels']:
            post_label(card['id'], contact_labels[self.contact_label])

    def __str__(self):
        return self.name
