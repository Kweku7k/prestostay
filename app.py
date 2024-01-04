import csv
import datetime
from datetime import timedelta
import json
import os
import random
from flask import Flask, flash, jsonify,redirect, session,url_for,render_template, request
from flask_login import UserMixin, login_user, logout_user, current_user, LoginManager, login_required
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, func
from itsdangerous import Serializer
from flask_bcrypt import Bcrypt
from dataprocessing import convertToNumber, createRooms, getOccupants
from utils import apiResponse, create_folder, send_sms, sendAnEmail, sendMnotifySms, sendTelegram, sendVendorTelegram, reportTelegram  
from forms import *
import pprint
import time
import requests
import geocoder
from urllib.parse import quote as url_quote
from sqlalchemy import or_


app=Flask(__name__)
bcrypt = Bcrypt(app)
sandboxDb = "postgresql://postgres:adumatta@database-1.crebgu8kjb7o.eu-north-1.rds.amazonaws.com:5432/staysandbox"
app.config['SECRET_KEY'] = 'c280ba2428b2157916b13s5e0c676dfde'
app.config['SQLALCHEMY_DATABASE_URI']= sandboxDb
googlerecaptchakey = "6LeVvCEpAAAAAJpamR_cN4meMFiMbuLO32Z3wrUu"


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mapsApiKey = os.environ.get('GOOGLEMAPSAPIKEY')

prestoUrl = "https://prestoghana.com"
baseUrl = "https://stay.prestoghana.com"

merchantID = "ec5fb5b5-2b80-4a9a-b522-24c90912f106"

environment = os.environ["ENVIRONMENT"]
# This value confirms the server is not null
server = os.environ["SERVER"]
# server = "SERVER"


#  ----- LOGIN MANAGER
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get_or_404(user_id)

# ------ MODELS

class Suggestions(db.Model):
    tablename = ['Suggestions']

    id = db.Column(db.Integer, primary_key=True)
    suggestion = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    total = db.Column(db.Integer)
    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'))


    def __repr__(self):
        return f"Suggestion('id: {self.id}', 'suggestion:{self.suggestion}', 'slug:{self.slug}')"
  



class Feedback(db.Model):
    tablename = ['Feedback']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    appId = db.Column(db.String)
    sender = db.Column(db.String)
    title = db.Column(db.String)
    message = db.Column(db.String)
    emailAddress = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    date_resolved = db.Column(db.DateTime)
    resolved = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return f"Feedback('id: {self.id}', 'Name:{self.name}', 'Phone:{self.sender}' , 'Resolved:{self.resolved}')"



class Refund(db.Model):
    tablename = ['Refund']

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.String)
    roomNumber = db.Column(db.String)
    name = db.Column(db.String)
    listingSlug = db.Column(db.String)
    userId = db.Column(db.String)
    reason = db.Column(db.String)
    account = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    datepaid = db.Column(db.DateTime)
    financeApprove = db.Column(db.Boolean, default=False)
    adminApprove = db.Column(db.Boolean, default=False)

    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'))

    def __repr__(self):
        return f"Refund('id: {self.id}', 'user:{self.userId} - {self.name} - {self.listingSlug}', 'date:{self.date}')"
  
    
class TransactionType(db.Model):
    tablename=['TransactionType']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    superListing = db.Column(db.String)
    maxAmount = db.Column(db.Float)
    minAmount = db.Column(db.Float)

    def __repr__(self):
        return f"TransactionType('id: {self.id}', 'name:{self.name}', 'superListing:{self.superListing}')"
    
class EmergencyContacts(db.Model):
    tablename=['EmergencyContacts']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    relationship = db.Column(db.String)
    userId = db.Column(db.String)
    username = db.Column(db.String)
    phoneNumber = db.Column(db.String)

    def __repr__(self):
        return f"EmergencyContact('id: {self.id}', 'name:{self.name}', 'user:{self.username}')"
    

class Listing(db.Model):
    tablename = ['Listing']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    # password = db.Column(db.String(), primary_key=False, unique=False, nullable=False)
    phone = db.Column(db.String)
    chatId = db.Column(db.String)
    logo = db.Column(db.String)
    description = db.Column(db.String)
    expectedRevenue = db.Column(db.Float, default=0.0)
    amountRecieved = db.Column(db.Float, default=0.0)
    amountDue = db.Column(db.Float, default=0.0)
    description = db.Column(db.String)
    location = db.Column(db.String)
    locationTag = db.Column(db.String)
    images = db.Column(db.String)
    slug = db.Column(db.String)
    type = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    suggestions = db.Column(db.String)

    def __repr__(self):
        return f"Listing('id: {self.id}', 'name:{self.name}',  'slug:{self.slug}', 'location:{self.location}')"

class SubListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    description = db.Column(db.String)
    listingId = db.Column(db.String)
    occupants = db.Column(db.Integer) #bedsAvailable
    quantity = db.Column(db.Integer, default=0)
    vacantSpace = db.Column(db.Integer, default=0)
    divideCost = db.Column(db.Boolean, default=True)
    superListing = db.Column(db.String)
    chatId = db.Column(db.String)
    listingSlug = db.Column(db.String)
    accountType = db.Column(db.String)
    # dismissable fields
    block = db.Column(db.String)
    roomId = db.Column(db.String)
    bedsAvailable = db.Column(db.String)
    bedsTaken = db.Column(db.String)
    location = db.Column(db.String)
    size = db.Column(db.String)
    status = db.Column(db.String)
    pricePerBed = db.Column(db.String)
    vacant = db.Column(db.Boolean, default=True)

    slug = db.Column(db.String)
    
    def __repr__(self):
        return f"SubListing('id: {self.id}', 'name:{self.name}', 'superlisting:{self.listingId}'. '{self.superListing}')"

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    listingId = db.Column(db.String)

    def __repr__(self):
        return f"Listing('id: {self.id}', 'name:{self.suggestion}', 'location:{self.location}')" 

class TenancyPeriod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listingId = db.Column(db.String)
    listingSlug = db.Column(db.String)
    name = db.Column(db.String)
    date_added = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    reservation_start_date = db.Column(db.DateTime)
    reservation_end_date = db.Column(db.DateTime)
    reservation_minimum = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"TenancyPeriod('id: {self.id}', 'name:{self.active}', 'location:{self.listingSlug}')" 

class LocationTagEnum(Enum):
    on_campus = 'on_campus'
    off_campus = 'off_campus'

class User(db.Model, UserMixin):
    """Model for user accounts."""
    __tablename__ = 'users'

    name = db.Column(db.String)

    firstname = db.Column(db.String)
    middlename = db.Column(db.String)
    surname = db.Column(db.String)
    joined = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    checkin = db.Column(db.DateTime)

    phone = db.Column(db.String)
    role = db.Column(db.String, default="user")
    indexNumber = db.Column(db.String)
    hostel = db.Column(db.String)
    listing = db.Column(db.String)
    listingSlug = db.Column(db.String)
    sublisting = db.Column(db.String)
    roomNumber = db.Column(db.String)
    status = db.Column(db.String, default="Pending")
    chatId = db.Column(db.String)
    telegramBot = db.Column(db.String)
    fullAmount = db.Column(db.Float, default=0)
    balance = db.Column(db.Float, default=0)
    paid = db.Column(db.Float, default=0)
    type = db.Column(db.String, default="payment")
    message = db.Column(db.String)
    callbackUrl = db.Column(db.String)
    availablebalance = db.Column(db.Float, default=0)
    percentage = db.Column(db.Float, default=0)
    role = db.Column(db.String, default="user")
    course = db.Column(db.String)
    level = db.Column(db.String)
    id = db.Column(db.Integer,primary_key=True)
    dailyDisbursal = db.Column(db.Boolean, default=False)
    username = db.Column(db.String,nullable=False,unique=False)
    email = db.Column(db.String())
    password = db.Column(db.String(), primary_key=False, unique=False, nullable=False)
    # dailyDisbursal = db.Column(db.Boolean, default=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User ('{self.username}', ' - {self.sublisting}', 'Listing - {self.listing}')"


class Transactions(db.Model):
    tablename = ['Transactions']

    id = db.Column(db.Integer, primary_key=True)
    appId = db.Column(db.String)
    userId = db.Column(db.String, nullable=False)
    username = db.Column(db.String)
    roomID = db.Column(db.String)
    listing = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    amount = db.Column(db.Float)
    total = db.Column(db.Float)
    charges = db.Column(db.Float)
    balanceBefore = db.Column(db.Float)
    balanceAfter = db.Column(db.Float)
    pending = db.Column(db.Boolean, default=True)
    requested = db.Column(db.Boolean, default=False)
    paid = db.Column(db.Boolean, default=False)
    account = db.Column(db.String)
    network = db.Column(db.String)    
    transactionType = db.Column(db.String)
    ledgerEntryId = db.Column(db.Integer)
    ref = db.Column(db.String) #notsupersure?
    prestoTransactionId = db.Column(db.Integer)
    channel = db.Column(db.String)
    telegramChatId = db.Column(db.String)

    
    def __repr__(self):
        return f"Transaction(': {self.id}', 'Amount:{self.amount}', 'User:{self.username}', 'Paid:{self.paid}')"

class LedgerEntry(db.Model):
    tablename = ['LedgerEntry']

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    amount = db.Column(db.Float)
    listing = db.Column(db.String)
    count = db.Column(db.Integer, default=0)
    balanceBefore = db.Column(db.Float)
    balanceAfter = db.Column(db.Float)
    transactionId = db.Column(db.Integer)
    type = db.Column(db.String)
    ref = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"Payment Ghc('{self.amount}', ' - {self.userId}')"

# ------ FUNCTIONS

def reportError(e):
    print(e)
    sendTelegram(e)
    pass

def getListing(id):
    print(id)
    try:
        if type(id) == int:
            listing = Listing.query.get_or_404(id)
        else:
            listing = Listing.query.filter_by(slug=id).first()
    except Exception as e:
        print(e)
        print("Couldnt find a listing with this id.")
        listing = None
    return Listing.query.get_or_404(1)

def getAllListings(suggestion=None):
    if suggestion == None:
        listings = Listing.query.all()
    else:
        listings = Listing.query.filter_by(suggestion=suggestion).all()
    return listings

