'''

    Author: John Turner
    Version: 1.0
    Last Updated: 3/6/2015

    View for the functions related to the Shopping Cart

'''

from django.conf import settings
from base_app.CustomForm import CustomForm
from django import forms
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http import HttpRequest
from django_mako_plus.controller import view_function
from django.contrib.auth.decorators import login_required, permission_required
import base_app.models as hmod
from django_mako_plus.controller.router import get_renderer
from django.utils.translation import ugettext as _
from base_app.CustomWidgets import CustomSelect, CustomRadioRenderer
from django.contrib.auth import authenticate, login, logout
import datetime
from datetime import timedelta
import requests
from django.core.mail import send_mail
import smtplib

templater = get_renderer('account')

##########################################################################################
################################### FORM CLASS ###########################################
##########################################################################################

class ShippingForm(CustomForm):

    ''' Class for the form to be used adding shipping info. '''

    # List of constants for the states:
    ALASKA = 'AK'
    ALABAMA = 'AL'
    ARKANSAS = 'AR'
    ARIZON = 'AZ'
    CALIFORNIA = 'CA'
    COLORADO = 'CO'
    CONNECTICUT = 'CT'
    DELAWARE = 'DE'
    FLORIDA = 'FL'
    GEORGIA = 'GA'
    HAWAII = 'HI'
    IOWA = 'IA'
    IDAHO = 'ID'
    ILLINOIS = 'IL'
    INDIANA = 'IN'
    KANSAS = 'KS'
    LOUISIANA = 'LA'
    MASSACHUSETTS = 'MA'
    MARYLAND = 'MD'
    MAINE = 'ME'
    MICHIGAN = 'MI'
    MINNESOTA = 'MN'
    MISSOURI = 'MO'
    MISSISSIPPI = 'MS'
    MONTANA = 'MT'
    NORTH_CAROLINA = 'NC'
    NORTH_DAKOTA = 'ND'
    NEBRASKA = 'NE'
    NEW_HAMPSHIRE = 'NH'
    NEW_JERSEY = 'NJ'
    NEW_MEXICO = 'NM'
    NEVADA = 'NV'
    NEW_YORK = 'NY'
    OHIO = 'OH'
    OKLAHOMA = 'OK'
    OREGON = 'OR'
    PENNSYLVANIA = 'PA'
    RHODE_ISLAND = 'RI'
    SOUTH_CAROLINA = 'SC'
    SOUTH_DAKOTA = 'SD'
    TENNESSEE = 'TN'
    TEXAS = 'TX'
    UTAH = 'UT'
    VIRGINIA = 'VA'
    VERMONT = 'VT'
    WASHINGTON = 'WA'
    WISCONSIN = 'WI'
    WEST_VIRGINIA = 'WV'
    WYOMING = 'WY'

    # Choices list of tuples for the car_states field
    STATE_CHOICES = (
        (ALASKA, 'Alaska'),
        (ALABAMA, 'Alabama'),
        (ARKANSAS, 'Arkansas'),
        (ARIZON, 'Arizon'),
        (CALIFORNIA, 'California'),
        (COLORADO, 'Colorado'),
        (CONNECTICUT, 'Connecticut'),
        (DELAWARE, 'Delaware'),
        (FLORIDA, 'Florida'),
        (GEORGIA, 'Georgia'),
        (HAWAII, 'Hawaii'),
        (IOWA, 'Iowa'),
        (IDAHO, 'Idaho'),
        (ILLINOIS, 'Illinois'),
        (INDIANA, 'Indiana'),
        (KANSAS, 'Kansas'),
        (LOUISIANA, 'Louisiana'),
        (MASSACHUSETTS, 'Massachusetts'),
        (MARYLAND, 'Maryland'),
        (MAINE, 'Maine'),
        (MICHIGAN, 'Michigan'),
        (MINNESOTA, 'Minnesota'),
        (MISSOURI, 'Missouri'),
        (MISSISSIPPI, 'Mississippi'),
        (MONTANA, 'Montana'),
        (NORTH_CAROLINA, 'North Carolina'),
        (NORTH_DAKOTA, 'North Dakota'),
        (NEBRASKA, 'Nebraska'),
        (NEW_HAMPSHIRE, 'New Hampshire'),
        (NEW_JERSEY, 'New Jersey'),
        (NEW_MEXICO, 'New Mexico'),
        (NEVADA, 'Nevada'),
        (NEW_YORK, 'New York'),
        (OHIO, 'Ohio'),
        (OKLAHOMA, 'Oklahoma'),
        (OREGON, 'Oregon'),
        (PENNSYLVANIA, 'Pennsylvania'),
        (RHODE_ISLAND, 'Rhode Island'),
        (SOUTH_CAROLINA, 'South Carolina'),
        (SOUTH_DAKOTA, 'South Dakota'),
        (TENNESSEE, 'Tennessee'),
        (TEXAS, 'Texas'),
        (UTAH, 'Utah'),
        (VIRGINIA, 'Virginia'),
        (VERMONT, 'Vermont'),
        (WASHINGTON, 'Washington'),
        (WISCONSIN, 'Wisconsin'),
        (WEST_VIRGINIA, 'West Virginia'),
        (WYOMING, 'Wyoming'),
    )

    ## Class title ##
    title = "Shipping Information"
    link = "products/products"

    # Don't include the delete button.
    delete_button = False

    # Submit text
    submit_text = 'Continue'

    ## Form Inputs ##
    address1 = forms.CharField(required=True, max_length=100)
    address2 = forms.CharField(required=False, max_length=100)
    city = forms.CharField(required=True, max_length=100)
    state = forms.ChoiceField(required=True, choices=STATE_CHOICES, widget=CustomSelect)
    ZIP = forms.CharField(required=True)

