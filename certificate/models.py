import uuid

from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.functions import Now
from django.utils import timezone
from django.contrib.auth.models import User

# Define file storage
fs = FileSystemStorage(location='files')

# Create your models here.

class Country(models.Model):
    country_id      = models.CharField(max_length=2)
    name            = models.CharField(max_length=200)
    capital         = models.CharField(blank=True, max_length=200)
    continent       = models.CharField(blank=True, max_length=200)
    currency        = models.CharField(blank=True, max_length=50)
    timezone_1      = models.CharField(blank=True, max_length=50)
    timezone_2      = models.CharField(blank=True, max_length=50)
    timezone_3      = models.CharField(blank=True, max_length=50)
    timezone_4      = models.CharField(blank=True, max_length=50)
    language_1      = models.CharField(blank=True, max_length=50)
    language_2      = models.CharField(blank=True, max_length=50)
    language_3      = models.CharField(blank=True, max_length=50)

    def __str__(self):
        return self.country_id

class Issuer(models.Model):
    name            = models.CharField('Name', max_length=150)
    issuer_id       = models.CharField('Issuer ID', max_length=150)
    description     = models.CharField('Description', max_length=200)
    parent          = models.ForeignKey(to='Issuer', null=True, blank=True, on_delete=models.PROTECT)
    contact         = models.CharField('Contact', blank=True, max_length=200)
    telephone       = models.CharField('Telephone', blank=True, max_length=50)
    email           = models.CharField('Email', blank=True, max_length=200)
    country         = models.ForeignKey(Country, blank=True, on_delete=models.PROTECT)
    state           = models.CharField('State', max_length=50)
    city            = models.CharField('Postal code', blank=True, max_length=50)
    postal_code     = models.CharField('Address 1', blank=True, max_length=20)
    address_2       = models.CharField('Address 2', blank=True, max_length=200)
    address_3       = models.CharField('Address 3', blank=True, max_length=200)
    address_4       = models.CharField('Address 4', blank=True, max_length=200)
    active          = models.BooleanField('Active', default=False)
    creation        = models.DateTimeField('Creation Date', default=timezone.now)

    def __str__(self):
        return str(self.name)

class Customer(models.Model):
    name            = models.CharField(verbose_name='Name', max_length=150)
    customer_id     = models.CharField(verbose_name='Customer ID', max_length=150)
    description     = models.CharField(verbose_name='Description', max_length=200)
    parent          = models.ForeignKey(to='Customer', null=True, blank=True, on_delete=models.PROTECT)
    contact         = models.CharField(verbose_name='Contact', blank=True, max_length=200)
    telephone       = models.CharField(verbose_name='Telephone', blank=True, max_length=50)
    email           = models.CharField(verbose_name='Email', max_length=200)
    country         = models.ForeignKey(Country, on_delete=models.PROTECT)
    state           = models.CharField(verbose_name='State', blank=True, max_length=50)
    city            = models.CharField(verbose_name='Postal code', blank=True, max_length=50)
    postal_code     = models.CharField(verbose_name='Address 1', blank=True, max_length=20)
    address_2       = models.CharField(verbose_name='Address 2', blank=True, max_length=200)
    address_3       = models.CharField(verbose_name='Address 3', blank=True, max_length=200)
    address_4       = models.CharField(verbose_name='Address 4', blank=True, max_length=200)
    active          = models.BooleanField(verbose_name='Active', default=False)
    creation        = models.DateTimeField(verbose_name='Creation Date', default=timezone.now)

    def __str__(self):
        return str(self.name)

class UserIssuer(models.Model):
    user            = models.ForeignKey(User, on_delete=models.PROTECT)
    issuer          = models.ForeignKey(Issuer, on_delete=models.PROTECT)
    active          = models.BooleanField('Active', default=False)
    creation        = models.DateTimeField('Creation Date', default=timezone.now)

    def __str__(self):
        return str('user: %s issuer: %s' % (self.user, self.issuer))

class UserCustomer(models.Model):
    user            = models.ForeignKey(User, on_delete=models.PROTECT)
    customer        = models.ForeignKey(Customer, on_delete=models.PROTECT)
    active          = models.BooleanField('Active', default=False)
    creation        = models.DateTimeField('Creation Date', default=timezone.now)

    def __str__(self):
        return str('user: %s customer: %s' % (self.user, self.customer))


class Certificate(models.Model):
    CERT_TYPES = {
        'CA': 'Calibration',
        'DE': 'Degree',
    }
    STATUSES ={
        'DRAFT': 'Draft',
        'APPROVED': 'Approved',
    }
    description         = models.CharField('Certificate description', max_length= 200)
    type                = models.CharField('Certificate Type', max_length=2, choices=CERT_TYPES)
    file                = models.FileField(null=True, storage=fs)
    language            = models.CharField('Language', max_length=50)
    creation            = models.DateTimeField('Creation date time', auto_now_add=True)
    issuer              = models.ForeignKey(Issuer, null=True, related_name='issuer_of', on_delete=models.PROTECT)
    uploader            = models.ForeignKey(User, null=True, related_name='uploader_of', on_delete=models.PROTECT)
    customer            = models.ForeignKey(Customer, null=True, related_name='customer_of', on_delete=models.PROTECT)
    upload              = models.DateTimeField('Upload date time', auto_now_add=True)
    status              = models.CharField('Status', max_length=30, choices=STATUSES, default='DRAFT')
    token               = models.CharField('Token', max_length=36, unique=True, default=uuid.uuid4, editable=False)
    due_date            = models.DateField( null=True , blank=True, default='2099-12-31')

    def __str__(self):
        return self.description