def createListing(body):
    print(body)
    new_listing = Listing(
        name=body.get("name"),
        description=body.get("description"),
        location=body.get("location", "Greater Accra"),
        locationTag=body.get("locationTag", "Accra"),
        email = body.get("email"),
        password = body.get("password"),
        )
    try:
        db.session.add(new_listing)
        db.session.commit()
    except Exception as e:
        print(e)
        reportError(e)
    return body


def fetch_cities_in_accra():
    # Replace 'YOUR_API_KEY' with your actual Google Maps API key.
    api_key = mapsApiKey
    
    # Define the base URL for the Places API text search.
    base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'

    # Specify the query to search for cities in the Accra region.
    query = 'cities in Accra, Ghana'

    # Construct the request URL.
    request_url = f'{base_url}query={query}&key={api_key}'

    try:
        # Send the HTTP request to the API.
        response = requests.get(request_url)

        print(response)
        
        # Check if the request was successful (HTTP status code 200).
        if response.status_code == 200:
            data = response.json()
            # print(data)
            
            # Extract the results containing city names.
            results = data.get('results', [])
            
            if results:
                city_names = [result['name'] for result in results]
                pprint.pprint(city_names)
                return city_names
            else:
                return []
        else:
            print(f'Error: {response.status_code} - {response.text}')
            return []
    except Exception as e:
        print(f'An error occurred: {e}')
        return []


def createSubListing(body, listing):
    print(body)
    cleanedName = body.get("name").replace(" ", "").lower()
    new_sub_listing = SubListing(
        name=body.get("name"),
        description=body.get("description"),
        listingId=listing.id,
        superListing=listing.slug,
        listingSlug=listing.slug,
        price=body.get("price"),
        slug = listing.slug+"-"+cleanedName
    )

    try:
        db.session.add(new_sub_listing)
        db.session.commit()
        flash(f'' + new_sub_listing.name + " has been added.")

    except Exception as e:
        print(e)
        reportError(e)

    return body


def createNewUser(body):
    print(body)
    print(body.get("username"))

    newUser = User(
        name=body.get("name"),
        email = body.get("email"),
        username = body.get("username"),
        phone=body.get("phone"),
        chatId=body.get("chatId"),
        telegramBot=body.get("telegramBot"),
        balance=body.get("balance"),
        type=body.get("type"),
        message=body.get("message"),
        callbackUrl=body.get("callbackUrl"),
        availablebalance=body.get("availablebalance"),
        percentage=body.get("percentage"),
        role=body.get("availablebalance")
        )

    try:
        db.session.add(newUser)
        db.session.commit()
    except Exception as e:
        print(e)
        reportError(e)
    return body

def deleteListing(id):
    startTime = time.now()
    listing = getListing(id)
    if listing != None:
        code = 200
        db.session.delete(listing)
        message = str(listing.id) +". " +listing.name + " has been deleted successful"
        data = getAllListings()
    else:
       message = "There was a problem deleting this data"
       data = listing
    return apiResponse(code, message, data, startTime)

def stay_user():
    userId = session.get('stay_user_id', None)
    if userId == None:
        flash(f'There is no account signed it at the moment. Please authenticate to continue')
        return redirect(url_for('findme'))
    else: 
        return User.query.get_or_404(userId)


def getkeys(json_body):
    # Parse the JSON data into a Python dictionary
    data_dict = json.loads(json_body)

    # Extract the keys from the dictionary
    keys = data_dict.keys()

    # Convert the keys to a list if needed
    keys_list = list(keys)

    # Print the keys
    print(keys_list)

def createTransaction(body):
    newTransaction = Transactions(
        userId=body.get("userId"),
        appId=body.get("appId"),
        username=body.get("username"),
        roomID=body.get("roomID"),
        amount=body.get("amount"),
        listing=body.get("listing"),
        balanceBefore=body.get("balanceBefore"),
        account = body.get("account"),
        network = body.get("network"),
        channel = body.get("channel"),
        transactionType = body.get('transactionType'),
        total=body.get('total')
    )

    try:
        db.session.add(newTransaction)
        db.session.commit()
    except Exception as e:
        reportError(e)
        flash('There was an error creating this transaction!')

    return newTransaction

def externalPay(transaction):
    print("Triggering External Pay Transaction!")

    paymentInfo = {
        "name":transaction.username,
        "transactionId":transaction.id,
        "amount":transaction.amount,
        "currency":"GHS",
        "reference":transaction.username,
        "charges":0.03,
        "callbackUrl":baseUrl+"/confirm/"+str(transaction.id)
    }

    print(paymentInfo)

    try:    
        response = requests.post(prestoUrl+"/externalpay/"+transaction.appId, json=paymentInfo)
        transaction.ref = response.json()["transactionId"]
    except Exception as e:
        print(e)
        print("Creating External Transaction failed!")

    print(response)
    print(response.json())
    return response.json()


def payWithPrestoPay(transaction):
# TODO: Edit to trigger accurate payment
# find user?
    user = User.query.get_or_404(transaction.userId)
    print(user)
    description = "nothing here yet"
    paymentInfo = {
            "appId":"PrestoSolutions", #tca kaf
            "ref":transaction.ref,
            "description":description,
            "reference":user.username+"-"+str(transaction.id),
            "paymentId":user.id, 
            "phone":"0"+transaction.account[-9:],
            "amount":transaction.amount,
            "total":0.10,
            "recipient":"external", #TODO:Change!
            "percentage":"3",
            "callbackUrl":baseUrl+"/verifyTransaction/"+str(transaction.id),#TODO: UPDATE THIS VALUE
            "firstName":user.username,
            "network":transaction.network
        }

    response = requests.post(prestoUrl+"/korba", json=paymentInfo)

    print("-----prestoPay------")
    print(paymentInfo)
    print(prestoUrl)
    status = response
    status = response.status_code
    print(status)
 
    try:
        transaction.ref = response.json()["transactionId"]
        transaction.requested = True
        transaction.prestoTransactionId = response.json()["transactionId"]
        db.session.commit()
    except Exception as e:
        print("e")
        print(e)
        print("Couldnt set transaction reference!")

    # if transaction.network == "CARD"

    if transaction.network == 'CARD':
                # create korba - presto transaction here and assign to orderId
        print(transaction.network)
        # transaction = korbaCheckout(candidate, amount, phone)
        description = "Paying GHS"+ str(transaction.amount) +" to "+ str(transaction.listing) + " for "+str(transaction.username) + "."
        callbackUrl = baseUrl+"/"+str(transaction.id)
        print(callbackUrl)
        
    responseBody = {
        "transactionId":transaction.id,
        "orderId":prestoUrl+transaction.ref,
        "merchantID" : merchantID ,
        "description" : "Paying "+ str(transaction.amount) +" for "+ str(user.username) + " in " + str(transaction.listing) + ".",
        "callbackUrl" :  baseUrl+str(transaction.id)
    }

    return responseBody

def confirmPrestoPayment(transaction):
    r = None
    try:
        r = requests.get(prestoUrl + '/verifykorbapayment/'+str(transaction.ref)).json()
    except Exception as e:
        print(e)
    
    print(r)
    print("--------------status--------------")
    status = r.get("status", "failed")
    print(status)


    print("--------------server--------------")
    print(server)

    print("--------------transaction channel--------------")
    print(transaction.channel)

    if status == 'success' or environment == 'DEV' and server == "LOCAL" or transaction.channel == 'BANK':

        print("Attempting to update transctionId: " +str(transaction.id) + " to paid! in " + environment + "environment || SERVER:" + server)
        
        # findtrasaction, again because of the lag.
        state = Transactions.query.get_or_404(transaction.id)
        if state.paid != True:
            try:
                state.paid = True
                db.session.commit()
                print("Transaction : "+str(transaction.id) + " has been updated to paid!")

            except Exception as e:
                print("Failed to update transctionId: "+str(transaction.id )+ " to paid!")
                app.logger.error(e)
                reportError(e)

            return True
        return False

    else:
        print(str(transaction.id) + " has failed.")
        return False

