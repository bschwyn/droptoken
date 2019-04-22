#!/bin/bash

echo "Downloading and installing latest updates"
apt-get update
apt-get upgrade -y

########### python
echo "Setting up python3 virtual environment"
#install python virtual environment
apt-get install python3-venv
python3 -m venv venv

echo "Other installations necessary for mysqldb python"
apt-get install python3-dev libmysqlclient-dev

# look at  https://askubuntu.com/questions/234758/how-to-use-a-python-virtualenv-with-sudo

echo "Activate virtual environment"
source venv/bin/activate

echo "Installing requirements"
pip install -r requirements.txt

############ mysql

echo "Installing mysql-server"
apt-get install mysql-server

echo "Setting up mysql user, options, and loading data from game_data.csv"
mysql < ./setup_mysql_and_load_data.sql

echo "Running script to load data from Player API into database"
python api_script.py