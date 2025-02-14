from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'capital', 'currency', 'timezone_1')
    search_fields = ('name', 'currency')
    list_filter = ('name', 'capital', 'currency', 'timezone_1')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('description', 'type', 'file', 'issuer', 'customer', 'due_date')
    search_fields = ('description', 'type')

@admin.register(Issuer)
class IssuerAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'parent', 'active', 'creation')
    search_fields = ('description', 'creation' )
    list_filter = ('name','parent', 'active', 'creation')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_id', 'description', 'active', 'creation')
    search_fields = ('description', 'creation' )
    list_filter = ('name','customer_id', 'active', 'creation')

@admin.register(UserCustomer)
class UserCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer', 'active', 'creation')
    search_fields = ('user', 'customer', 'active')
    list_filter = ('user','customer', 'active')

@admin.register(UserIssuer)
class UserIssuerAdmin(admin.ModelAdmin):
    list_display = ('user', 'issuer', 'active', 'creation')
    search_fields = ('user', 'issuer', 'active')
    list_filter = ('user','issuer', 'active')