def updateUserBalance(transaction):
    # find vote with same transaction id.
    alreadyCounted = LedgerEntry.query.filter_by(transactionId = transaction.id).first()
    if alreadyCounted != None: #If found.
        return None

    try: #Create a new vote
        newLedgerEntry = LedgerEntry(userId=transaction.userId, name=transaction.username, listing = transaction.listing, amount=transaction.amount, transactionId=transaction.id)
        db.session.add(newLedgerEntry)
        db.session.commit()
    except Exception as e:
        app.logger.error(e)
        reportError(str(e))
        app.logger.error("Couldnt create ledgerEntry for " + transaction.username)

    try: #SET UP DECIMAL POINTS
        user = User.query.get_or_404(int(transaction.userId))
        listing = Listing.query.filter_by(slug = user.listingSlug).first()
        
        transaction.balanceBefore = user.balance
        transaction.balanceAfter = user.balance - newLedgerEntry.amount

        listing.amountRecieved += newLedgerEntry.amount
        listing.amountDue -= newLedgerEntry.amount

        print("----------------------- Updating balance ---------------------------")
        print("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        sendTelegram("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        
        user.balance -= newLedgerEntry.amount
        user.paid += newLedgerEntry.amount
        
        transaction.ledgerEntryId = newLedgerEntry.id

        db.session.commit()

        print("----------------------- Updated Successfully! ---------------------------")

    except Exception as e:
        app.logger.error("Updating user " + user.username + " balance has failed." )
        app.logger.error(e)
        reportError(str(e))

    return newLedgerEntry


def changeToDateTime(date_string):
    date_format = "%m/%d/%Y"
    # Use datetime.strptime to parse the string and convert it to a datetime object
    date_obj = datetime.strptime(date_string, date_format)

def uploadTransactions(filename):
    csv_file_path = filename  # Replace with the path to your CSV file
    message = "All Transactions were updated successfully!"

    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        disimilarNames = []
        
        for row in csv_reader:
            print(row)
            print("====================================")
            print("Updating Data For " + row["Full Name"])

            try:
                transaction = Transactions(appId=row["listingSlug"], username=row["Full Name"], amount=row["Amount Paid"], channel = row["Payment Method"], paid=True  )
                users = User.query.filter_by(username=transaction.username)
                print(users.all())
                print(users.count())

                transaction.date = datetime.datetime.strptime(row["Date of Transaction"], "%m/%d/%Y")

                if users.count() != 1:
                    disimilarNames.append(row["Full Name"])
                else:
                    db.session.add(transaction)
            except Exception as e:
                message = "There seems to have been an issue with the upload"
                print(e)
        
        print(disimilarNames)

            

        db.session.commit()
            
    return message

def uploadData(filename, format=False):
    csv_file_path = filename  # Replace with the path to your CSV file
    message = "New Users updated successfully!"


    if format == True and os.environ.get("SERVER") == "LOCAL":
        for u in User.query.all():
            db.session.delete(u)

    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            print(row)

            if row.get('Number'):
                try:
                    emailThingy = random.sample(range(1, 7000 + 1), 1)[0]
                    user = User(username = row["Name"], password = "0000",email = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+str(emailThingy)+"@prestoghana.com", phone = row["Number"], indexNumber=row["Index Number"], listing=row["Listing"], paid=convertToNumber(row["Paid"]), roomNumber=row["Room Number"], fullAmount=convertToNumber(row["Full Amount"]), balance=convertToNumber(row["Balance"]), listingSlug=row["listingSlug"] )
                    db.session.add(user)
                except Exception as e:
                    message = "There seems to have been an issue with the upload"
                    print(e)

                db.session.commit()
    return message

def logger(param):
    print(param)
    sendTelegram(param)
    return "Successful"

def uploadRoomData(filename, listing, format=False):
    csv_file_path = filename  # Replace with the path to your CSV file
    message = "New Rooms updated successfully!"

    if format == True:
        for u in SubListing.query.all():
            db.session.delete(u)

    print("Attempting Create New Sublistings for " + listing.name)

    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)

        # first_10_rows = list(csv_reader)[:30]
        
        for row in csv_reader:
            print(row)
            sublistingName = row["Room Number"]
            foundSubListing = SubListing.query.filter_by(name=sublistingName).first()

            print("---------------")
            print(foundSubListing)
            print("---------------")


            if foundSubListing == None:
                block = sublistingName[0]
                roomId=sublistingName.replace(block, '')
                try:
                    occupants = 1 if row["Vacant"] == 'FALSE' else 0
                    # sublisting = SubListing(name = row["Name"], block=row["Block"], roomId=row["RoomId"], bedsAvailable=row["Beds Available"], bedsTaken = row["Beds Taken"], location = row["Location"], size=row["Size"], status = row["Vacancy Status"], pricePerBed=row["Price per bed"], price=row["Price"], listingId=row["Listing Id"], superListing=row["Super Listing"] )
                    sublisting = SubListing(name = row["Room Number"], block=block, roomId=roomId, bedsAvailable=1, bedsTaken = 1, quantity=1, occupants=occupants, location = row["Location"], size=row["Size"], status = True, pricePerBed=convertToNumber(row["PricePerBed"]), price=convertToNumber(row["Price"]), listingId=listing.id, superListing=listing.slug )
                    db.session.add(sublisting)
                    db.session.commit()


                except Exception as e:
                    message = "There seems to have been an issue with the upload"
                    errormessage = e
                    print(errormessage)
            else:
                try:
                    foundSubListing.quantity += 1
                    if row["Vacant"] == 'FALSE':
                        foundSubListing.occupants += 1
                    else:
                        foundSubListing.vacantSpace += 1
                    db.session.commit()
                except Exception as e:
                    print("---------------")
                    print(errormessage)
                    print("---------------")

            
            
    return message


   
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error(error)
    print("error")
    print(error)

    error_message = str(error)

      # Check if the error_message contains "500 Internal Server Error" (default Flask message)
    # if error_message == "500 Internal Server Error":
        # If it's the default message, try to extract the original exception message
    original_exception = getattr(error, "original_exception", None)
    if original_exception:
        error_message = str(original_exception)
        print("====================")
        print(error_message)

        reportTelegram(error_message)
    
    return render_template('500.html'), 500


        


# ----- ROUTES

@app.route('/issue', methods=['GET', 'POST'])
@app.route('/issue/<string:appId>', methods=['GET', 'POST'])
def issue(appId=None):
    form = FeedbackForm()

    if request.method == 'POST':
        print(request.form)
        recaptcha_response = request.form['g-recaptcha-response']

         # Verify the reCAPTCHA response
        verify_url = f'https://www.google.com/recaptcha/api/siteverify?secret={googlerecaptchakey}&response={recaptcha_response}'
        verify_response = requests.post(verify_url)
        verify_data = verify_response.json()

        if verify_data['success']:
            
            print("This is a post request")
            if form.validate_on_submit():
                print("Form has been validated")
                
                print(form.data)
                sendTelegram(f'New Feedback recieved. {json.dumps(form.data)}')

                try:
                    newFeedback = Feedback(sender=form.phoneNumber.data, title=form.title.data, message=form.issue.data, emailAddress=form.email.data, name=form.name.data, appId=appId)
                    db.session.add(newFeedback)
                    db.session.commit()
                except Exception as e:
                    print(e)

                if newFeedback is not None:
                    # message = 'Hi '+newFeedback.name+', <br/> Your issue has been raised and is being resolved. Someone from support will reach out if neccessary. Thank You. <br/> <br/> Powered By PrestoGhana'
                    # if form.email.data:
                    #     sendMail(form.email.data,'Your feedback has been recieved', message )
                    
                    if form.phoneNumber.data is not None:
                        smsmessage = 'Hi '+newFeedback.name+', \n Your issue has been raised and is being resolved. Someone from support will reach out if neccessary. Thank You.'
                        send_sms(newFeedback.sender, smsmessage)

                    pass
                if appId is not None:
                    return redirect(url_for('paymentMethod', username=appId))
                else:
                    return render_template('feedback.html', title="Thank You For Your Feedback ", description ="Your feedback has been recieved and is being reviewed! If need be someone ")
            
            else:
                print(form.errors)
                return "Form submitted successfully!"
        else:
            # Handle reCAPTCHA verification failure
            flash(f'reCAPTCHA verification failed. Please try again.')

            # return "reCAPTCHA verification failed. Please try again."
        
    return render_template('issue.html', form=form)
    
    
    # if downloaded.status_code == 200:
    #     print("Yes")
    # return render_template('feedback.html', title="CSV Exported" ,description="Please check your downloads for the exported csv." )
        


@app.route('/find',methods=['GET','POST'])
def index():
    suggestions = [
        {
            "name":"Pronto Hostel",
            "image":"https://www.aveliving.com/AVE/media/Property_Images/Florham%20Park/hero/flor-apt-living-(2)-hero.jpg?ext=.jpg",
            "tag":"On Campus"
         },
         {
            "name":"Boys Hostel",
            "image":"https://2.bp.blogspot.com/-9ylQ35fyyAY/TcmL8CWqGZI/AAAAAAAAAcw/v_NvZD0MRPo/s1600/BQ1.jpg",
            "tag":"On Campus"
         },
         {
            "name":"JnJ Hostel",
            "image":"https://www.kandja.tn/wp-content/uploads/2023/03/Accra-real-estate-14.jpg",
            "tag":"Off Campus"
         },
        ]
    
    newOffers = [
        {
            "name":"Pink Hostel",
            "image":"https://i.pinimg.com/originals/9e/93/54/9e935464be32e3931dea5692138a7e4d.jpg",
            "tag":"On Campus"
         },
         {
            "name":"Green Hostel",
            "image":"https://learn.g2.com/hubfs/iStock-685053710.jpg",
            "tag":"Off Campus"
         },
         {
            "name":"Blue Hostel",
            "image":"https://blog.calameo.com/wp-content/uploads/2022/01/beasty-hktkNOBN8y8-unsplash-scaled.jpg",
            "tag":"Off Campus"
         }
        ]
    
    limitedSpaces = [
        {
            "name":"Wine Hostel",
            "image":"https://i.pinimg.com/originals/9e/93/54/9e935464be32e3931dea5692138a7e4d.jpg",
            "tag":"Off Campus"
         },
         {
            "name":"Red Hostel",
            "image":"https://learn.g2.com/hubfs/iStock-685053710.jpg",
            "tag":"Off Campus"
         }
        ]
    
    if request.method=='POST':
        print("no")
        return render_template('index.html')
    
    return render_template('index.html', current_user=None, suggestions=suggestions, newOffers=newOffers, limitedSpaces=limitedSpaces)

@app.route('/')
def landingPage():
    return render_template('landingpage.html', loadingMessage = "Loading!")

@app.route('/recpayment')
def recpayment():
    return render_template('paylandingpage.html', loadingMessage = "Loading!")


@app.route('/preview', methods=['GET', 'POST'])
def preview():
    listing = {
        "name":"Pronto Hostel",
        "price":"200",
        "roomOptions":["One In A Room", "Two In A Room", "Three In A Room", "Four In A Room"],
        "description":"AVE luxury apartments are the perfect home for the discerning renter. Most of our residents are local professionals, individuals who are relocating for work or life in transition,downsizers, commuters, and newlyweds.AVE apartments feature spacious layouts, home-like fixtures and finishes, full appliance packages, abundant closet space including walk-ins, private patios or balconies, and washers and dryers.",
        "location":"50 meters from the Central University Roundabout",
        "images":["https://www.aveliving.com/AVE/media/Property_Images/Florham%20Park/hero/flor-apt-living-(2)-hero.jpg?ext=.jpg", "https://www.aveliving.com/AVE/media/Property_Images/Florham%20Park/hero/flor-apt-kitchen-(1)-hero.jpg?ext=.jpg","https://res.cloudinary.com/sagacity/image/upload/c_crop,h_3126,w_5000,x_0,y_0/c_limit,dpr_auto,f_auto,fl_lossy,q_80,w_1080/NQS_MS_LENORA_View_20_Bedroom_gbgxsr.jpg"],
        "amenities":["A/C", "24/7 Ghana Water", "Balcony"]
    }

    reviewData={
        "5":30,
        "4":90,
        "3":10,
        "2":80,
        "1":10,
    }

    # Using the keys() method to get all keys
    all_keys = reviewData.keys()

    # Converting the view object to a list (optional, but can be useful)
    reviewKeys = list(all_keys)

    print(reviewKeys)

    return render_template('preview.html', current_user=None, listing=listing, reviewKeys=reviewKeys, reviewData=reviewData)

@app.route('/enquiry', methods=['GET', 'POST'])
def enquiry():
    form = Enquiry()
    purchaseData = {
        "name":"Pronto Hostel",
        "price":"Ghc 300.00",
        "room":"One In A Room",
    }
    if form.validate_on_submit():
        message = "From: "+form.name.data + "\nContact: "+ form.contact.data + "\nMessage: "+ form.note.data
        sendTelegram(message)
        flash(f'Message delivered','success')
        return redirect(url_for('index'))
    return render_template('form.html', current_user=None, form=form, purchaseData=purchaseData)

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    cities = fetch_cities_in_accra()
    print(cities)
    return jsonify(cities)


