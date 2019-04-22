


### Introduction


Droptoken takes place on a 4x4 grid, a token is dropped along a column and goes to the lowest unoccupied row of the
board. A player wins when they have 4 tokens next to ech other either along a row, in a column, or on a diagonal. If
the board is filled, and nobody has won, then the game is a draw. Each player takes a turn, starting with player 1,
until the game is either a win or a draw. If a player tries to put a token in a column that is already full, that
results in an error state, and the player must play again until the play is a valid move.

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

or

```python droptoken.py -123```

Views for the questions can be created individually by including the question number as a command line argument


```python droptoken.py -1 -2``` or ```python droptoken.py -12```  to create views for questions 1 and 2

For question 3, if you want to create a view for only one outcome, then include which type in the CLI, for example: 
```python droptoken -3 win``` 

### Testing

To run tests, run:

```pytest```




### Database Choice

For an initial test run I used the python library Pandas.

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