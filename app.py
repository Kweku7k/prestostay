import csv
import datetime
import json
import os
from flask import Flask, flash, jsonify,redirect,url_for,render_template, request
from flask_login import login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, func
from itsdangerous import Serializer
from flask_bcrypt import Bcrypt
from utils import apiResponse, send_sms, sendTelegram
from flask_login import  LoginManager
from forms import *
import pprint
import time
import requests
import geocoder
from urllib.parse import quote as url_quote



app=Flask(__name__)
bcrypt = Bcrypt(app)
sandboxDb = "postgresql://postgres:adumatta@database-1.crebgu8kjb7o.eu-north-1.rds.amazonaws.com:5432/stay"
app.config['SECRET_KEY'] = 'c280ba2428b2157916b13s5e0c676dfde'
app.config['SQLALCHEMY_DATABASE_URI']= sandboxDb


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mapsApiKey = os.environ.get('GOOGLEMAPSAPIKEY')


prestoUrl = "https://prestoghana.com"
baseUrl = "https://stay.prestoghana.com"

merchantID = "ec5fb5b5-2b80-4a9a-b522-24c90912f106"

environment = os.environ["ENVIRONMENT"]
# This value confirms the server is not null
# server = os.environ["SERVER"]
server = "SERVER"


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
    
class Listing(db.Model):
    tablename = ['Listing']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    phone = db.Column(db.String)
    logo = db.Column(db.String)
    description = db.Column(db.String)
    expectedRevenue = db.Column(db.Float)
    amountRecieved = db.Column(db.Float)
    amountDue = db.Column(db.Float)
    description = db.Column(db.String)
    location = db.Column(db.String)
    locationTag = db.Column(db.String)
    images = db.Column(db.String)
    slug = db.Column(db.String)
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
    divideCost = db.Column(db.Boolean, default=True)
    superListing = db.Column(db.String)
    listingSlug = db.Column(db.String)
    # dismissable fields
    block = db.Column(db.String)
    roomId = db.Column(db.String)
    bedsAvailable = db.Column(db.String)
    bedsTaken = db.Column(db.String)
    location = db.Column(db.String)
    size = db.Column(db.String)
    status = db.Column(db.String)
    pricePerBed = db.Column(db.String)

    slug = db.Column(db.String)
    
    def __repr__(self):
        return f"SubListing('id: {self.id}', 'name:{self.name}', 'superlisting:{self.listingId}'. '{self.superListing}')"

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    listingId = db.Column(db.String)

    def __repr__(self):
        return f"Listing('id: {self.id}', 'name:{self.suggestion}', 'location:{self.location}')" 

class LocationTagEnum(Enum):
    on_campus = 'on_campus'
    off_campus = 'off_campus'

class User(db.Model):
    """Model for user accounts."""
    __tablename__ = 'users'

    name = db.Column(db.String)
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
    id = db.Column(db.Integer,primary_key=True)
    dailyDisbursal = db.Column(db.Boolean, default=False)
    username = db.Column(db.String,nullable=False,unique=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), primary_key=False, unique=False, nullable=False)

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
    ledgerEntryId = db.Column(db.Integer)
    ref = db.Column(db.String) #notsupersure?
    prestoTransactionId = db.Column(db.Integer)
    channel = db.Column(db.String)
    
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
    pass

def getListing(id):
    try:
        listing = Listing.query.get_or_404(id)
    except Exception as e:
        print(e)
        print("Couldnt find a listing with this id.")
        listing = None
    return listing

def getAllListings(suggestion=None):
    if suggestion == None:
        listings = Listing.query.all()
    else:
        listings = Listing.query.filter_by(suggestion=suggestion).all()
    return listings

