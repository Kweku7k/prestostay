import csv
import datetime
import json
import os
from flask import Flask, flash,redirect,url_for,render_template, request
from flask_login import current_user, login_user, logout_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from itsdangerous import Serializer
from flask_bcrypt import Bcrypt
from utils import apiResponse, send_sms, sendTelegram
from flask_login import  LoginManager
from forms import *
import pprint
import time
import requests

app=Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'c280ba2428b2157916b13s5e0c676dfde'
app.config['SQLALCHEMY_DATABASE_URI']= "sqlite:///test.db"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

prestoUrl = "https://prestoghana.com"
baseUrl = "stay.prestoghana.com"
merchantID = "x"

environment = os.environ["ENVIRONMENT"]
# This value confirms the server is not null
server = os.environ["SERVER"]


#  ----- LOGIN MANAGER
@login_manager.user_loader
def user_loader(user_id):
    #TODO change here
    return User.query.get(user_id)

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
    description = db.Column(db.String)
    location = db.Column(db.String)
    locationTag = db.Column(db.String)
    images = db.relationship('Image', backref='listing', lazy=True)
    suggestions = db.relationship('Suggestions', backref='listing', lazy=True)

    def __repr__(self):
        return f"Listing('id: {self.id}', 'name:{self.suggestion}', 'location:{self.location}')"

class SubListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    description = db.Column(db.String)
    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'))
    superListing = db.Column(db.Integer, db.ForeignKey('listing.name'))
    
    def __repr__(self):
        return f"SubListing('id: {self.id}', 'name:{self.name}', 'superlisting:{self.listingId}'. '{self.superListing}')"

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)

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
    indexNumber = db.Column(db.String)
    hostel = db.Column(db.String)
    listing = db.Column(db.String)
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
        return '<User {}>'.format(self.username)


class Transactions(db.Model):
    tablename = ['Transactions']

    id = db.Column(db.Integer, primary_key=True)
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
        location=body.get("location"),
        locationTag=body.get("locationTag"),
        images=body.get("images"),
        suggestion = body.get("suggestion")
        )

    try:
        db.session.add(new_listing)
        db.session.commit()
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
        username=body.get("username"),
        roomID=body.get("roomID"),
        amount=body.get("amount"),
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
            "callbackUrl":prestoUrl+"/confirm/"+str(transaction.id),#TODO: UPDATE THIS VALUE
            "firstName":user.username,
            "network":transaction.network
        }

    response = requests.post(prestoUrl+"/korba", json=paymentInfo)

    app.logger.info("-----prestoPay------")
    app.logger.info(paymentInfo)
    app.logger.info(prestoUrl)
    status = response
    status = response.status_code
    app.logger.info(status)
 
    try:
        transaction.ref = response.json()["transactionId"]
        transaction.requested = True
        transaction.prestoTransactionId = response.json()["transactionId"]
        db.session.commit()
    except Exception as e:
        app.logger.info("e")
        app.logger.info(e)
        app.logger.info("Couldnt set transaction reference!")

    # if transaction.network == "CARD"

    if transaction.network == 'CARD':
                # create korba - presto transaction here and assign to orderId
        app.logger.info(transaction.network)
        # transaction = korbaCheckout(candidate, amount, phone)
        description = "Buying "+ str(transaction.amount) +" votes for "+ str(transaction.username) + " "+str(candidate.award) + " election."
        callbackUrl = baseUrl+str(transaction.id)
        app.logger.info(callbackUrl)
        
    responseBody = {
        "transactionId":transaction.id,
        "orderId":prestoUrl+transaction.ref,
        "merchantID" : merchantID ,
        "description" : "Buying "+ str(transaction.amount) +" votes for "+ str(user.username) + " " + str(transaction.listing) + " election.",
        "callbackUrl" :  baseUrl+str(transaction.id)
    }

    return responseBody

