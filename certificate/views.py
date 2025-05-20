import os
from io import BytesIO

import qrcode
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from pypdf import PdfReader, PdfWriter, Transformation
from rolepermissions.checkers import has_role
#from PyPDF2 import PdfReader, PdfWriter, Transformation
from rolepermissions.decorators import has_role_decorator
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.conf import settings
from django.db.models import Q
from pypdf import PdfReader, PdfWriter, Transformation


from .admin import UserIssuerAdmin
from .models import Certificate, Issuer, Customer, Country, UserCustomer, UserIssuer, CertificateHistory
from .forms import CertificateForm, IssuerForm, CustomerForm, CountryForm, UserIssuerForm, UserCustomerForm

from django.core import serializers

from .templatetags.custom_filters import user_has_role


# Create your views here.
#class CertificateListView(ListView):
#    model = Certificate
#    template_name = 'certificate/home.html'

def logout(request):
    logout(request)
    return HttpResponseRedirect('/login')

@login_required
def certificate_list_view(request):
    template = 'certificate/certificate-list.html'
    #user = User.objects.filter(username=request.user)
    ## If user is superuser, retrieve all records
    #if request.user.is_superuser:
    if request.user.is_superuser or has_role(request.user, 'internal_resource'):
        certificate = Certificate.objects.filter(status='APPROVED')
    ## now check whether user is an internal_resource an 
    #elif UserIssuer.objects.filter(user=request.user).exists() and has_role(request.user, 'internal_resource'):
        #issuer = UserIssuer.objects.filter(user=request.user, active=True)
        #certificate = Certificate.objects.filter(issuer__in=issuer.values_list('issuer'), status='APPROVED')
        #certificate = Certificate.objects.filter(status='APPROVED')
    ## If users is associated with a customer, retrieve all records of this customer
    elif UserCustomer.objects.filter(user=request.user).exists():
        customer = UserCustomer.objects.filter(user=request.user, active=True)
        certificate = Certificate.objects.filter(customer__in=customer.values_list('customer'), status='APPROVED')
        #certificate = Certificate.objects.all()
        #certificate = Certificate.objects.filter(user=c)
    else:
        certificate = []
    context = {'certificate': certificate}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def certificate_create(request):
    template = 'certificate/certificate-form.html'
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.uploader = request.user
            form.instance.status = 'DRAFT'
            # Save the uploaded file temporarily
            uploaded_file = form.cleaned_data['file']
            add_stamp = form.cleaned_data['add_stamp']

            temp_file_path = f'/tmp/{uploaded_file.name}'
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            # Generate a unique token (UUID)
            certificate_token = str(form.instance.token)

            # Generate the QR code
            qr_url = f'localhost/validate/{certificate_token}/'  # URL for validation
            qr_code = qrcode.make(qr_url)
            qr_buffer = BytesIO()
            qr_code.save(qr_buffer)
            qr_buffer.seek(0)

            # Save the QR code as an image
            qr_image_path = '/tmp/qr_code.png'
            qr_code.save(qr_image_path)


            # Create a PDF containing the QR code with ReportLab
            #qr_pdf_path = '/tmp/qr_code.pdf'
            #qr_canvas = canvas.Canvas(qr_pdf_path, pagesize=letter)

            #qr_canvas.drawImage(qr_image_path, 400, 50, width=100, height=100)  # Adjust position and size
            #qr_canvas.save()


            # Apply watermark using PyPDF2
            watermark_path = os.path.join(settings.STATIC_ROOT, 'watermark_1.pdf')
            #watermark_path =  './watermark_1.pdf'
            output_path = f'/tmp/watermarked_{uploaded_file.name}'

            reader_pdf = PdfReader(temp_file_path)
            watermark = PdfReader(watermark_path).pages[0]

            writer_pdf = PdfWriter()

            # Path to the stamp image
            stamp_image_path = os.path.join(settings.STATIC_ROOT, 'stamp.png')

            for page in reader_pdf.pages:
                # Adjusting the size of the watermark
                scale_x = page.mediabox.width / watermark.mediabox.width
                scale_y = page.mediabox.height / watermark.mediabox.height
                transformation = Transformation().scale(sx=scale_x, sy=scale_y)

                # Merging the watermark onto the PDF page
                page.merge_transformed_page(watermark, transformation, over=False)
                
                if add_stamp:
                    # Add the stamp image to the upper-right corner
                    page_width = page.mediabox.width
                    page_height = page.mediabox.height
                    stamp_width = 100  # Adjust the width of the stamp
                    stamp_height = 100  # Adjust the height of the stamp
                    stamp_x = page_width - stamp_width - 10  # 10 units from the right edge
                    stamp_y = page_height - stamp_height - 10  # 10 units from the top edge

                    # Create a temporary PDF with the stamp image
                    stamp_pdf_path = '/tmp/stamp.pdf'
                    c = canvas.Canvas(stamp_pdf_path, pagesize=(page_width, page_height))
                    c.drawImage(stamp_image_path, stamp_x, stamp_y, width=stamp_width, height=stamp_height)
                    c.save()

                    # Merge the stamp PDF onto the current page
                    stamp_pdf_reader = PdfReader(stamp_pdf_path)
                    stamp_page = stamp_pdf_reader.pages[0]
                    page.merge_page(stamp_page)
                
                writer_pdf.add_page(page)

            # Merge QR code PDF onto the last page
            #qr_pdf_reader = PdfReader(qr_pdf_path)
            #qr_page = qr_pdf_reader.pages[0]

            # Overlay QR code PDF onto the last page
            #last_page = writer_pdf.pages[-1]
            #last_page.merge_page(qr_page)

            # Save the watermarked file with QR code
            with open(output_path, 'wb') as output_file:
                writer_pdf.write(output_file)

            # Save the watermarked file to the model
            with open(output_path, 'rb') as watermarked_file:
                form.instance.file.save(f'watermarked_{uploaded_file.name}', watermarked_file)

            # Cleanup
            os.remove(output_path)
            # Clean up the temporary QR code image after use
            os.remove(qr_image_path)

            # Clean up temporary files
            os.remove(temp_file_path)
            #os.remove(qr_pdf_path)

            # Save the instance to the database
            certificate = form.save()

            # Record history
            CertificateHistory.objects.create(
                certificate=certificate,
                action='CREATED',
                user=request.user,
                comments='Certificate created'
            )

            # Retrieve the issuer and customer
            issuer = certificate.issuer
            customer = certificate.customer

            # Email appover to inform that certificate is ready for approval
            email_approver(issuer, customer)

            return redirect('certificate')
        else:
            print("Invalid Form")
            form = CertificateForm()
            context = {'form': form}
            return render(request, template, context)
    else:
        form = CertificateForm()
        context = {'form': form}
        return render(request, template, context)

