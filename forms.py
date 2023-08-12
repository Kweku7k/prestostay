from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea

class FindUser(FlaskForm):
    hostel = SelectField('Hostel', choices=[('Pronto Hostel', 'Pronto Hostel')]) #Api call for all rooms
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15, message="Your phone number should be more than 10 digits and less than 15")])
    submit = SubmitField('Proceed')

class PaymentForm(FlaskForm):
    # hostel = SelectField('Hostel', choices=[('','---Select---'),('Pronto Hostel', 'Pronto Hostel')]) #Api call for all rooms
    network = SelectField('Network', choices=[('','--Select--'),('MTN', 'MTN'),('VODAFONE','VODAFONE'),('AIRTELTIGO','AIRTELTIGO')]) #Api call for all rooms
    name = StringField('Name')
    amount = StringField('Amount', validators=[DataRequired()])
    indexNumber = StringField('Index Number')
    account = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15, message="Your phone number should be more than 10 digits and less than 15")])
    note = StringField('Leave A Note.')
    submit = SubmitField('Proceed')

class ListingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    locationTag = StringField('LocationTag', validators=[DataRequired()])
    images = StringField('Images')
    suggestions = StringField('Suggestions', validators=[DataRequired()])
    submit = SubmitField('Upload')

class OnboardForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Your passwords dont match, please try again')])
    submit = SubmitField('Sign Up')

class Enquiry(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    contact = StringField('Phone Number', validators=[DataRequired()])
    note = StringField('What do you want to know', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Enquire')