@app.route('/newlisting', methods=['GET', 'POST'])
def newlisting():
    form = ListingForm()

    if form.validate_on_submit():
        newListing = createListing(form.data)
        pprint.pprint(newListing)
        return redirect(url_for('maps'))
    else:
        print("form.errors")
        print(form.errors)
    return render_template('newlisting.html', form=form, current_user=None)

@app.route('/newsublisting/<int:listing>', methods=['GET', 'POST'])
def newsublisting(listing):
    form = SubListingForm()
    listing = Listing.query.get_or_404(listing)
    if listing != None:
        if form.validate_on_submit():
            newListing = createSubListing(form.data, listing)
            pprint.pprint(newListing)
            return redirect(url_for('newsublisting', listing=listing.id))
        else:
            print(form.errors)
        return render_template('newsublisting.html', form=form, current_user=None, listing=listing)
    else:
        return render_template('404.html', message="There was no listing with this Id.")


@app.route('/editsublisting/<int:sublisting>', methods=['GET', 'POST'])
def editsublisting(sublisting):
    form = SubListingForm()

    sublisting = SubListing.query.get_or_404(sublisting)
    listing = Listing.query.filter_by(slug=sublisting.listingSlug).first()


    if sublisting != None:
        if request.method == 'POST':
            if form.validate_on_submit():
                try:

                    sublisting.name = form.name.data
                    sublisting.price = form.price.data
                    sublisting.quantity = form.quantity.data
                    sublisting.description = form.description.data

                    db.session.commit()
                except Exception as e:
                    print(e)
                    reportError(e)

                flash(f'' + sublisting.name +' has been updated successfully.')
                return redirect(url_for('mysublistings'))
            else:
                print(form.errors)
        else:
            form.name.data = sublisting.name
            form.price.data = sublisting.price
            form.quantity.data = sublisting.quantity
            form.description.data = sublisting.description

        return render_template('newsublisting.html', form=form, current_user=None, listing=listing)
    else:
        return render_template('404.html', message="There was no listing with this Id.")


@app.route('/allusers', methods=['GET', 'POST'])
@app.route('/allusers/<string:status>', methods=['GET', 'POST'])
@login_required
def getallusers(status="all", search=None):
    form = SearchForm()
    print(current_user)
    listing = getListing(current_user.listing)
    minimum = 700
    users = User.query.filter_by(listingSlug=listing.slug).order_by(User.username.asc()).all()

    if request.method == 'POST':
        search=form.search.data
        print("Searching: ", search)
        users = User.query.filter(User.username.ilike(f'%{search}%'), User.roomNumber.ilike(f'%{search}%')).all()


        users = User.query.filter(or_(User.username.ilike(f'%{search}%'), User.roomNumber.ilike(f'%{search}%'))).all()


        print(users)

    else:
        if status == "debt":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid <= minimum).all()
        elif status == "full":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid >= User.fullAmount).all()
        elif status == "min":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid >= minimum ).all()
        elif status == "grad":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid <= minimum).all()
    return render_template('allusers.html', users=users, form=form,listing=listing, status=status)


@app.route('/allrefunds', methods=['GET', 'POST'])
@app.route('/allrefunds/<string:status>', methods=['GET', 'POST'])
@login_required
def getallrefunds(status="all", search=None):
    form = SearchForm()
    print(current_user)
    listing = getListing(current_user.listing)
    minimum = 700
    refunds = Refund.query.filter_by(listingSlug=listing.slug).all()

    if request.method == 'POST':
        search=form.search.data
        print("Searching: ", search)
        users = User.query.filter(User.username.ilike(f'%{search}%'), User.roomNumber.ilike(f'%{search}%')).all()


        users = User.query.filter(or_(User.username.ilike(f'%{search}%'), User.roomNumber.ilike(f'%{search}%'))).all()


        print(users)

    else:
        if status == "debt":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid <= minimum).all()
        elif status == "full":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid >= User.fullAmount).all()
        elif status == "min":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid >= minimum ).all()
        elif status == "grad":
            users = User.query.filter(User.listingSlug == listing.slug, User.paid <= minimum).all()
    return render_template('allrefunds.html', refunds=refunds, form=form,listing=listing, status=status)