@login_required
@has_role_decorator('approver')
def certificate_approval(request, pk):
    template = 'certificate/certificate-approval.html'
    certificate = get_object_or_404(Certificate, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            certificate.status = 'APPROVED'
            certificate.rejection_reason = ''
            certificate.save()

            # Record history
            CertificateHistory.objects.create(
                certificate=certificate,
                action='APPROVED',
                user=request.user,
                comments='Certificate approved'
            )

            # Inform customer that certificate was released
            send_email(certificate.issuer, certificate.customer, certificate.file.path)
        elif action == 'reject':
            rejection_reason = request.POST.get('rejection_reason')
            certificate.status = 'REJECTED'
            certificate.rejection_reason = rejection_reason
            certificate.save()

            # Record history
            CertificateHistory.objects.create(
                certificate=certificate,
                action='REJECTED',
                user=request.user,
                comments=rejection_reason
            )

            # Inform uploader that certificate was rejected
            email_rejection(certificate.uploader, rejection_reason)

        return redirect('certificate-approval-list')

    # Retrieve the history of actions taken on the certificate
    history = CertificateHistory.objects.filter(certificate=certificate).order_by('-timestamp')

    context = {
        'certificate': certificate,
        'history': history,
    }

    return render(request, template, context)


def certificate_validate(request, token):
    # Retrieve the certificate by token
    certificate = get_object_or_404(Certificate, token=token)
    template = 'certificate/certificate-validate.html'

    # Render a template to display certificate details
    context = {
        'data': certificate
    }
    return render(request, template, context)

@login_required
@has_role_decorator('certificate_admin')
def certificate_delete(request, pk):
    # if request.method == 'POST':
    #     certificate = get_object_or_404(Certificate, pk=pk)
    #     certificate.delete()
    #     return JsonResponse({'success': True})
    # return JsonResponse({'success': False})  
    certificate = get_object_or_404(Certificate, pk=pk)
    certificate.delete()
    return redirect('certificate')


@login_required
def certificate_detail(request, pk):
    template = 'certificate/detail.html'
    certificate = get_object_or_404(Certificate, pk=pk)
    fields = vars(certificate)
    context = {"fields": fields}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def certificate_update(request, pk):
    template = 'certificate/form.html'
    certificate = get_object_or_404(Certificate, pk=pk)
    form = CertificateForm(request.POST or None, instance=certificate)

    if form.is_valid():
        form.save()
        return redirect('certificate')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def issuer_list_view(request):
    template = 'certificate/issuer-list.html'
    issuer = Issuer.objects.all()
    context = {'issuer': issuer}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def issuer_create(request):
    template = 'certificate/form.html'
    form = IssuerForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('issuer')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def issuer_detail(request, pk):
    template = 'certificate/detail.html'
    issuer = get_object_or_404(Issuer, pk=pk)
    fields = vars(issuer)
    context = {"fields": fields}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def issuer_update(request, pk):
    template = 'certificate/form.html'
    issuer = get_object_or_404(Issuer, pk=pk)
    form = IssuerForm(request.POST or None, instance=issuer)

    if form.is_valid():
        form.save()
        return redirect('issuer')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def customer_list_view(request):
    template = 'certificate/customer-list.html'
    customer = Customer.objects.all()
    context = {'customer': customer}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def customer_create(request):
    template = 'certificate/form.html'
    form = CustomerForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('customer')

    context = {'form': form}
    return render(request, template, context)

@login_required
def customer_detail(request, pk):
    template = 'certificate/detail.html'
    customer = get_object_or_404(Customer, pk=pk)
    fields = vars(customer)
    context = {"fields": fields}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def customer_update(request, pk):
    template = 'certificate/form.html'
    customer = get_object_or_404(Customer, pk=pk)
    form = IssuerForm(request.POST or None, instance=customer)

    if form.is_valid():
        form.save()
        return redirect('customer')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def country_list_view(request):
    template = 'certificate/country-list.html'
    country = Country.objects.all()
    context = {'country': country}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def country_create(request):
    template = 'certificate/form.html'
    form = CountryForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('country')

    context = {'form': form}
    return render(request, template, context)

@login_required
def country_detail(request, pk):
    template = 'certificate/detail.html'
    country = get_object_or_404(Country, pk=pk)
    fields = vars(country)
    context = {"fields": fields}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def country_update(request, pk):
    template = 'certificate/form.html'
    country = get_object_or_404(Country, pk=pk)
    form = CountryForm(request.POST or None, instance=country)

    if form.is_valid():
        form.save()
        return redirect('country')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def user_issuer_list_view(request):
    template = 'certificate/user-issuer-list.html'
    data = UserIssuer.objects.all()
    context = {'data': data }
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def user_issuer_create(request):
    template = 'certificate/form.html'
    form = UserIssuerForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('user-issuer')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def user_issuer_update(request, pk):
    template = 'certificate/form.html'
    country = get_object_or_404(Country, pk=pk)
    form = UserIssuerForm(request.POST or None, instance=country)

    if form.is_valid():
        form.save()
        return redirect('user-issuer')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('internal_resource')
def user_customer_list_view(request):
    template = 'certificate/user-customer-list.html'
    data = UserCustomer.objects.all()
    context = {'data': data }
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def user_customer_create(request):
    template = 'certificate/form.html'
    form = UserCustomerForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('user-customer')

    context = {'form': form}
    return render(request, template, context)

@login_required
@has_role_decorator('site_admin')
def user_customer_update(request, pk):
    template = 'certificate/form.html'
    country = get_object_or_404(Country, pk=pk)
    form = UserCustomerForm(request.POST or None, instance=country)

    if form.is_valid():
        form.save()
        return redirect('user-customer')

    context = {'form': form}
    return render(request, template, context)


def email_customer(request):
    issuer = Issuer.objects.get(pk=request.POST.get('issuer'))
    customer = Customer.objects.get(pk=request.POST.get('customer'))
    
    print('Email customer')
    print('Issuer: '+ getattr(customer, 'name')) 
    print('Customer: '+ getattr(issuer, 'name'))

    subject = 'Calibration certificate from ' + getattr(issuer, 'name')
    context = {'issuer': getattr(issuer, 'name'),
               'customer': getattr(customer, 'name'),
               }
    template = 'certificate/email_customer.html'
    html_message = render_to_string(template, context)
    from_email = 'teste120120120@gmail.com'
    send_mail(subject=subject,
              message=strip_tags(html_message),
              from_email=from_email,
              recipient_list=['saulofmaciel@yahoo.com.br', 
                              getattr(customer, 'email'), 
                              getattr(issuer, 'email')],
              html_message=html_message,
              fail_silently=False)



def email_approver(issuer, customer):
    subject = 'Calibration certificate to ' + getattr(customer, 'name')
    context = {'issuer': getattr(issuer, 'name'),
               'customer': getattr(customer, 'name'),
               }
    template = 'certificate/email_approver.html'
    html_message = render_to_string(template, context)
    from_email = 'teste120120120@gmail.com'
    # from_email = 'support@dpbs.com.br'
    # to = [context.get('email'), from_email]
    # to = ['saulofmaciel@yahoo.com.br']
    send_mail(subject=subject,
              message=strip_tags(html_message),
              from_email=from_email,
              recipient_list=['saulofmaciel@yahoo.com.br', 
                              getattr(issuer, 'email')],
              html_message=html_message,
              fail_silently=False)
    

def email_rejection(uploader, rejection_reason):
    subject = 'Certificate Rejected'
    context = {'rejection_reason': rejection_reason}
    template = 'certificate/email_rejection.html'
    html_message = render_to_string(template, context)
    from_email = 'teste120120120@gmail.com'
    recipient_list = [uploader.email]

    msg = EmailMultiAlternatives(
        subject=subject,
        body=strip_tags(html_message),
        from_email=from_email,
        to=recipient_list,
    )
    msg.attach_alternative(html_message, 'text/html')
    msg.send()


def send_email(issuer, customer, file_path=None):
    subject = 'Calibration certificate from ' + getattr(issuer, 'name')
    context = {'issuer': getattr(issuer, 'name'),
               'customer': getattr(customer, 'name'),
               }
    template = 'certificate/email_customer.html'
    html_message = render_to_string(template, context)

    from_email = 'teste120120120@gmail.com'
    recipient_list = ['saulofmaciel@yahoo.com.br', 
                      getattr(customer, 'email'), 
                      getattr(issuer, 'email')]

    msg = EmailMultiAlternatives(
              subject=subject,
              body=strip_tags(html_message),
              from_email=from_email,
              to=recipient_list,
              )
    msg.attach_alternative(html_message, 'text/html')

    if file_path:
        with open(file_path, 'rb') as f:
            msg.attach(os.path.basename(file_path), f.read(), 'application/pdf')

    msg.send()

#    send_mail('Testing',
#              'Testing e-mail message',
#              'teste120120120@gmail.com',
#              ['saulofmaciel@yahoo.com.br'],
#              fail_silently=False)

@login_required
@has_role_decorator('approver')
def certificate_approval_list(request):
    template = 'certificate/certificate-approval-list.html'
    certificates = Certificate.objects.filter(Q(status='DRAFT') | Q(status='REJECTED'))
    context = {'certificates': certificates}
    print('Certificate-approval-list: ' + str(context))
    return render(request, template, context)


@login_required
@has_role_decorator('internal_resource')
def certificate_resubmit(request, pk):
    template = 'certificate/certificate-resubmit.html'
    certificate = get_object_or_404(Certificate, pk=pk)

    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=certificate)
        user_comment = request.POST.get('user_comment')
        if form.is_valid():
            form.instance.status = 'DRAFT'
            form.instance.rejection_reason = ''
            form.save()

            # Record history
            CertificateHistory.objects.create(
                certificate=certificate,
                action='RESUBMITTED',
                user=request.user,
                comments=user_comment or 'Certificate resubmitted'
            )

            # Email approver to inform that certificate is ready for approval
            email_approver(certificate.issuer, certificate.customer)
            return redirect('certificate-approval-list')

    else:
        form = CertificateForm(instance=certificate)

    # Retrieve the history of actions taken on the certificate
    history = CertificateHistory.objects.filter(certificate=certificate).order_by('-timestamp')

    context = {
        'form': form,
        'certificate': certificate,
        'history': history,
    }

    return render(request, template, context)
