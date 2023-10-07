from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField,SubmitField, BooleanField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea

class FindUser(FlaskForm):
    hostel = SelectField('Hostel', choices=[('CU Female Annex', 'CU Female Annex')]) #Api call for all rooms
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    submit = SubmitField('Proceed')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SelectSubListingForm(FlaskForm):
    name = StringField('Name')
    location = SelectField('Location', choices=['All Floors'])
    block = SelectField('Block', choices=['All Blocks'])
    bedsAvailable = SelectField('Beds Available', choices=['All Beds'])
    size = SelectField('Size', choices=['All Sizes'])
    # price = SelectField('Beds', choices=['All Room Types'])
    # occupancy = SelectField('Region', choices=['Greater Accra','Greater Accra'])

    submit = SubmitField('Submit')


class PaymentForm(FlaskForm):
    name = StringField('Name')
    amount = StringField('Transaction Amount', validators=[DataRequired()])
    indexNumber = StringField('Index Number')
    # account = StringField('Phone', validators=[Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    note = StringField('Leave A Note.')
    submit = SubmitField('Proceed')

class ListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    # location = StringField('Location', validators=[DataRequired()])
    location = SelectField('Region', choices=['Greater Accra','Greater Accra'])
    locationTag = StringField('LocationTag')
    images = StringField('Images')
    suggestions = StringField('Suggestions')
    submit = SubmitField('Upload')

class SubListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    quantity = IntegerField('Quantity')
    submit = SubmitField('Create')

class UserListing(FlaskForm):
    sublisting = SelectField('Network', choices=[('','--Select--'),('MTN', 'MTN'),('VODAFONE','VODAFONE'),('AIRTELTIGO','AIRTELTIGO')]) #Api call for all rooms
    submit = SubmitField('Done')

class ProfileForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    indexNumber = StringField('Index Number', validators=[DataRequired()])
    listing = StringField('Listing', validators=[DataRequired()])

    balance = FloatField('Balance')
    paid = FloatField('Paid')
    fullAmount = FloatField('FullAmount')

    submit = SubmitField('Update')

class OnboardForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    listing = SelectField('Listing', choices=[]) #Api call for all rooms
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Your passwords dont match, please try again')])
    submit = SubmitField('Update')

class Enquiry(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    contact = StringField('Phone Number', validators=[DataRequired()])
    note = StringField('What do you want to know', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Enquire')
