
import requests
import MySQLdb
import sys

def upload_to_database(cursor, id,nation):
    query = "INSERT INTO apitable (player_id, nation) VALUES(" + str(id) + ", '" + str(nation) + "');"
    print(query, file=sys.stderr)
    cursor.execute(query)

def parse_json_and_upload(json_array, cursor):
    for object in json_array:  #10 objects per array
        try:
            id = object['id']
            nat = object['data']['nat']
            upload_to_database(cursor, id, nat)
        except KeyError as e:
            #logging missing data could be important
            print(e, file=sys.stderr)

def get_data_from_api(cursor):
    params = {'Accept': 'application/json'}
    url = 'https://x37sv76kth.execute-api.us-west-1.amazonaws.com/prod/users?page='
    page = 0
    r = requests.get(url=url + str(page), params=params)

    # iterate through all api pages (approx ~500 at current time)
    json_array = r.json()
    while json_array:  # while json is not empty...
        parse_json_and_upload(json_array, cursor)
        page += 1
        try:
            r = requests.get(url=url + str(page), params=params)
        except requests.exceptions.RequestException as e:
            print(e, file=sys.stderr)

            # In a fully automated system, I will want to handle connection errors, http errors, timeouts,
            # and do retries on connection failures

        json_array = r.json()

def main():
    db_connection = MySQLdb.connect(host="localhost",  # your host, usually localhost
                                    user="98point6",  # your username
                                    passwd="password",  # your password
                                    db="benschwyn_droptoken")
    cursor = db_connection.cursor()
    get_data_from_api(cursor)
    db_connection.commit()

    db_connection.close()


if __name__ == "__main__":
    main()