##########################################################################################
################################### FORM CLASS ###########################################
##########################################################################################

class PaymentForm(CustomForm):

    ''' Class for the form for payment info. '''

    ## Class title ##
    title = "Payment Info"
    link = "products/products"

    # Don't include the delete button.
    delete_button = False

    # Submit text
    submit_text = 'Continue'

    ## Form Inputs ##
    credit_card_number = forms.CharField(required=True, max_length=100)
    card_holder_name = forms.CharField(max_length=100)
    card_company = forms.CharField(max_length=50)
    cvc = forms.IntegerField(required=True)
    expiration_month = forms.CharField(required=True, max_length=2)
    expiration_year = forms.CharField(required=True, max_length=4)
    ZIP = forms.CharField(required=True)
    confirmation = forms.CharField(required=False, max_length=500, widget=forms.HiddenInput())

    def clean(self):
        API_URL = 'http://dithers.cs.byu.edu/iscore/api/v1/charges'
        API_KEY = 'c07bb6c7c7d8ee46e96ca5b74f2ced53'

        r = requests.post(API_URL, data = {
            'apiKey': API_KEY,
            'currency': 'usd',
            'amount': self.request.session['total'],
            'type': self.cleaned_data['card_company'],
            'number': self.cleaned_data['credit_card_number'],
            'exp_month': self.cleaned_data['expiration_month'],
            'exp_year': self.cleaned_data['expiration_year'],
            'cvc': self.cleaned_data['cvc'],
            'name': self.cleaned_data['card_holder_name'],
            'description': 'Charge for:' + self.cleaned_data['card_holder_name'],
        })

        # parse response to a dictionary
        resp = r.json()
        print(self.request.session['total'])
        if 'error' in resp:
            raise forms.ValidationError("ERROR: " + resp['error'])
        else:
            self.cleaned_data['confirmation'] = resp['ID']

        return self.cleaned_data

##########################################################################################
################################# DEFAULT ACTION #########################################
##########################################################################################

@view_function
def process_request(request):

    # Define the view bag
    params = {}

    # Create a shopping cart in the session if it doesn't already exist
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Make sure the session variable recognizes the change
    request.session.modified = True

    # Dictionary for items
    items = {}

    # Grab the items from the shopping cart:
    for pid in request.session['cart']:

        try:
            item = hmod.Inventory.objects.get(id=pid)
        except hmod.Inventory.DoesNotExist:
            return HttpResponse('failed getting item')

        items[item] = request.session['cart'][pid]

    # Grab the rentals from the shopping cart:
    params['items'] = items
    params['total'] = 0

    return templater.render_to_response(request, 'ShoppingCart.html', params)

##########################################################################################
################################### ADD ITEM ACTION ######################################
##########################################################################################

@view_function
def add(request):

    # Define the view bag
    params = {}

    # Create the shopping cart if it already hasn't been
    if 'cart' not in request.session:
        request.session['cart'] = {}

    # Grab the item according to the data passed in the GET
    pid = request.REQUEST.get('id')
    quantity = int(request.REQUEST.get('quantity'))

    if pid in request.session['cart']:
        request.session['cart'][pid] += quantity
    else:
        request.session['cart'][pid] = quantity

    # Make sure the session variable recognizes the change
    request.session.modified = True

    return HttpResponseRedirect('/account/ShoppingCart/')



##########################################################################################
################################ REMOVE ITEM ACTION ######################################
##########################################################################################

