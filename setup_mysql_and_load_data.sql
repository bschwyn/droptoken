CREATE USER '98point6'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO '98point6'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE benschwyn_droptoken;
USE benschwyn_droptoken;

SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

CREATE TABLE game_data (
game_id VARCHAR(255),
player_id INT,
move_number INT,
column_number INT,
result VARCHAR(255));

CREATE TABLE games_won_per_column (
column_number INT,
games INT);

CREATE TABLE games_and_players (
game_id varchar(255),
player1 INT,
player2 INT,
last_player INT,
result VARCHAR(11));

CREATE TABLE apitable (
player_id INT,
nation VARCHAR(255));


LOAD DATA LOCAL INFILE './game_data.csv'
INTO TABLE game_data
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;