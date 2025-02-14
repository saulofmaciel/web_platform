from django.urls import path
from . import views

urlpatterns = [
    path('', views.certificate_list_view, name='home'),
    #path('logout/', views.logout, name='logout'),

    path('certificate', views.certificate_list_view, name='certificate'),
    path('certificate-create', views.certificate_create, name='certificate-create'),
    path('certificate-detail/<int:pk>', views.certificate_detail, name='certificate-detail'),
    path('certificate-update/<int:pk>', views.certificate_update, name='certificate-update'),
    path('certificate-delete/<int:pk>', views.certificate_delete, name='certificate-delete'),
    path('certificate-approval-list', views.certificate_approval_list, name='certificate-approval-list'),
    path('certificate-approval/<int:pk>', views.certificate_approval, name='certificate-approval'),
    path('certificate-validate/<str:token>', views.certificate_validate, name='certificate-validate'),

    path('issuer', views.issuer_list_view, name='issuer'),
    path('issuer-create', views.issuer_create, name='issuer-create'),
    path('issuer-detail/<int:pk>', views.issuer_detail, name='issuer-detail'),
    path('issuer-update/<int:pk>', views.issuer_update, name='issuer-update'),

    path('customer', views.customer_list_view, name='customer'),
    path('customer-create', views.customer_create, name='customer-create'),
    path('customer-detail/<int:pk>', views.customer_detail, name='customer-detail'),
    path('customer-update/<int:pk>', views.customer_update, name='customer-update'),

    path('country', views.country_list_view, name='country'),
    path('country-create', views.country_create, name='country-create'),
    path('country-detail/<int:pk>', views.country_detail, name='country-detail'),
    path('country-update/<int:pk>', views.country_update, name='country-update'),

    path('user-issuer-view', views.user_issuer_list_view, name='user-issuer'),
    path('user-issuer-create', views.user_issuer_create, name='user-issuer-create'),
    path('user-issuer-update/<int:pk>', views.user_issuer_update, name='user-issuer-update'),

    path('user-customer-view', views.user_customer_list_view, name='user-customer'),
    path('user-customer-create', views.user_customer_create, name='user-customer-create'),
    path('user-customer-update/<int:pk>', views.user_customer_update, name='user-customer-update'),

]
