from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, DateField, FloatField,SubmitField, BooleanField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea

class FindUser(FlaskForm):
    hostel = SelectField('Hostel', choices=[('CU Female Annex', 'CU Female Annex')]) #Api call for all rooms
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    submit = SubmitField('Proceed')

class BroadcastForm(FlaskForm):
    group = SelectField('Group', choices=[('All Tenants'),('Debtors')])
    message = StringField('Message',widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Broadcast')

class FindRecUser(FlaskForm):
    organisation = SelectField('Organisation', choices=[('CU Female Annex', 'CU Female Annex')]) #Api call for all rooms
    phone = StringField('Phone Or Index Number', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    submit = SubmitField('Proceed')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SelectSubListingForm(FlaskForm):
    name = StringField('Name')
    location = SelectField('Location', choices=['All Floors'])
    bedsAvailable = SelectField('Beds Available', choices=['All Beds'])
    size = SelectField('Size', choices=['All Sizes'])
    submit = SubmitField('Search')


class ProntoProfileFormPersonalInformation(FlaskForm):
    firstname = StringField('First Name')
    middlename = StringField('Middle Name(s)')
    surname = StringField('Surname')
    personalPhoneNumber = StringField('Personal Phone Number')
    checkInDate = DateField('When do you intend to check in')
    submit = SubmitField('Next')

class ProntoProfileFormEducationInformation(FlaskForm):
    studentId = StringField('Student Id')
    course = SelectField('Course', choices=['Default'])
    level = SelectField('Level', choices=[level for level in range(100, 700, 100)]+['ATHE', 'Diploma'])
    submit = SubmitField('Next')
    

class ProntoProfileFormEmergencyInformation(FlaskForm):
    name = StringField('Name Of Emergency Contact')
    number = StringField('Phone Number')
    relationship = SelectField('Relationship To Emergency Contact', choices=['Daddy'])
    submit = SubmitField('Done')

class RefundForm(FlaskForm):
    name = StringField('Name')
    amount = StringField('Refund Amount', validators=[DataRequired()])
    indexNumber = StringField('Index Number')

    reason = StringField('Reason', widget=TextArea(), validators=[DataRequired()])

    contact = StringField('A phone number we can reach you on.')
    transactionType = SelectField('Transaction Type', choices=[('Default','Default'),('Refund', 'Refund')])
    submit = SubmitField('Request Refund!')

class PaymentForm(FlaskForm):
    name = StringField('Name')
    amount = StringField('Transaction Amount', validators=[DataRequired()])
    indexNumber = StringField('Index Number')
    transactionType = SelectField('Transaction Type', choices=['Default'])
    note = StringField('Leave A Note.')
    submit = SubmitField('Proceed')

class TenancyPeriodForm(FlaskForm):
    name = StringField('Name')
    startDate = DateField('Start Date', validators=[DataRequired()])
    endDate = DateField('End Date', validators=[DataRequired()])
    reservationStartDate = DateField('Open Reservations', validators=[DataRequired()])
    reservationEndDate = DateField('Close Reservations', validators=[DataRequired()])
    reservationMinimum = IntegerField('Minimum Reservation Amount', validators=[DataRequired()])
    submit = SubmitField('Create Reservation')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')



class FeedbackForm(FlaskForm):
    name = StringField('Name')
    title = StringField('Title')
    issue = StringField('Description', widget=TextArea(), validators=[DataRequired()])
    
    email = StringField('Email')
    phoneNumber = StringField('Phone Number')
    description = StringField('Your Feedback')

    info = StringField('Extra Information')
    submit = SubmitField('Report!')


class ListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = EmailField('Name', validators=[DataRequired()])
    # password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    # confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Your passwords dont match, please try again')])
    
    description = StringField('Description')
    location = SelectField('Region', choices=['Greater Accra','Greater Accra'])
    locationTag = StringField('LocationTag')
    images = StringField('Images')
    suggestions = StringField('Suggestions')
    submit = SubmitField('Upload')

class SubListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = StringField('Description')
    quantity = IntegerField('Quantity')
    submit = SubmitField('Create')

class UserListing(FlaskForm):
    sublisting = SelectField('Network', choices=[('','--Select--'),('MTN', 'MTN'),('VODAFONE','VODAFONE'),('AIRTELTIGO','AIRTELTIGO')]) #Api call for all rooms
    submit = SubmitField('Done')

class ProfileForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    indexNumber = StringField('Index Number')
    roomNumber = StringField('Room Number')
    listing = StringField('Listing')
    picture = StringField('Picture')

    balance = FloatField('Balance')
    paid = FloatField('Paid')
    fullAmount = FloatField('FullAmount')
    submit = SubmitField('Update')

class OnboardForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    listing = SelectField('Listing', choices=[]) #Api call for all rooms
    password = PasswordField('Password', validators=[Length(min=6)])
    # confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Your passwords dont match, please try again')])
    submit = SubmitField('Update')

class RegisterForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    organisation = SelectField('Listing', choices=[]) #Api call for all rooms
    password = PasswordField('Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Your passwords dont match, please try again')])
    submit = SubmitField('Update')


class Enquiry(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    contact = StringField('Phone Number', validators=[DataRequired()])
    note = StringField('What do you want to know', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Enquire')