@view_function
def remove(request):
    '''
        Removes an item from the shopping cart.
    '''

    # Define the view bag
    params = {}

    # Grab the item id
    pid = request.REQUEST.get('id')

    # Remove from the shopping cart
    if pid in request.session['cart']:

        del request.session['cart'][pid]

    request.session.modified = True

    return HttpResponseRedirect('/account/ShoppingCart/')



##########################################################################################
################################# SHIPPING INFO FUNCTION #################################
##########################################################################################

@view_function
@login_required(login_url='/homepage/login/')
def shipping_info(request):
    '''
        Sends the user to the shipping info page.
    '''

    # Define the view bag
    params={}

    # Grab the user
    try:
        user = hmod.User.objects.get(id=request.user.id)
    except hmod.User.DoesNotExist:
        return HttpResponseRedirect('/products/products/')

    # Pass in user data to the form
    form = ShippingForm(request, initial={
        'address1': user.address.address1,
        'address2': user.address.address2,
        'city': user.address.city,
        'state': user.address.state,
        'ZIP': user.address.ZIP,
        })

    if request.method == 'POST':

        # Validate the form
        form = ShippingForm(request, request.POST)

        if form.is_valid():

            # Return user to list
            return HttpResponseRedirect('/account/ShoppingCart.payment/')

    params['form'] = form

    return templater.render_to_response(request, 'ShippingInfo.html', params)

##########################################################################################
################################ CREDIT CARD INFO FUNCTION ###############################
##########################################################################################

@view_function
@login_required(login_url='/homepage/login/')
def payment(request):
    '''
        Sends the user to the payment page.
    '''

    # Define the view bag
    params={}

    # Pass in user data to the form
    form = PaymentForm(request)
    form.submit_text = "CHARGE NOW"
    form.confirmation = False

    if request.method == 'POST':

        # Validate the form
        form = PaymentForm(request, request.POST)

        if form.is_valid():

            request.session['confirmation'] = form.cleaned_data['confirmation']
            # Return user to list
            return HttpResponseRedirect('/account/ShoppingCart.confirmation/')

    params['form'] = form

    return templater.render_to_response(request, 'PaymentInfo.html', params)

##########################################################################################
################################### CONFIRMATION ACTION ##################################
##########################################################################################

@view_function
@login_required(login_url='/homepage/login/')
def confirmation(request):
    '''
        Sends the user to the confirmation page.
    '''

    ##ONLY EXECUTE IF REST CALL CONFIRMATION COMES BACK OF PAYMENT

    # Define the view bag
    params={}

    # Create Transaction
    transaction = hmod.Transaction()
    transaction.customer = request.user
    transaction.transaction_date = datetime.datetime.now()
    transaction.confirmation_id = request.session['confirmation']
    transaction.save()

    rentals = []
    products = []

    # Grab the items from the shopping cart:
    for pid in request.session['cart']:

        try:
            inv = hmod.Item.objects.get(id=pid)
            rentable = True
        except hmod.Item.DoesNotExist:
            try:
                inv = hmod.Inventory.objects.get(id=pid)
                rentable = False
            except hmod.Inventory.DoesNotExist:
                print('How is an item that does not exist getting into the cart?')
                return HttpResponse('Inventory doesnt exist')

        if not rentable:
            inv.quantity_on_hand -= request.session['cart'][pid]

            # make a sale line item in the transaction
            saleitem = hmod.SaleItem()
            saleitem.product = inv
            saleitem.quantity = request.session['cart'][pid]
            saleitem.amount = inv.specs.price * request.session['cart'][pid]
            saleitem.transaction = transaction

            saleitem.save()

            products.append(saleitem)

        else:
            inv.quantity_on_hand -= 1
            inv.times_rented += 1

            days = request.session['cart'][pid]
            #make a rental line item
            rentalitem = hmod.RentalItem()
            rentalitem.date_out = datetime.date.today()
            rentalitem.due_date = datetime.date.today() + timedelta(days=days)
            rentalitem.amount = inv.standard_rental_price * request.session['cart'][pid]
            rentalitem.item = inv
            rentalitem.transaction = transaction

            rentalitem.save()

            rentals.append(rentalitem)

        inv.save()

    ##ADD A LINE ITEM SHOWING AMOUNT PAID TO TRANSACTION
    params['rentals'] = rentals
    params['products'] = products

    request.session['cart'] = {}

    subject = "Receipt for your purchase"

    body = templater.render(request, 'receipt.html', params)

    send_mail(subject, body, 'derik.hasvold.backup@gmail.com', [request.user.email], html_message = body, fail_silently = False)

    return templater.render_to_response(request, 'confirmation.html', params)