def createListing(body):
    print(body)
    # pprint.pprint(body.json())
    # body = jsonify(body.data)
    new_listing = Listing(
        name=body.get("name"),
        description=body.get("description"),
        location=body.get("location", "Greater Accra"),
        locationTag=body.get("locationTag", "Accra")
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

def uploadData(filename):
    csv_file_path = filename  # Replace with the path to your CSV file
    message = "New Users updated successfully!"

    for u in User.query.all():
        db.session.delete(u)

    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            print(row)

            try:
                user = User(username = row["Name"], password = "0000",email = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+row["Number"]+"@prestoghana.com", phone = row["Number"], indexNumber=row["Index Number"], listing=row["Listing"], paid=row["Paid"], roomNumber=row["Room Number"], fullAmount=row["Full Amount"], balance=row["Balance"], listingSlug=row["listingSlug"] )
                db.session.add(user)
            except Exception as e:
                message = "There seems to have been an issue with the upload"
                print(e)

            db.session.commit()
            
    return message

def uploadRoomData(filename, listing):
    csv_file_path = filename  # Replace with the path to your CSV file
    message = "New Rooms updated successfully!"

    print("Attempting Create New Sublistings for " + listing.name)

    # for u in SubListing.query.filter_by(listingS):
    #     db.session.delete(u)

    # create a new sublisting

    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        
        for row in csv_reader:
            print(row)

            try:
                # user = User(username = row["Name"], password = "0000",email = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+row["Number"]+"@prestoghana.com", phone = row["Number"], indexNumber=row["Index Number"], listing=row["Listing"], paid=row["Paid"], roomNumber=row["Room Number"], fullAmount=row["Full Amount"], balance=row["Balance"], listingSlug=row["listingSlug"] )
                sublisting = SubListing(name = row["Name"], block=row["Block"], roomId=row["RoomId"], bedsAvailable=row["Beds Available"], bedsTaken = row["Beds Taken"], location = row["Location"], size=row["Size"], status = row["Vacancy Status"], pricePerBed=row["Price per bed"], price=row["Price"], listingId=row["Listing Id"], superListing=row["Super Lisiting"] )
                db.session.add(sublisting)

            except Exception as e:
                message = "There seems to have been an issue with the upload"
                print(e)

            db.session.commit()
            
    return message



        


# ----- ROUTES


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


    # form.location.choices = cities

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
def getallusers():
    users = User.query.all()
    return render_template('allusers.html', users=users)

@app.route('/onboard', methods=(['POST','GET']))
def onboard():
    form = OnboardForm()

    form.listing.choices = [(listing.slug, listing.name) for listing in Listing.query.all()]
    if current_user:
        logout_user()
        print ("You have been logged out")
    if form.validate_on_submit():
        print(form.data)
        # check email
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
            print(form.confirm_password.data)

            user = User.query.filter_by(email=form.email.data).first()

            return redirect(url_for('sublisting', userId=user.id))
    else:
        print(form.errors)
    return render_template('onboard.html', form=form, title="Onboard New User")

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
        listing = Listing.query.filter_by(slug="")
        
        print(user)
        if user is None:
            flash(f'We couldnt find anyone with this phone number.')
            return redirect(url_for('findme'))
        
        return redirect(url_for('pay', userId=user.id))
        # return render_template('confirmUser.html', user=user, form=form)
    return render_template('pay.html', current_user=None, form=form)



@app.route('/recpay', methods=['GET', 'POST'])
def recpay():
    form = FindUser()
    print(form.data)

    tempUserBody = {
        "name":"A Church",
        "logo":"https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.vecteezy.com%2Ffree-vector%2Fchurch-logo&psig=AOvVaw3QF9tq4rKcoxDOshWhwYzl&ust=1696564331488000&source=images&cd=vfe&ved=0CBEQjRxqFwoTCPix9eOA3oEDFQAAAAAdAAAAABAE"
    }
    if form.validate_on_submit():
        phoneNumber = form.phone.data.replace(" ", "")[-9:] 

        print("phoneNumber")
        print(phoneNumber)

        user = User.query.filter(User.phone.endswith(phoneNumber)).first()
        listing = Listing.query.filter_by(slug="")
        
        print(user)
        if user is None:
            flash(f'We couldnt find anyone with this phone number.')
            return redirect(url_for('findme'))
        
        return redirect(url_for('pay', userId=user.id))
    return render_template('recpay.html', current_user=None, form=form, user=tempUserBody)


@app.route('/pay/<int:userId>', methods=['GET','POST'])
def pay(userId):
    user = User.query.get_or_404(userId)
    form = PaymentForm()
    listing = Listing.query.filter_by(slug=user.listingSlug).first()
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
            flash(form.errors[0])
    return render_template('confirmUser.html', user=user, form=form)

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

@app.route('/updateSubListing/<int:userId>/<string:subListingSlug>', methods=['GET', 'POST'])
def updateSubListing(userId, subListingSlug):

    user = User.query.get_or_404(userId)
    sublisting = SubListing.query.filter_by(slug=subListingSlug).first()
    
    if user == None:
        flash(f'No user was found')
        print('No user was found')
    elif sublisting == None:
        flash(f'There was no sublisting with this slug')
        print('There was no sublisting with this slug')

    try:
        user.sublistingSlug = subListingSlug
        user.fullAmount += sublisting.pricePerBed
        user.roomNumber = sublisting.name
        db.session.commit()
    except Exception as e:
        print(e)
        reportError(e)

    updateBalance()

    return redirect(url_for('pay',userId=user.id))

def aggregateValues(value):
    distinct_values = db.session.query(SubListing.value).distinct().all()
    distinct_values = [value[0] for value in distinct_values] 
    return distinct_values

@app.route('/listing/<int:userId>', methods=['GET','POST'])
def sublisting(userId):
    sublistingform = SelectSubListingForm()
    user = User.query.get_or_404(userId)
    listing = Listing.query.filter_by(slug=user.listing).first()
    print(user)
    print("listing", listing)
    form = ListingForm()
    sublistings = SubListing.query.filter_by(superListing=user.listing).all()
    # print(sublistings)
    print(user.sublisting)

    sublistingform.location.choices = [value[0] for value in db.session.query(SubListing.location).distinct().all()] 
    sublistingform.bedsAvailable.choices = [value[0] + " in a room" for value in db.session.query(SubListing.bedsAvailable).distinct().all()] 
    sublistingform.size.choices = [value[0] for value in db.session.query(SubListing.size).distinct().all()] 
    sublistingform.block.choices = ["Block " + value[0] for value in db.session.query(SubListing.block).distinct().all()] 
    # sublistingform.size.choices = [value[0] for value in db.session.query(SubListing.size).distinct().all()] 

    # append "--" at the starting of the drop down
    if user.sublisting != None:
        if request.method == 'POST':
            if sublistingform.validate_on_submit():
                try:
                    print("form.location.data")
                    print(form.location.data)
                    sublistings = SubListing.query.filter_by(location=form.location.data).all()
                except Exception as e:
                    print(e)

            if form.validate_on_submit():
                try:   
                    user.sublisting = form.sublisting.data
                    user.roomId = form.roomId.data
                    user.fullAmount = user.fullAmount + sublisting.price
                    db.session.commit()

                except Exception as e:
                    reportError(e)
                    flash(f'We couldnt update your listing, please try again later.')

                return redirect(url_for('transaction', transactionId=transaction.id))
            else:
                print("Errors:",form.errors)
                # flash(form.errors[0])
    return render_template('sublisting.html', user=user, sublistingform=sublistingform,listing=listing, sublistings=sublistings, form=form)

@app.route('/mysublistings', methods=['GET', 'POST'])
def mysublistings():
    listing = Listing.query.get_or_404(1)
    sublistings = SubListing.query.filter_by(listingSlug=listing.slug).all()
    return render_template('mysublistings.html',sublistings=sublistings, listing=listing,user=None)


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
                
                message = "Student Name:"+ str(transaction.username) + "\nHostel Name: "+transaction.listing + "\nAmount:" + str(transaction.amount) + "\nPayment Method:"+transaction.channel + "\nPayment  Date" + transaction.date_created.strftime("%Y-%m-%d %H:%M:%S") + "\nReceipt Number: PRS" + str(transaction.id) + "REF" + str(transaction.ref) +"\nYour payment has been received successfully!."

                print("send_sms || PrestoStay)")
                send_sms(transaction.account, message)

                responseMessage = transaction.listing + "\nSuccessfully bought " +str(transaction.amount) + " for " + str(transaction.username) + "." + "\nBefore: " + str(transaction.balanceBefore) + "\nAfter: "+ str(transaction.balanceAfter) + "\nTransactionId:" + str(transaction.id) + "\nAccount:" + str(transaction.network) + " : "+ str(transaction.account) + "\LedgerId: " + str(entry.id)
                print(responseMessage)
                print(responseMessage)
                sendTelegram(responseMessage)
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
    # if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        print(user)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("Logged in successful. \n " + user.username)
            sendTelegram("Logged in successful. \n " + user.username)
            login_user(user)
                # login_user(user)
            next = request.args.get('next')
            # if not is_safe_url(next):
            return redirect(next or url_for('users.dashboard')) 
            # return redirect(url_f or(dashboard))
        else:
            print(form.password.data)
            # print("The password is not correct")
            flash(f'There was a problem with your login credentials. Please check try again')
    else:
        print("This is a get request")
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
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

    sublistings = SubListing.query.filter_by(listingSlug=listing.slug).count()

    # todaysTransactions = Transactions.query.filter(func.date(Transactions.date_created) == func.date(datetime.datetime.utcnow()), Transactions.paid == True, Transactions.appId == "pronto").all()
    todaysTransactions = Transactions.query.filter(
    func.date(Transactions.date_created) == func.date(datetime.datetime.utcnow()),
    Transactions.paid == True,
    Transactions.appId == "pronto"
    ).all()
    
    todaysBalance = sum(transaction.amount for transaction in todaysTransactions)
    totalTodayTransactions = len(todaysTransactions)

    occupied = 0
    
    print(activeUsers)
    return render_template('dashboard.html', cashTransactions=cashTransactions ,user=current_user, occupied=occupied,sublistings=sublistings, totalTodayTransactions=totalTodayTransactions,listing=listing, activeUsers=activeUsers, totalTransasactions=totalTransasactions,todaysBalance=todaysBalance,amountRecieved=amountRecieved, due=due,expected_revenue=expected_revenue)



@app.route('/upload/<string:dataType>', methods=['GET', 'POST'])
@app.route('/upload/<string:listingSlug>/<string:dataType>', methods=['GET', 'POST'])
def upload(listingSlug, dataType = None):
    listing = Listing.query.filter_by(slug=listingSlug).first()
    users = User.query.filter_by(listingSlug=listing.slug).all()
    if request.method == 'POST':

        if 'csv_file' not in request.files:
            return "No CSV file provided"

        csv_file = request.files['csv_file']

        if csv_file.filename == '':
            return "No selected file"

        # Process the uploaded CSV file
        csv_content = csv_file.read().decode('utf-8')

        # Generate a unique file name with date-time stamp
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"uploaded_csv_{timestamp}.csv"

        # Save the processed CSV with the generated filename
        
        save_path = os.path.join(app.root_path,"Uploads", filename)  # Replace "path_to_save" with your desired path
        
        with open(save_path, "w") as f:
            f.write(csv_content)

        flash(f"CSV file uploaded and saved as {filename}")

        if dataType == "transactions":
            message = uploadTransactions(save_path)
        elif dataType == "users":
            message = uploadData(save_path)
        elif dataType == "rooms":
            message = uploadRoomData(save_path, listing)

        print(message)

        return redirect(url_for('dashboard'))
    
    return render_template('upload.html', users=users)


@app.route('/transactions/<int:userId>', methods=['GET', 'POST'])
def usertransactions(userId):
    user = User.query.get_or_404(userId)
    transactions = Transactions.query.filter_by(userId = str(user.id), paid=True).all()
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




@app.route('/updateBalance', methods=['GET', 'POST'])
def updateBalance():
    listing = Listing.query.get_or_404(1)

    expectedRevenue = 0
    amountRecieved = 0

    for i in User.query.filter_by(listingSlug=listing.slug).all():
        print(i)
        i.balance = i.fullAmount - i.paid

        amountRecieved += i.paid
        expectedRevenue += i.fullAmount

    # Ledger entry

    listing.amountRecieved = amountRecieved
    listing.expectedRevenue = expectedRevenue



    db.session.commit()

    flash(f'Data has been updated!')
    return redirect(url_for('dashboard'))

@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    user = User.query.get_or_404(id)
    form = ProfileForm()
    if user != None:
        print(user)
        if request.method == 'POST':
            if form.validate_on_submit():
                print(form.data)

                try:
                    user.username = form.username.data
                    user.listing = form.listing.data
                    user.balance = form.balance.data
                    user.paid = form.paid.data
                    user.phone = form.phone.data
                    user.indexNumber = form.indexNumber.data
                    user.fullAmount = form.fullAmount.data
                    user.email = form.email.data
                    db.session.commit()

                    flash(f'' + user.username+' has been updated successfully')
                    return redirect(url_for('dashboard'))
                except Exception as e:
                    print(e)
                    reportError(e)
                    flash(f'Updating of your profile failed, please check and try again')
        
            else:
                print(form.errors)
                flash(form.errors[0])

        elif request.method == 'GET':
            form.username.data = user.username
            form.listing.data = user.listing
            form.balance.data = user.balance
            form.phone.data = user.phone
            form.indexNumber.data = user.indexNumber
            form.fullAmount.data = user.fullAmount
            form.email.data = user.email
            form.paid.data = user.paid
        return render_template('profile.html', user=user, form=form)
    else:
        return render_template('404.html', message = "The user you chose cant be found")



if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0",debug=True)