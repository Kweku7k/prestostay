#!/bin/bash

#Delete the previous environment
sudo rm -r env

# Set the name of the virtual environment
venv_name="env"

# Create a new virtual environment
python3 -m venv $venv_name

# Activate the virtual environment
source $venv_name/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install uwsgi
pip install uwsgi

#Restart the forms application
sudo systemctl restart stay.service

# Deactivate the virtual environment
#deactivate