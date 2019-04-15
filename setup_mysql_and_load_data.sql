CREATE USER '98point6'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON *.* TO '98point6'@'localhost';
FLUSH PRIVILEGES;

CREATE DATABASE mydb;
USE mydb;

CREATE TABLE game_data (
game_id VARCHAR(255),
player_id INT,
move_number INT,
column_number INT,
RESULT VARCHAR(255)
);

LOAD DATA LOCAL INFILE './game_data.csv'
INTO TABLE game_data
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));