


### Introduction

This is my work sample for 98point6! It has a MySQL database that contains moves and other information for the connect-4 like game "droptoken".

### Installation and Setup

Download repository:

```
clone https://github.com/bschwyn/droptoken
cd droptoken
```

Make the setup file executable and run it. This will set up a python virtual environment with python3, install the required modules, install MySQL, setup the MySQL database, user, tables, and settings, and load the data from the game_data csv file. It will then run a script which will page through the api to load the relevant player data into the database.

```
chmod +x setup.sh
sudo ./setup.sh
```

! there may be a problem with sudo source venv/bin/activate
and in this case you will likely need to activate the python virtual environment once it is installed. Do this via:

```source venv/bin/activate```

and make sure to run install the requirements with this activated.

### Usage

To create views for all of the questions, run:

```python droptoken.py```


Views for the questions can be created individually by including the question number as a command line argument

For example:

```python droptoken.py -1 -2``` or ```python droptoken.py -12``` 

to create views for questions 1 and 2.

A reminder:
- Question 1 is about 'what is the percent rank of each column used as the first move of the game?'
- Question 2 is 'how many games did each nation play'
- Question 3 is 'create a list of players that played a single game that they either won, lost or drew' 

For question 3, if you want to create a view for only one outcome, then include which type in the CLI, for example: 
```python droptoken -3 win``` 

### Views

After all of the queries are run, the view names can be accessed by:

- Q1: games_won_per_column or percentile_column_rank
- Q2: games_per_nation
- Q3: single_player_game_win, single_player_game_lose, single_player_game_draw

### Testing

To run tests, run:

```pytest```
or
```pytest droptoken.py```



### Database Choice

There were several considerations in my choice of database:
- The first consideration was whether to use a relational database or not. Speed, while a consideration, was not of p
paramount importance, and the data was flat and simply structured. I wanted to be able to have the user ask complex questions that a key-value store would not be suited for. While scalability was a concern, the amount of data was not so large that a distributed systemwas necessary.

  I chose to use a SQL relational database rather than a NoSQL database. 
  
- Ease of installation and cost. As a individual consumer it was important to use open source software. While PostGres has a large number of options and settings that would be useful, my system did not need to be complex and I found MySQL to be simpler to set up. Both databases would have been reasonable choices.

### Memory, Speed, and Scalability analysis

The size of the game_data file is 2.3 MB for 145k rows of data, about 16 bytes/line or 229 bytes/game.

For a 1000x increase in games, this goes to 2.3 GB, which is small enough to fit in memory on a single device, so there is no need to consider extra large or distributed systems. (yet!)

To collect data from the API takes about 2 minutes to go through 500 pages of 10 players each. This is a reasonable amount of time for a single query, but becomes untenable as the system scales.  A 1000x increase in the number of players causes a query involving all of the player data to take multiple days. This amount of data would go from ~5MB initially to ~5GB.

### Storing the API data

A solution for the query time was necessary, so I elected to download the player data once into a database. A different database could have been used, but using the same MySQL database would make queries easy. There was also a choice for how to store the data, as it was originally in json. 
One possibility was to put the json data directly into MySQL, however if there were missing fields in the json data this could cause errors in queries.

I think it is better to extract the desired fields from the json and do any transformation or cleaning of it before putting it into MySQL, though I would be interested in hearing the opinions of other engineers on this.

### Future Work

Errors:

One of the things that I do not know much about best practices for, is what to do with errors, and the replacement of 
data w/ errors. Some of the game_ids in the droptoken dataset are strings of characters, rather than numbers. Given the data, it would be possible to write a function that figures out the correct game_id based off of it's relative numerical position compared to other data. (i.e. go back to the previous numbered gameid and increment it to get the right one). In this case it seems quite easy to find the correct data from the error-filled data. However, if, say, column_number was incorrect, it would be quite difficult to figure out.

It seems likely that cleaning of the data would need to be handled on a case by case basis. It also needs to be decided whether to handle this before, during, or after the upload of the data, as the types in the database tables are set.

Uploading data:

In a working system, presumably the games are coming from somewhere and database updates need to occur. Perhaps we can talk about this!

Tests:

I would have liked to get a module working that mocked out database functions. This would have allowed me to run the same functions on simple data sets that were hand-verifiable.
Many of the tests that I did while creating the queries were 'order of magnitude / ballpark' tests. I would have liked to write these up.

Automation:

There may be some errors here, or lack of flexibility if something failes. I also expect that there  are better ways of doing this, such as dedicated config files.