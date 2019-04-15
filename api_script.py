
import requests
import MySQLdb #mysqlclient
import sys

def upload_to_database(cursor, id,nation):
    query = "INSERT INTO apitable (player_id, nation) VALUES(" + str(id) + ", '" + str(nation) + "');"
    print(query, file=sys.stderr)
    cursor.execute(query)

def parse_json_and_upload(json_array, cursor):
    for object in json_array:  #10 objects
        id = object['id']
        nat = object['data']['nat']
        upload_to_database(cursor, id, nat)

def get_data_from_api(cursor):
    params = {'Accept': 'application/json'}
    url = 'https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users?page='
    page = 0
    r = requests.get(url=url + str(page), params=params)
    # iterate through entire json player library thing (should take approx 5 minutes)
    json_array = r.json()
    while json_array:  # while json is not empty...
        parse_json_and_upload(json_array, cursor)
        page += 1
        r = requests.get(url=url + str(page), params=params)
        json_array = r.json()

def create_table(cursor):
    cursor.execute("CREATE TABLE apitable (player_id INT, nation VARCHAR(255));")

def main():
    db_connection = MySQLdb.connect(host="localhost",  # your host, usually localhost
                                    user="98point6",  # your username
                                    passwd="password",  # your password
                                    db="mydb")
    cursor = db_connection.cursor()
    create_table(cursor)
    get_data_from_api(cursor)
    db_connection.commit()

    db_connection.close()


if __name__ == "__main__":
    main()
