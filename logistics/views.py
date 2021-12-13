from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import BadHeaderError, send_mail
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View

from .models import TradeTransaction, ActionRecord
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from .forms import NewUserForm, form_validation_error
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django_tables2 import SingleTableView, MultiTableMixin
from .tables import TransactionTable, ActionRecordTable
from django_filters.views import FilterView

# Tab views: https://django-tabination.readthedocs.io/en/latest/usage.html


class PendingTransactionListView(SingleTableView, FilterView):
    model = TradeTransaction
    table_class = TransactionTable
    context_object_name = 'table'
    template_name = 'logistics/index.html'

    def get_context_data(self, **kwargs):
        context = super(PendingTransactionListView, self).get_context_data(**kwargs)
        context['table_transaction'] = TransactionTable(TradeTransaction.objects.filter(transaction_completed__isnull=True).order_by('transaction_date'), prefix="1-")
        context['table_action'] = ActionRecordTable(ActionRecord.objects.filter(processed__exact=False).order_by('action_completed'), prefix="2-")

        return context


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("logistics:index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm
    return render(request=request, template_name="logistics/register.html", context={"register_form": form})

# https://www.ordinarycoders.com/blog/article/django-user-register-login-logout


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="logistics/login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
        if associated_users.exists():
            for user in associated_users:
                subject = "Password Reset Requested"
                email_template_name = "logistics/password_reset_email.txt"
                c = {
                    "email": user.email,
                    'domain': 'https://ac1ded6e7549.ngrok.io/logistics/',
                    'site_name': 'DR Logistics',
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, c)
                try:
                    send_mail(subject, email, 'eiredrake@gmail.com', [user.email], fail_silently=False)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return redirect("logistics/password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="logistics/password_reset.html", context={"password_reset_form": password_reset_form})