def confirmPrestoPayment(transaction):
    r = requests.get(prestoUrl + '/verifykorbapayment/'+transaction.ref).json()
    
    app.logger.info(r)
    app.logger.info("--------------status--------------")
    status = r.get("status")
    app.logger.info(status)


    app.logger.info("--------------server--------------")
    app.logger.info(server)

    if status == 'success' or environment == 'DEV' and server == "LOCAL":

        app.logger.info("Attempting to update transctionId: " +str(transaction.id) + " to paid! in " + environment + "environment || SERVER:" + server)
        
        # findtrasaction, again because of the lag.
        state = Transactions.query.get_or_404(transaction.id)
        if state.paid != True:
            try:
                state.paid = True
                db.session.commit()
                app.logger.info("Transaction : "+str(transaction.id) + " has been updated to paid!")

            except Exception as e:
                app.logger.info("Failed to update transctionId: "+str(transaction.id )+ " to paid!")
                app.logger.error(e)
                reportError(e)

            return True
        return False

    else:
        app.logger.info(str(transaction.id) + " has failed.")
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
        app.logger.error("Couldnt create vote for " + transaction.username)

    try: #Attatch vote to candidate
        user = User.query.get_or_404(int(transaction.userId))
        
        transaction.balanceBefore = user.balance
        transaction.balanceAfter = user.balance - newLedgerEntry.amount

        app.logger.info("----------------------- Updating balance ---------------------------")
        app.logger.info("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        sendTelegram("Attempting to update " + user.username + " balance from " + str(transaction.balanceBefore) + " to " + str(transaction.balanceAfter))
        
        user.balance -= newLedgerEntry.amount
        transaction.ledgerEntryId = newLedgerEntry.id

        db.session.commit()

        app.logger.info("----------------------- Updated Successfully! ---------------------------")

    except Exception as e:
        app.logger.error("Updating user " + user.username + " balance has failed." )
        app.logger.error(e)
        reportError(str(e))

    return newLedgerEntry

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
                user = User(username = row["Name"], password = "0000",email = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')+row["Index Number"]+"@prestoghana.com", phone = row["Number"], indexNumber=row["Index Number"], listing="Pronto Hostel", paid=row["Paid"], roomNumber=row["Room Number"], fullAmount=row["Full Amount"], balance=row["Balance"] )
                db.session.add(user)
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
    return render_template('landingpage.html')

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

@app.route('/newlisting', methods=['GET', 'POST'])
def newlisting():
    form = ListingForm()

    if form.validate_on_submit():
        newListing = createListing(form.data)
        pprint.pprint(newListing)
    else:
        print(form.errors)

    return render_template('newlisting.html', form=form, current_user=None)

@app.route('/allusers', methods=['GET', 'POST'])
def getallusers():
    users = User.query.all()
    return render_template('allusers.html', users=users)

@app.route('/onboard', methods=(['POST','GET']))
def onboard():
    form = OnboardForm()
    if current_user:
        logout_user()
        print ("You have been logged out")
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        newuser = User(username=form.username.data, email=form.email.data, phone=form.phone.data, password=hashed_password)
        try:
            db.session.add(newuser)
            db.session.commit()
            send_sms(newuser.phone, "You have been successfully onboarded to PrestoPay. \nhttps://prestoghana.com/dashboard \nYour username is "+ newuser.username+ "\nIf you need any form of support you can call +233545977791 ")
        except Exception as e:
            print("User was not able to be created")
        print("Registered new user: " + newuser.username + " " + newuser.email)
        print(form.password.data)
        print(form.confirm_password.data)

        user = User.query.filter_by(email=form.email.data).first()

        try:
            login_user(user, remember=True) 
        except:
            print("could not log current user in")
        return redirect(url_for('pay', userId=user.id))
    else:
        print(form.errors)
    return render_template('onboard.html', form=form, title="Onboard New User")

@app.route('/findme', methods=['GET', 'POST'])
def findme():
    form = FindUser()
    if form.validate_on_submit():
        user = User.query.filter_by(phone = form.phone.data).first()
        return redirect(url_for('pay', userId=user.id))
        # return render_template('confirmUser.html', user=user, form=form)
    return render_template('pay.html', current_user=None, form=form)

# YET TO  BE WORKED ON!

@app.route('/pay/<int:userId>', methods=['GET','POST'])
def pay(userId):
    user = User.query.get_or_404(userId)
    form = PaymentForm()
    if request.method == 'POST':
        if form.validate_on_submit():

            body={
                "userId":user.id,
                "username":user.username,
                "roomID":user.roomNumber,
                "amount":form.amount.data,
                "balanceBefore":user.balance,
                "account":form.account.data, 
                "network":form.network.data,
                "channel":"WEB"
            }

            transaction = createTransaction(body)

            response = payWithPrestoPay(transaction)
            print(response)

            return redirect(url_for('transaction', transactionId=transaction.id))
        else:
            print(form.errors)
            flash(form.errors[0])
    return render_template('confirmUser.html', user=user, form=form)

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
    message = "In Progress"

    transaction = Transactions.query.get_or_404(transactionId)

    if transaction.paid == False:
        message = "Failed Transaction"
        if confirmPrestoPayment(transaction) == True:

            message = "Duplicate"
            entry = updateUserBalance(transaction)
            if entry != None: #If a vote was created
                # message = "You have successfully bought " + str(entry.amount) + " vote(s) for " + transaction.username + "\n TransactionID: " + str(transaction.id)+"PRS"+str(transaction.ref) + "\n \n Powered By PrestoStay"
                
                message = "Student Name:"+ str(transaction.username) + "\n Hostel Name: "+transaction.listing + "Fee Amount:" + transaction.amount + "\n Payment Method:"+transaction.channel + "\nPayment  Date" + transaction.date_created + "Receipt Number: PRS" + str(transaction.id) + "REF" + str(transaction.ref) +"Your payment has been received."

                app.logger.info("send_sms || PrestoStay)")
                send_sms(transaction.account, message)

                responseMessage = transaction.listing + "\nSuccessfully bought " +str(transaction.amount) + " for " + str(transaction.username) + "." + "\nBefore: " + str(transaction.votesBefore) + "\nAfter: "+ str(transaction.balanceAfter) + "\nTransactionId:" + str(transaction.id) + "\nAccount:" + str(transaction.network) + " : "+ str(transaction.account) + "\nVoteId: " + str(entry.id)
                print(responseMessage)
                app.logger.info(responseMessage)
                sendTelegram(responseMessage)
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
    app.logger.info(responseBody)
    return responseBody

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    activeUsers = User.query.count()
    availableBalance = 1072.00
    expected_revenue = 1672.00
    due = expected_revenue - availableBalance
    todaysBalance = 0
    totalTransasactions = 20
    print(activeUsers)
    return render_template('dashboard.html', user=current_user, activeUsers=activeUsers, totalTransasactions=totalTransasactions,todaysBalance=todaysBalance,availableBalance=availableBalance, due=due,expected_revenue=expected_revenue)



@app.route('/upload', methods=['GET', 'POST'])
def upload():
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
    
        message = uploadData(save_path)
        print(message)

        return redirect(url_for('dashboard'))

       


    
    return render_template('upload.html')


@app.route('/transactions/<int:userId>', methods=['GET', 'POST'])
def usertransactions(userId):
    user = User.query.get_or_404(userId)
    transactions = Transactions.query.filter_by(userId = user.id).all()
    print(transactions)
    return render_template('alltransactions.html', user=user,transactions=transactions)

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0",debug=True)