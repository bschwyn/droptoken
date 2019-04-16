#!/bin/bash

echo "Downloading and installing latest updates"
apt-get update
apt-get upgrade -y

########### python
echo "Setting up python3 virtual environment"
#install python virtual environment
apt-get install python3-venv
python3 -m venv venv

echo "Activate virtual environment"
source venv/bin/activate

echo "Other installations necessary for mysqldb python"
apt-get install python3-dev libmysqlclient-dev

echo "Installing requirements"
pip install -r requirements.txt

############ mysql

echo "Installing mysql-server"
apt-get install mysql-server

echo "Setting up mysql user, options, and loading data from game_data.csv"
mysql < ./setup_mysql_and_load_data.sql

echo "MySQL user created."
echo "Username:   98point6"
echo "Password:   password"
echo "game_data.csv loaded"

echo "Running script to load data from Player API into database"
python api_script.py