@app.route('/onboard', methods=(['POST','GET']))
@app.route('/onboard/<string:organisationslug>', methods=(['POST','GET']))
def onboard(organisationslug):
    form = OnboardForm()

    if organisationslug is not None:
        listing =  Listing.query.filter_by(slug=organisationslug).first()
        form.listing.choices = [(listing.slug, listing.name)]
    else:
        form.listing.choices = [(listing.slug, listing.name) for listing in Listing.query.all()]
    form.password.data = '000000'
    
    if current_user:
        logout_user()
        print ("You have been logged out")
    if form.validate_on_submit():
        print(form.data)
        if User.query.filter_by(email = form.email.data).first() != None:
            print("user")
            flash(f'There is already a user with this email address')
            return render_template('onboard.html', form=form, title="Onboard New User")
            
        elif User.query.filter_by(phone = form.phone.data).first() != None:
            flash(f'There is already a user with this phone number')
            return render_template('onboard.html', form=form, title="Onboard New User")
        
        else:
            listing = Listing.query.filter_by(slug=form.listing.data).first()
            print(listing)

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            newuser = User(username=form.username.data, email=form.email.data, phone=form.phone.data, listing=form.listing.data, listingSlug=listing.slug, password=hashed_password)
            print(newuser)
            try:
                db.session.add(newuser)
                db.session.commit()
                send_sms(newuser.phone, "You have been successfully onboarded to PrestoStay. \nhttps://stay.prestoghana.com/" + str(newuser.id) +  " \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
                sendTelegram(newuser.phone, newuser.username +" : " + newuser.phone + "has onboarded to PrestoPay. \nhttps://stay.prestoghana.com/profile/ \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
                return redirect(url_for('sublisting', userId=newuser.id))
            except Exception as e:
                print(e)
                print("User was not able to be created")
            print("Registered new user: " + newuser.username + " " + newuser.email)
            
            print(form.password.data)
            # print(form.confirm_password.data)

            user = User.query.filter_by(email=form.email.data).first()

            # return redirect(url_for('prontoform', userId=user.id))
            return redirect(url_for('sublisting', userId=user.id))

    else:
        print(form.errors)

        # errors = [value for value.messages in form.errors.values()]
        # print(errors)
        # for error in errors:
        #     flash(error)

    return render_template('onboard.html', form=form, title="Onboard New User")


# Logic to validate room against tenats data
# pick one room
# look for users in that room
# confirm occupant count == Room Count
# confirm room price == user.fullAmount
# 




@app.route('/register/<string:organisationslug>', methods=(['POST','GET']))
# @app.route('/register', methods=(['POST','GET']))
def register(organisationslug = None):
    form = RegisterForm()
    organisation = None
    welcomeMessage = "Welcome To PrestoPay"
    welcomeDescription = "Please fill in the form to create a new account."
    title = organisationslug
    form.organisation.choices = [(value.slug,value.name) for value in Listing.query.all()]

    if request.method == 'GET':
        if organisationslug != None: #Default route
            organisation = Listing.query.filter_by(slug=organisationslug).first()
            
            if organisation == None:
                flash(f'There was no organisation with this slug, please check and try again.')
            else:
                welcomeMessage = organisation.name
                welcomeDescription ="Welcome to "+organisation.name+" onboarding portal. Please enter your details to create your account and get started."
                form.organisation.data = organisation.name

        if current_user:
            logout_user()
            print ("You have been logged out")
        
    elif request.method=='POST':
        if form.validate_on_submit():
            print(form.data)
            # check email
            if User.query.filter_by(email = form.email.data).first() != None:
                print("user")
                flash(f'There is already a user with this email address')
                return render_template('register.html', form=form, title="Onboard New User")
                
            elif User.query.filter_by(phone = form.phone.data).first() != None:
                flash(f'There is already a user with this phone number')
                return render_template('register.html', form=form, title="Onboard New User")
            
            else:
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                newuser = User(username=form.username.data, email=form.email.data, phone=form.phone.data, listing=form.organisation.data, listingSlug=form.organisation.data, password=hashed_password)
                print(newuser)
                try:
                    db.session.add(newuser)
                    db.session.commit()
                    send_sms(newuser.phone, "You have been successfully onboarded to "+organisation.name+". \nhttps://stay.prestoghana.com/recpay" + str(newuser.id) +  " \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
                    sendTelegram(newuser.phone, newuser.username +" : " + newuser.phone + "has onboarded to PrestoPay. \nhttps://stay.prestoghana.com/profile/ \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
                    session['stay_user_id'] = newuser.id
                    return redirect(url_for('sublisting', userId=newuser.id))
                except Exception as e:
                    print(e)
                    print("User was not able to be created")
                print("Registered new user: " + newuser.username + " " + newuser.email)
                
                print(form.password.data)
                print(form.confirm_password.data)

                user = User.query.filter_by(email=form.email.data).first()

                # return redirect(url_for('pay', userId=user.id))
                return redirect(url_for('sublisting', userId=user.id))
        else:
            print(form.errors)
    return render_template('register.html', organisation=organisation,welcomeDescription=welcomeDescription, form=form, title=title, welcomeMessage=welcomeMessage)


@app.route('/maps', methods=['GET', 'POST'])
def maps():
    ipData = get_user_location()
    print(mapsApiKey)
    print(ipData)
    return render_template('mapsandbox.html', mapsApiKey=mapsApiKey, ipData=ipData)


def get_user_location():
    try:
        # Get the user's public IP address using a service like ipinfo.io
        ip_response = requests.get('https://ipinfo.io')
        ip_data = ip_response.json()
        user_ip = ip_data.get('ip')     

        # Use the user's IP address to fetch geolocation data
        geo = geocoder.ip(user_ip)

        print("geo")
        print(geo)
        print(type(geo))
        

        # Extract relevant location information
        user_city = geo.city
        # user_region = geo.region
        user_country = geo.country
        user_lat = geo.lat
        user_lon = geo.lng

        return {
            'city': user_city,
            'country': user_country,
            'lat': user_lat,
            'lng': user_lon
        }
    
    except Exception as e:
        # Handle any exceptions that may occur during the process
        print(f"Error: {str(e)}")
        return None


@app.route('/findme', methods=['GET', 'POST'])
def findme():
    form = FindUser()
    print(form.data)
    if form.validate_on_submit():
        phoneNumber = form.phone.data.replace(" ", "")[-9:] 

        print("phoneNumber")
        print(phoneNumber)

        user = User.query.filter(User.phone.endswith(phoneNumber)).first()
        
        print(user)
        if user is None:
            flash(f'We couldnt find anyone with this phone number.')
            return redirect(url_for('findme'))
        else:
            session['stay_user_id'] = user.id
            return redirect(url_for('pay', userId=user.id))
        # return render_template('confirmUser.html', user=user, form=form)
    return render_template('pay.html', current_user=None, form=form)



@app.route('/recpay', methods=['GET', 'POST'])
@app.route('/<string:organisationSlug>', methods=['GET', 'POST'])
def recpay(organisationSlug = None):
    form = FindRecUser()
    loadingMessage = 'Attempting to log you in.'

    print(form.data)

    form.organisation.choices = [value.name for value in Listing.query.all()]

    if organisationSlug != None:
        organisation = Listing.query.filter_by(slug=organisationSlug).first()
        
        if organisation is not None:
            form.organisation.data = organisation.name
        else:
            flash(f'No organisation with slug:'+organisationSlug+' was found. Please choose from the dropdown')
            

    tempUserBody = {
        "name":"Make A Recurring Payment",
        "logo":"https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.vecteezy.com%2Ffree-vector%2Fchurch-logo&psig=AOvVaw3QF9tq4rKcoxDOshWhwYzl&ust=1696564331488000&source=images&cd=vfe&ved=0CBEQjRxqFwoTCPix9eOA3oEDFQAAAAAdAAAAABAE"
    }
    if request.method == 'POST':
        if form.validate_on_submit():
            phoneNumber = form.phone.data.replace(" ", "")[-9:] 

            sendTelegram("Attempting to find: "+phoneNumber)

            print("phoneNumber")
            print(phoneNumber)

            listing = Listing.query.filter_by(name=form.organisation.data).first()
            user = User.query.filter(User.phone.endswith(phoneNumber), User.listingSlug==listing.slug).first()
            
            print(user)

            if user is None:
                flash(f'We couldnt find anyone with this phone number in '+listing.name+' please check and try again.')
                sendTelegram("Couldnt find: "+user.username)
                return redirect(url_for('recpay', organisationSlug=organisationSlug))
            else:
                sendTelegram("Found: "+user.username)
            return redirect(url_for('pay', userId=user.id))
    return render_template('recpay.html', current_user=None, loadingMessage=loadingMessage, form=form, user=tempUserBody)



# @app.route('/recpay/<int:userId>', methods=['GET','POST'])
# def recpayId(userId):
#     user = User.query.get_or_404(userId)
#     form = PaymentForm()
#     listing = Listing.query.filter_by(slug=user.listingSlug).first()
#     if request.method == 'POST':
#         if form.validate_on_submit():

#             body={
#                 "userId":user.id,
#                 "appId":listing.slug,
#                 "username":user.username,
#                 "roomID":user.roomNumber,
#                 "listing":user.listing,
#                 "amount":form.amount.data,
#                 "balanceBefore":user.balance,
#                 # "account":form.account.data, 
#                 # "network":form.network.data,
#                 "channel":"WEB"
#             }

#             transaction = createTransaction(body)

#             response = externalPay(transaction)

#             return redirect(response["url"])

#         else:
#             print(form.errors)
#             flash(form.errors[0])
#     return render_template('confirmUser.html', user=user, form=form)

@app.route('/pay/<int:userId>', methods=['GET','POST'])
def pay(userId):
    print("current_user")
    # print(current_user.username)
    user = User.query.get_or_404(userId)
    form = PaymentForm()
    listing = Listing.query.filter_by(slug=user.listingSlug).first()
    choices = TransactionType.query.filter_by(superListing=user.listingSlug).all()

    if len(choices) > 0:
        form.transactionType.choices = [transactionType.name for transactionType in choices]
    else:
        form.transactionType.data = 'Default'
    if request.method == 'POST':
        if form.validate_on_submit():
            body={
                "userId":user.id,
                "appId":listing.slug,
                "username":user.username,
                "roomID":user.roomNumber,
                "listing":user.listing,
                "amount":form.amount.data,
                "balanceBefore":user.balance,
                "transactionType":form.transactionType.data,
                # "account":form.account.data, 
                # "network":form.network.data,
                "channel":"WEB"
            }

            transaction = createTransaction(body)

            response = externalPay(transaction)

            return redirect(response["url"])

            # response = payWithPrestoPay(transaction)
            # print(response)

            # if body["network"] == "CARD":
            #     return render_template('paywithkorba.html', 
            #                            orderId = body["username"], amount=body["amount"], callbackUrl=response["callbackUrl"], merchantID=merchantID, description=response["description"])
            
            # else:
            #     return redirect(url_for('transaction', transactionId=transaction.id))

        else:
            print(form.errors)    
    return render_template('confirmUser.html', user=user, listing=listing, form=form)

@app.route('/actionrefund/<int:id>/<int:action>')
def actionrefund(id,action):
    print("action")
    print(action)
    refund = Refund.query.get_or_404(id)
    user = User.query.get_or_404(refund.userId)
    if current_user.role != '':
        if action == 1:
            # sendsms to user
            send_sms(user.phone,f"Congratulations, {refund.name} your refund has been approved by the administrator! We are currently pending approval by finance and then you are good to go! \n\n Powered By PrestoGhana")

            # sendtelegram to group include user who approved
            sendTelegram(f"Refund Id: {refund.id} \n{refund.name} - {refund.amount} \nApproved by the admin and forwarded to finance! ")

            sendAnEmail("PrestStay", f'ACTION REQUIRED: Approve Refund {refund.id} - {refund.name} - {refund.amount}', f'Refund Id: {refund.id} \nName:{refund.name}\nAmount:{refund.amount}\nDate Requested:{refund.date}. \n\nPlease confirm this transaction on your PrestoSolutions dashboard ',"mr.adumatta@gmail.com")

            flash(f'Refund Id: {refund.id} has been processed and forwarded to Finance.')

        else:
            flash(f'No action was taken.')
    return redirect(url_for('dashboard'))

@app.route('/allperiods', methods=['GET', 'POST'])
def getallperiods():
    form = SearchForm()
    # view all periods
    # what happens when a search is successful!
    listing = getListing(current_user)
    print(listing)
    periods = TenancyPeriod.query.filter_by(listingSlug=current_user.listingSlug).all()
    print(periods)
    return render_template('periods.html', form=form,periods=periods, listing=listing)

@app.route('/period/', methods=['GET', 'POST'])
@app.route('/period/<int:id>', methods=['GET', 'POST'])
def period(id=None):
    print(id)
    form = TenancyPeriodForm()
    rooms = SubListing.query.filter_by(listingSlug=current_user.listingSlug).all()
    listing = getListing(current_user.listingSlug)

    if id is not None:
        period = TenancyPeriod.query.get_or_404(id)
    else:
        period = None

    print(listing)

    if request.method == 'POST':
        if form.validate_on_submit():

            if period is not None:
                # update
                period.name = form.name.data
                form.name.data = period.name
                period.reservation_minimum = form.reservationMinimum.data 
                period.reservation_start_date = form.reservationStartDate.data 
                period.reservation_end_date = form.reservationEndDate.data 

                period.start_date = form.startDate.data 
                period.end_date = form.endDate.data

                try:
                    db.session.commit()
                    flash(f'Your period {period.name} was updated successfully.')
                    return redirect(url_for('getallperiods'))
                except Exception as e:
                    flash(f'There was an issue updating this records')
            else:
                try:
                    newperiod = TenancyPeriod(name=form.name.data, listingId=listing.id, listingSlug=listing.slug, start_date=form.startDate.data, end_date=form.endDate.data, reservation_start_date=form.reservationStartDate.data, reservation_end_date=form.reservationEndDate.data, reservation_minimum=form.reservationMinimum.data)
                    db.session.add(newperiod)
                    db.session.commit()
                    flash(f'Tenancy Period - {newperiod.name} has been created successfully')
                    return redirect(url_for('getallperiods'))
                except Exception as e:
                    reportError(e)
        else:
            print(form.errors)
    if request.method == 'GET':
        if id is not None:
            period = TenancyPeriod.query.get_or_404(id)
            
            form.name.data = period.name
            form.reservationMinimum.data = period.reservation_minimum
            form.reservationStartDate.data = period.reservation_start_date
            form.reservationEndDate.data = period.reservation_end_date

            form.startDate.data = period.start_date
            form.endDate.data = period.end_date
            # form.submit = 'Update!'
    return render_template('period.html', form=form, rooms=rooms, listing=listing)


@app.route('/reserved', methods=['GET', 'POST'])
@login_required
def reserved():
    form = SearchForm()
    # view all periods
    # what happens when a search is successful!
    listing = getListing(current_user)
    print(listing)
    periods = TenancyPeriod.query.filter_by(listingSlug=current_user.listingSlug).all()
    print(periods)
    return render_template('reserved.html', form=form,periods=periods, listing=listing)

@app.route('/findrefund/<int:id>', methods=['GET', 'POST'])
@login_required
def findrefund(id):
    form = RefundForm()

    refund = Refund.query.get_or_404(id)
    user = User.query.get_or_404(refund.userId)

    listing = Listing.query.filter_by(slug=user.listingSlug).first()
    choices = TransactionType.query.filter_by(superListing=user.listingSlug).all()

    # refundAmount

    form.amount.data = refund.amount
    form.reason.data = refund.reason
    # reason

    return render_template('refund.html', user=user, listing=listing, form=form, current_user=current_user, refund=refund)


@app.route('/refund/<int:userId>', methods=['GET','POST'])
def refund(userId):
    print("current_user")
    # print(current_user.username)
    user = User.query.get_or_404(userId)
    form = RefundForm()
    listing = Listing.query.filter_by(slug=user.listingSlug).first()
    choices = TransactionType.query.filter_by(superListing=user.listingSlug).all()

    if len(choices) > 0:
        form.transactionType.choices = [transactionType.name for transactionType in choices]
    else:
        form.transactionType.data = 'Refund'
    if request.method == 'POST':
        if form.validate_on_submit():

            try:
                requestedRefund = Refund(name=user.username, amount=form.amount.data, listingSlug=listing.slug, userId=user.id, reason=form.reason.data, listingId=listing.id, roomNumber=user.roomNumber)
                db.session.add(requestedRefund)
                db.session.commit()
            except Exception as e:
                reportError(e)

            smsmessage = f'Hello, {user.username} your request for a refund of GHS{requestedRefund.amount} has been recieved and is being processed. Someone from the Administration will reach out to you in due time.'
            # send an sms to the user
            # send_sms(user.phone, smsmessage)

            # update in the telegram group
            telegramMessage = f'A refund of GHS{requestedRefund.amount} has been request by {user.username}. \nReason:{requestedRefund.reason}\n Please visit your dashboard and take action. \nTicketId: {listing.slug}-{requestedRefund.id}-{form.transactionType.data}'
            sendTelegram(telegramMessage)
            
            # send an email to finance
            sendAnEmail('Presto Stay', f'Refund of GHS{requestedRefund.amount}', telegramMessage, 'mr.adumatta@gmail.com')
            # pass
            flash(f'Your request has been processed, your will recieve a confirmation message soon.')
            return redirect(url_for('pay', userId=user.id))
        else:
            print(form.errors)    
    return render_template('refund.html', user=user, listing=listing, form=form, )

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    flash("You have been successfully logged out")
    logout_user()
    return redirect(url_for('login'))

@app.route("/broadcast", methods=['GET','POST'])
@login_required
def broadcast():
    listing = Listing.query.get_or_404(1)
    form = BroadcastForm()

    contacts = User.query.filter_by(listingSlug=listing.slug).all()
    numberOfContacts = User.query.filter_by(listingSlug=listing.slug).count()

    allcontacts = [contact.phone for contact in contacts]
    print(allcontacts)
    
    app.logger.info(session)

    loadingMessage = "Broadcasting message to " + str(numberOfContacts) + " contacts, this might take a while😭"
    if request.method == 'POST':
        app.logger.info(session)
        app.logger.info("form.csrf_token.data")
        app.logger.info(form.csrf_token.data)
        message = form.message.data
        message += "\n \nPowered By PrestoStay"
        app.logger.info(message)

        smsresponse = sendMnotifySms('CUOLDGIRLS',allcontacts, message)
        sendTelegram(smsresponse)

        # app.logger.info(contacts)
        # for contact in contacts:
        #     send_sms(contact, message, "PrestoVotes")
        flash(str(numberOfContacts) + ' messages to ' + form.group.data + 'has been sent!.')
        return redirect(url_for('dashboard'))

    return render_template('broadcast.html',  contacts=contacts, numberOfContacts=numberOfContacts, form=form, loadingMessage=loadingMessage, listing=listing)


@app.route('/subSlugs/<string:listingSlug>', methods=['GET', 'POST'])
def createSubListingSlugs(listingSlug):
    sublisting = SubListing.query.filter_by(superListing=listingSlug).all()
    for s in sublisting:
        newslug = s.name.strip()+"-"+s.superListing+"-"+str(s.price)
        newslug = newslug.strip()
        print(newslug)
        s.slug = newslug
        db.session.commit()
    return "Done."

@app.route('/updateSubListing/<int:userId>/<int:subListingId>', methods=['GET', 'POST'])
def updateSubListing(userId, subListingId):

    user = User.query.get_or_404(userId)
    if user.roomNumber is not None:
        flash(f'Please unassign this user before reassigning.')
        return redirect(url_for('profile', id=user.id))
    print(user)
    sublisting = SubListing.query.get_or_404(subListingId)
    print(sublisting)
    # sublisting = SubListing.query.filter_by(slug=subListingId).first()
    
    if user == None:
        flash(f'No user was found')
        print('No user was found')
    elif sublisting == None:
        flash(f'There was no sublisting with this slug')
        print('There was no sublisting with this slug')

    try:
        user.sublisting = sublisting.id
        user.fullAmount += float(sublisting.pricePerBed)
        user.roomNumber = sublisting.name

        # Confirming it will not show here more when unvacant
        sublisting.occupants = sublisting.occupants + 1
            # find the room and set the occupancy minus one
        if sublisting.occupants == sublisting.quantity:
            sublisting.vacant = False
        else:
            sublisting.vacant = True
        db.session.commit()

        sendTelegram("Sublisting: "+ sublisting.name +" has been updated to: \nOccupants:"+ str(sublisting.occupants))

    except Exception as e:
        print(e)
        reportError(e)

    updateBalance(user.id)

    return redirect(url_for('profile',id=user.id))

def aggregateValues(value):
    distinct_values = db.session.query(SubListing.value).distinct().all()
    distinct_values = [value[0] for value in distinct_values] 
    return distinct_values


@app.route('/getroomid/<string:input_string>')
def getroomid(input_string):
    # block = ''.join(filter(str.isalpha, input_string))
    # roomId = ''.join(filter(str.isdigit, input_string))

    block = input_string[0]
    roomId = input_string.replace(block, "")

    print(block)
    print(roomId)
    return (roomId, block)

@app.route('/updateroomdata/<string:superListing>', methods=['GET', 'POST'])
def updateroomdata(superListing):
    # loop to set bedsTaken to 0:
    # allrooms = SubListing.query.filter_by(listingSlug=superListing).all()
    # for room in allrooms:
    #     room.bedsTaken = 0
    #     db.session.commit()

    print("Finding tenants in :"+superListing)
    tenants = User.query.filter_by(listingSlug=superListing).all()
    print(tenants)

    for i in tenants:
        print(i.roomNumber)
        # seperate room number into block and id
        # find sublisting
        roomDataTuple = getroomid(i.roomNumber)
        print(roomDataTuple)
        room = SubListing.query.filter_by(name=i.roomNumber, listingSlug=superListing).first()
        print("Room", room)
        if room != None:
        # reduce bedTakenCountBy1
            room.bedsTaken =+ 1
            db.session.commit()
    return "Done"
    

@app.route('/updateRoomCount/<string:superListing>')
def updateRoomCount(superListing):

    # Updates the subisting data
    sublistings = SubListing.query.filter_by(superListing=superListing).all()
    for i in sublistings:
        print(i.bedsAvailable, i.bedsTaken, i.status)
        if i.bedsAvailable != i.bedsTaken:
            i.vacant = True
        else:
            i.vacant = False
        print(i.vacant)
    db.session.commit()
    return 'Done'


@app.route('/prontoform', methods=['GET', 'POST'])
def prontoform():
    user =  stay_user()
    return render_template('prontoform/prontoform.html',user=user)

@app.route('/prontoform/personal', methods=['GET', 'POST'])
def prontoformPersonal():
    form = ProntoProfileFormPersonalInformation()
    if form.validate_on_submit():
        userId = session['stay_user_id']
        user = User.query.get_or_404(userId)
        try:
            user.firstname = form.firstname.data
            user.middlename = form.middlename.data
            user.surname = form.surname.data
            db.session.commit()
            return redirect(url_for('prontoformEduction'))
        except Exception as e:
            reportError(e)
    return render_template('prontoform/personalInformation.html', progress=30, form=form)

@app.route('/prontoform/eductionInformation', methods=['GET', 'POST'])
def prontoformEduction():
    form = ProntoProfileFormEducationInformation()
    if form.validate_on_submit():
        userId = session['stay_user_id']
        user = User.query.get_or_404(userId)
        try:
            user.level = form.level.data
            user.course = form.course.data
            user.indexNumber = form.studentId.data
            db.session.commit()
        except Exception as e:
            reportError(e)
        return redirect(url_for('prontoformEmergency'))
    return render_template('prontoform/education.html', progress=60, form=form)

@app.route('/prontoform/emergency', methods=['GET', 'POST'])
def prontoformEmergency():
    form = ProntoProfileFormEmergencyInformation()
    if form.validate_on_submit():
        userId = session['stay_user_id']
        user = User.query.get_or_404(userId)
        try:
            newEmergencyEntry = EmergencyContacts(name=form.name.data, relationship=form.relationship.data, userId=userId, username=user.username)
            db.session.add(newEmergencyEntry)
            db.session.commit()
        except Exception as e:
            reportError(e)
        return redirect(url_for('sublisting', userId=userId))
    else:
        # [flash(error) for error  in form.errors.values[]]
        print(form.errors)
    return render_template('prontoform/emergency.html', progress=90, form=form)


@app.route('/listing/<int:userId>', methods=['GET','POST'])
def sublisting(userId):
    sublistingform = SelectSubListingForm()
    message = 'You have reached the end of this list.'

    user = User.query.get_or_404(userId)
    listing = Listing.query.filter_by(slug=user.listingSlug).first()
    print(user)
    print("listing", listing)
    form = ListingForm()
    sublistings = SubListing.query.filter_by(superListing=user.listingSlug, vacant=True).order_by(SubListing.name.asc()).all()
    # print(sublistings)
    print(user.sublisting)    
    
    pprint.pprint(sublistingform.data)


    sublistingform.location.choices = [value[0] for value in db.session.query(SubListing.location).distinct().all()] 
    sublistingform.location.choices.insert(0,('All Floors'))

    sublistingform.bedsAvailable.choices = [value[0] + " in a room" for value in db.session.query(SubListing.bedsAvailable).distinct().all()] 
    sublistingform.bedsAvailable.choices.insert(0,'All Beds')
    
    sublistingform.size.choices = [value[0] for value in db.session.query(SubListing.size).distinct().all()] 
    sublistingform.size.choices.insert(0,'All Sizes')

    if request.method == 'POST':
        if sublistingform.validate_on_submit():
            try:
                print("sublistingform.location.data")
                print(sublistingform.location.data)
                # sublistingsData = SubListing.query.filter_by(location=sublistingform.location.data, bedsAvailable=sublistingform.bedsAvailable.data[0])

                if sublistingform.location.data != 'All Floors':
                    sublistings = [listing for listing in sublistings if listing.location == sublistingform.location.data]
                if sublistingform.bedsAvailable.data != 'All Beds':
                    sublistings = [listing for listing in sublistings if listing.bedsAvailable == sublistingform.bedsAvailable.data[0]]
                if sublistingform.size.data != 'All Sizes':
                    sublistings = [listing for listing in sublistings if listing.size == sublistingform.size.data]
                    # check to see if the value is not None

                print(sublistings)

                if len(sublistings) == 0:
                    message = 'Unfortunately, there were no listings found. Please try to search again.'
            except Exception as e:
                print(e)
        else:
            print("Errors:",sublistingform.errors)

        # if form.validate_on_submit():
        #     try:   
        #         user.sublisting = form.sublisting.data
        #         user.roomId = form.roomId.data
        #         user.fullAmount = user.fullAmount + sublisting.price
        #         user.roomNumber = sublisting.name
        #         db.session.commit()

        #     except Exception as e:
        #         reportError(e)
        #         flash(f'We couldnt update your listing, please try again later.')

        #     return redirect(url_for('transaction', transactionId=transaction.id))
        # else:
        #     print("Errors:",form.errors)

        # updateSubListing(user.id)
            # flash(form.errors[0])

    print("Passing This listing")
    print(listing)
    return render_template('sublisting.html', user=user, message=message,sublistingform=sublistingform,listing=listing, sublistings=sublistings, form=form)

@app.route('/mysublistings', methods=['GET', 'POST'])
def mysublistings():
    listing = getListing(1)
    sublistings = SubListing.query.filter_by(superListing=listing.slug).order_by(SubListing.name.asc()).all()
    return render_template('mysublistings.html',sublistings=sublistings, listing=listing,user=None)

@app.route('/unassign/<int:userId>', methods=['GET', 'POST'])
@login_required
def unassign(userId):
    print(userId)
    user = User.query.get_or_404(userId)
    room = SubListing.query.filter_by(name=user.roomNumber).first()
    logger("Attempting to unassign "+user.username+" from "+room.name)

    try:
        # remove one occupant from room
        room.occupants -= 1
        # remove room number from occupant
        user.roomNumber = None
        user.fullAmount = 0
        # Set status to unassigned.
        user.status = "Unassigned"
        db.session.commit()
        logger("SUCCESSFUL: \nUnassigning "+user.username+" from "+room.name)

    except Exception as e:
        reportError(e)
    return redirect(url_for('profile', id=user.id))
    

@app.route('/transaction/<int:transactionId>', methods=['GET', 'POST'])
def transaction(transactionId): 
    transaction = Transactions.query.get_or_404(transactionId)
    user = User.query.get_or_404(transaction.userId)
    return render_template('transaction.html', transaction=transaction, user=user)

@app.route('/verifyTransaction/<int:transactionid>', methods=['GET', 'POST'])
def verifyTransaction(transactionid):
    transaction = Transactions.query.get_or_404(transactionid)
    # user = User.query.get_or_404(transaction.userId)
    confirm(transaction.id)
    return redirect(url_for('transaction', transactionId=transaction.id))

@app.route('/confirm/<string:transactionId>', methods=['GET', 'POST'])
def confirm(transactionId):
    print("-------------- CALLBACK RECIEVED --------------- ")
    print(request.url)
    print("-------------- CALLBACK DATA --------------- ")
    print(request.json)

    message = "In Progress"
    transaction = Transactions.query.get_or_404(transactionId)
    print(transaction)
    listing = Listing.query.filter_by(slug=transaction.listing).first()
    # SECURE THIS ROUTE

    if transaction.paid == False:
        body = request.json
        try:
            print("Attempting to update transaction id: " + str(transaction.id) + " with prestoRef ")
            transactionRef = body["transactionId"]
            print(transactionRef)

            transaction.ref = transactionRef
            transaction.account = body.get("account")
            transaction.channel = body.get("channel")

            db.session.commit()
        except Exception as e:
            print(e)

        message = "Failed Transaction"

        if confirmPrestoPayment(transaction) == True:

            message = "Duplicate"
            entry = updateUserBalance(transaction)
            if entry != None: #If a vote was created
                # message = "You have successfully bought " + str(entry.amount) + " vote(s) for " + transaction.username + "\n TransactionID: " + str(transaction.id)+"PRS"+str(transaction.ref) + "\n \n Powered By PrestoStay"
                
                # if listing.slug == 'prontohostel':
                responseMessage = transaction.listing + "\nSuccessfully bought " +str(transaction.amount) + " for " + str(transaction.username) + "." + "\nBefore: " + str(transaction.balanceBefore) + "\nAfter: "+ str(transaction.balanceAfter) + "\nTransactionId:" + str(transaction.id) + "\nAccount:" + str(transaction.network) + " : "+ str(transaction.account) + "\nLedgerId: " + str(entry.id)
                message = "Student Name:"+ str(transaction.username) + "\nHostel Name: "+transaction.listing + "\nAmount:" + str(transaction.amount) + "\nPayment Method:"+transaction.channel + "\nPayment  Date" + transaction.date_created.strftime("%Y-%m-%d %H:%M:%S") + "\nReceipt Number: PRS" + str(transaction.id) + "REF" + str(transaction.ref) +"\nYour payment has been received successfully!."
                # else:
                    # message = f'Hello '+  str(transaction.username) +' your '+ str(transaction.transactionType) +' payment of GHS' + str(transaction.amount) +' has been recieved successfully.\n\nPowered By PrestoGhana'
                    # responseMessage = message
                print("send_sms || PrestoStay)")
                send_sms(transaction.account, message)

                print(responseMessage)
                sendTelegram(responseMessage)
                sendVendorTelegram(responseMessage, listing.chatId)
                flash(f'This transaction was successful! You should recieve and sms.')
            else:
                app.logger.error("Transaction: " + str(transaction.id) + " was attempting to be recreated.")
            
        else:
            message = "This transaction has either failed or is being processed. Please check or try again."

    responseBody = {
        "message":message,
        "transactionId":transaction.id,
        "prestoTransactionId":transaction.ref,
        "paid":transaction.paid
    }
    print(responseBody)
    return responseBody


@app.route('/login', methods=['GET', 'POST'])
def login():
    logout_user()
    form = LoginForm()
    if request.method == 'POST':
        print(form.email.data)
        print(form.password.data)
        user = User.query.filter_by(email = form.email.data).first()
        print(user)
        if user and bcrypt.check_password_hash(user.password, form.password.data) and user.role == 'admin':
            print("Logged in successful. \n " + user.username)
            sendTelegram("Logged in successful. \n " + user.username)
            login_user(user)
            next = request.args.get('next')
            # if not is_safe_url(next):
            return redirect(next or url_for('dashboard')) 
            # return redirect(url_f or(dashboard))
        else:
            print(form.password.data)
            print("The password is not correct")
            flash(f'There was a problem with your login credentials. Please check try again')
    else:
        print("This is a get request")
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # listing = getListing(current_user.listing)
    listing = Listing.query.get_or_404(1)
    activeUsers = User.query.filter_by(listingSlug = listing.slug).count()
    amountRecieved = listing.amountRecieved
    expected_revenue = listing.expectedRevenue
    due = expected_revenue - amountRecieved
    totalTransasactions = 20
    bankTransactions = Transactions.query.filter_by(channel="BANK", paid=True).all()
    
    cashTransactions = 0
    for c in bankTransactions:
        cashTransactions += c.amount

    sublistings = SubListing.query.filter_by(superListing=listing.slug).count()

    todaysTransactions = Transactions.query.filter(
    func.date(Transactions.date_created) == func.date(datetime.datetime.utcnow()),
    Transactions.paid == True,
    Transactions.appId == "pronto"
    ).all()

    transactions = Transactions.query.filter_by(appId =listing.slug).count()
    successfulTransactions = Transactions.query.filter_by(appId =listing.slug, paid=True).count()
    
    todaysBalance = sum(transaction.amount for transaction in todaysTransactions)
    totalTodayTransactions = len(todaysTransactions)

    occupied = 0

    contacts = User.query.filter_by(listingSlug=listing.slug).count()   

    transactionTypes = TransactionType.query.filter_by(superListing='mmogcc').count() 
    print(activeUsers)

    weekTransactions = db.session.query(func.date(Transactions.date_created), func.sum(Transactions.amount)).filter(Transactions.paid == True, Transactions.appId == listing.slug, func.date(Transactions.date_created) > datetime.datetime.today() - datetime.timedelta(weeks=1) ).group_by(func.date(Transactions.date_created)).all()

    approvedrefund = Refund.query.filter_by(listingSlug=current_user.listingSlug,financeApprove=True, adminApprove=True).count()
    pendingrefund = Refund.query.filter_by(listingSlug=current_user.listingSlug).count()

    tenancyperiods = TenancyPeriod.query.filter_by(listingSlug=current_user.listingSlug, active=True).count()
    past_due_tenancy_periods = 0
    
    dates = []
    amount = []

    for index, w in enumerate(weekTransactions):
        print(w)
        print(w[0])
        dates.append(str(w[0]))
        amount.append(w[1])
        if index == 7:
            break

    try:
        minAmount = min(amount)
    except Exception as e:
        print(e)
        minAmount = 0

    try:
        maxAmount = max(amount)
    except Exception as e:
        print(e)
        maxAmount = 0

    print(str(maxAmount) + " - " + str(minAmount))

    data = {
        "tenants":contacts,
        "rooms":sublistings,
        "dates":dates,
        "amount":amount,
        "maxAmount":maxAmount,
        "minAmount":minAmount,
        "debtors":7,
        "roomsOccupied":7,
        "pending_refunds":pendingrefund,
        "approved_refunds":approvedrefund,
        "tenancy_periods":tenancyperiods,
        "past_due_tenancy_periods":past_due_tenancy_periods
    }

    pprint.pprint(data)
    return render_template('dashboard.html', data=data,successfulTransactions=successfulTransactions,transactions=transactions, transactionTypes=transactionTypes,cashTransactions=cashTransactions, contacts=contacts ,user=current_user, occupied=occupied,sublistings=sublistings, totalTodayTransactions=totalTodayTransactions,listing=listing, activeUsers=activeUsers, totalTransasactions=totalTransasactions,todaysBalance=todaysBalance,amountRecieved=amountRecieved, due=due,expected_revenue=expected_revenue)


def getUserByMsisdn(msisdn):
    phone = "0"+msisdn[-9:]
    user = User.query.filter_by(phone = phone).first()
    return user if user is not None else None

def findByIndexNumber(index):
    user = User.query.filter_by(indexNumber = index).first()
    return user if user is not None else None

@app.route('/ussd', methods=['GET', 'POST'])
def rancardussd():
    sessionRequest = request.json
    sessionBody = {
    "MSISDN": sessionRequest["msisdn"],
    "USERDATA": sessionRequest["data"],
    "NETWORK": sessionRequest["mobileNetwork"],
    "SESSIONID": sessionRequest["sessionId"]
}
    print("---------REQUEST-----------")
    print(sessionRequest)
    print(sessionBody)
    print("--------------------")

    msisdn = sessionBody['MSISDN']
    userdata = sessionBody['USERDATA']

    # message="Hello, Please Enter Your Index Number.\n eg.int/20/01/3356."
    if sessionRequest['menu'] == 0:
        session.clear()
        message = "Welcome to PrestoStay; \nPlease enter your index number to proceed into your account. eg.int/20/01/3356"
    else:
        # declare the user
        user = session.get('userId', None)
        amount = session.get('amount',None)
        confirm = session.get('confirm',None)


        if userdata is not None:

            print(userdata)
            
            if user is None:
                user = findByIndexNumber(userdata)
                if user is None:
                    message = f"Sorry, no user with index number {userdata} was found. Please check and try again."
                else:
                    print("Found:", user)
                    message = f"Hello {user.username} Room: {user.roomNumber}. You have an outstanding balance of GHS {user.balance}. Please enter your amount due"
                    session['userId'] = user.id
                    session['username'] = user.username
                    session['userbalance'] = user.balance
                    session['userlisting'] = user.listing
                    session['userlistingslug'] = user.listingSlug
                    session['userroomnumber'] = user.roomNumber

            elif amount is None:
                session['amount'] = userdata
                message = f"Please confirm transaction of GHS {userdata} to {session['userlisting']} Room: {session['userroomnumber']} \n1. Confirm \n2.Cancel"

            elif confirm is None:
                session['confirm'] = userdata
                if userdata == '1':
                    # make api call!
                    body={
                        "userId":user,
                        "appId":session.get('userlistingslug','cuoldgirls'),
                        "username":session.get('username', None),
                        "roomID":session.get('userroomnumber', None),
                        "listing":session.get('userlisting', 'CU Old Girls'),
                        "amount":amount,
                        "balanceBefore":session.get('userbalance', None),
                        "transactionType":"form.transactionType.data",
                        "account":msisdn, 
                        "network":sessionRequest['mobileNetwork'],
                        "channel":"USSD"
                    }

                    transaction = createTransaction(body)
                    payWithPrestoPay(transaction)
                    # if api call is successful.
                    # if sessionRequest['mobileNetwork'] == 'MTN':
                    message = "Please check your approvals to confirm this transaction."
                    # else:
                    #     message = "Please check your approvals to confirm this transaction."

                else:
                    session.clear()
                    message = "Welcome to PrestoStay; \nPlease enter your index number to proceed into your account. eg.int/20/01/3356"

        else:
            message = "Please check your entry and try again!"



        

    # if user there is user proceed, else, fraud
    # if user is not None: #If an account is found
    #     if session['amount'] is not None:
    #         message = "Please confirm transaction of GHS {amount} to {user.listing} Room: {user.roomNumber} "
    # else: 
    #     message = "Unfortunately we didnt find index number: {userdata} \nPlease enter your index number to proceed into your account."

    # else:
    #     # FIRST REQUEST GOES HERE!
    #     user = getUserByMsisdn(msisdn)
    #     if user:
    #         session['userId'] = user.id
    #         session['username'] = user.username
    #         session['userbalance'] = user.balance
    #         message = f"Hello {user.username} Room: {user.roomNumber}. You have an outstanding balance of GHS {user.balance}. Please enter your amount due"
    #     else:
    #         message = f"Welcome to PrestoStay; Please enter your index number to proceed into your account."

    response = {
            "continueSession": True,
            "message": message
        }

    return response




@app.route('/upload/<string:dataType>', methods=['GET', 'POST'])
@app.route('/upload/<string:listingSlug>/<string:dataType>', methods=['GET', 'POST'])
def upload(listingSlug, dataType = None):
    listing = Listing.query.filter_by(slug=listingSlug).first()
    users = User.query.filter_by(listingSlug=listing.slug).all()
    if request.method == 'POST':

        if 'csv_file' not in request.files:
            print("No CSV File!")
            return "No CSV file provided"

        csv_file = request.files['csv_file']

        if csv_file.filename == '':
            return "No selected file"

        # Process the uploaded CSV file
        csv_content = csv_file.read().decode('utf-8')

        # Generate a unique file name with date-time stamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # filename = f"uploaded_csv_{timestamp}.csv"
        filename = f"{listing.slug}-rawdata.csv"

        # Save the processed CSV with the generated filename
        save_path = os.path.join(app.root_path,"Uploads", filename)  # Replace "path_to_save" with your desired path
        
        with open(save_path, "w") as f:
            f.write(csv_content)

        flash(f"CSV file uploaded and saved as {filename}")

        if dataType == "transactions":
            message = uploadTransactions(save_path)

        elif dataType == "users":
            # newdatapath = getOccupants(save_path, listing)
            message = uploadData(save_path, True)

        elif dataType == "rooms":
            # folder = create_folder(os.path.join(app.root_path,listing.slug))    
            # writepath = os.path.join(app.root_path,folder, f'rooms-{timestamp}.csv')  # Replace "path_to_save" with your desired path
            # newdatapath = createRooms(save_path, writepath, listing)
            message = uploadRoomData(save_path, listing, True)

            return message
        
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html', users=users)

@app.route('/alltransactions', methods=['GET', 'POST'])
def alltransactions():
    user = current_user
    transactions = Transactions.query.filter_by(appId=user.listingSlug).order_by(Transactions.id.desc()).all()
    print(transactions)
    return render_template('alltransactions.html', transactions=transactions,user=None)


@app.route('/transactions/<int:userId>', methods=['GET', 'POST'])
def usertransactions(userId):
    user = User.query.get_or_404(userId)
    transactions = Transactions.query.filter_by(userId = str(user.id), paid=True).order_by(Transactions.id.desc()).all()
    print(transactions)
    return render_template('alltransactions.html', user=user,transactions=transactions)

@app.route('/deleteuser/<int:id>', methods=['GET', 'POST'])
def deleteuser(id):
    user = User.query.get_or_404(id)
    if user == None:
        flash(f'There was no user with that id.')
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'has been delete successfully!')
    except Exception as e:
        flash(f'This action failed.')

    return redirect(url_for('upload'))


@app.route('/resendsms/<int:id>', methods=['GET', 'POST'])
def resendsms(id):
    user = User.query.get_or_404(id)
    if user == None:
        flash(f'There was no user with that id.')
    try:
        print("Retrying sms to " + user.phone)
        retrymessage = "You have been successfully onboarded to PrestoStay. \nhttps://stay.prestoghana.com/" + str(user.id) +  " \nYour username is "+ user.username+ "\nIf you need any form of support you can call +233545977791 "
        
        smsresponse = send_sms(user.phone, retrymessage)
        print(smsresponse["status"])

        flash(f'has been delete successfully!')
    except Exception as e:
        print(e)
        flash(f'This action failed.')

    return redirect(url_for('upload'))


@app.route('/updateAllRooms/<string:listingSlug>', methods=['GET', 'POST'])
def updateAllUsersInSubListing(listingSlug):
    for i in User.query.filter_by(listingSlug=listingSlug, role="user").all():
        print(i)
        updateBalance(i.id)
    return "Done"


# @app.route('/updateBalance/<int:userId>', methods=['GET', 'POST'])
def updateBalance(userId):
    listing = Listing.query.get_or_404(1)
    print(listing)

    expectedRevenue = 0
    amountRecieved = 0

    user = User.query.get_or_404(userId)
    room = SubListing.query.filter_by(name = user.roomNumber).first()

    if room is not None:
        user.fullAmount = room.price
        user.balance = user.fullAmount - user.paid
        print(user)
        print("Room Name:",room.name, "Price:",room.price)
        print("FullAmount:",user.fullAmount)
        print("PaidAmount:",user.paid)
        db.session.commit()   
    else:
        print("_________________")
        print("USER:",user.username,"ISNT ASSIGNED A ROOM!")
        print("_________________")
        

    # listing.amountRecieved = amountRecieved
    # listing.expectedRevenue = expectedRevenue

    # db.session.commit()

    flash(f'Data has been updated!')
    return redirect(url_for('dashboard'))

def updateUserProfileBalance(id):
    user = User.query.get_or_404(id)
    try:
        user.balance = user.fullAmount - user.paid
        db.session.commit()
    except Exception as e:
        reportError(e)
    return "Done!"

@app.route('/profile', methods=['GET', 'POST'])
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
@login_required
def profile(id=None):
    form = ProfileForm()
    listing = current_user.listing
    print(listing)
    # getAllListings()
    if id is not None:
        user = User.query.get_or_404(id)
        if user != None:
            print(user)
            if request.method == 'POST':
                if form.validate_on_submit():
                    print(form.data)
                    try:
                        user.username = form.username.data
                        # user.listing = form.listing.data
                        user.balance = form.balance.data
                        # user.paid = form.paid.data
                        # user.roomNumber = form.roomNumber.data
                        user.phone = form.phone.data
                        user.indexNumber = form.indexNumber.data
                        # user.fullAmount = form.fullAmount.data
                        user.email = form.email.data
                        db.session.commit()

                        # updateUserProfileBalance(id)
                        updateBalance(id)

                        flash(f'' + user.username+' has been updated successfully')
                        return redirect(url_for('getallusers'))
                    
                    except Exception as e:
                        reportError(e)
                        flash(f'Updating of your profile failed, please check and try again')
            
                else:
                    print(form.errors)

            elif request.method == 'GET':
                form.username.data = user.username
                form.listing.data = user.listing
                form.balance.data = user.balance
                form.phone.data = user.phone
                form.indexNumber.data = user.indexNumber
                form.fullAmount.data = user.fullAmount
                form.roomNumber.data = user.roomNumber
                form.email.data = user.email
                form.paid.data = user.paid
    else:
        user = None
        # listing = current_user
        form.listing.data = listing
        if request.method == 'POST':
            try:
                newuser = User(username=form.username.data, email=form.email.data, phone=form.phone.data, listing=listing)
                db.session.add(newuser)
                db.session.commit()

                updateUserBalance(newuser)
            except Exception as e:
                reportError(e)
    return render_template('profile.html', user=user, form=form, listing=getListing(1))
    # else:
    #     return render_template('404.html', message = "The user you chose cant be found")





if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)