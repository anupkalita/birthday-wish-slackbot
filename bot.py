from datetime import datetime
from multiprocessing import connection
from click import command
import slack
from flask import Flask
from slackeventsapi import SlackEventAdapter
import sqlite3
import requests
import json

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter("5b3f3da259964d55f4af3a68bd6ccc3f", "/slack/events", app)

client = slack.WebClient(token="xoxb-3140197001491-3153889557873-tqrm3XcbC2y3gKE1F8FhRRCn")

BOT_ID = client.api_call("auth.test")["user_id"]
x = datetime.now()
current_date = str(x.day) + "-" +str(x.month)
current_year = str(x.year)
# print(current_date, current_year)

#sql connection
connection = sqlite3.connect("bday.db")

cursor = connection.cursor()

command1 = """
    CREATE TABLE IF NOT EXISTS bday_details(id INTEGER PRIMARY KEY, date TEXT, name TEXT, user_id TEXT, channel_id TEXT)
"""
cursor.execute(command1)


#function to wish bday
def bday_wish():
    #sql connection
    connection = sqlite3.connect("bday.db")
    cursor = connection.cursor()

    command2 = """
    CREATE TABLE IF NOT EXISTS bday_wishes(id INTEGER PRIMARY KEY, date TEXT, name TEXT, user_id TEXT, channel_id TEXT, year TEXT)
    """
    cursor.execute(command2)

    cursor.execute("SELECT * FROM bday_details")
    results = cursor.fetchall()

    for i in results:
        bdate = i[1]
        name = i[2]
        id =  i[3]
        channel_id = i[4]
        cursor.execute("SELECT * FROM bday_wishes")
        wishes = cursor.fetchall()
        flag = 0
        for j in wishes:
            wdate = j[1]
            u_id = j[3]
            year = j[5]
            if bdate == wdate and id == u_id and current_year == year:
                flag = 1
        if flag == 0 and bdate == current_date:
            client.chat_postMessage(channel=channel_id, text=f"Happy Birthday {name.upper()}")
            cursor.execute("INSERT INTO bday_wishes VALUES(NULL,?, ?, ?, ?, ?)", (f"{bdate}", f"{name}", f"{id}", f"{channel_id}", f"{current_year}"))
  
    
    connection.commit()
    connection.close()
  
#store user bday details
def get_bday_details(text, user_id, channel_id):
    #sql connection
    connection = sqlite3.connect("bday.db")
    cursor = connection.cursor()

    user_details = text.split("/")
    user_details.append(user_id)
    user_details.append(channel_id)
    print(user_details)

    cursor.execute("SELECT * FROM bday_details")
    results1 = cursor.fetchall()

    flag = 0
    for i in results1:
        if i[3] == user_details[3]:
            print("Data present already")
            flag = 1
            client.chat_postMessage(channel=channel_id, text=f"{user_details[2]}'s details is already stored")
            break

    if flag==0:
        cursor.execute("INSERT INTO bday_details VALUES(NULL,?, ?, ?, ?)", (f"{user_details[1]}", f"{user_details[2]}", f"{user_details[3]}", f"{user_details[4]}"))
        client.chat_postMessage(channel=channel_id, text=f"{user_details[2]}'s details added successfully")

    bday_wish()

    connection.commit()
    connection.close()

# function to show the list of birthday
def show_bday(channel_id):
    #sql connection
    connection = sqlite3.connect("bday.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM bday_details WHERE channel_id=?", (channel_id,))
    results = cursor.fetchall()
    print(results)

    for i in results:
        client.chat_postMessage(channel=channel_id, text=f"ID-{i[3]}, {i[2]}'s birthday is on {i[1]}")

    connection.commit()
    connection.close()

def remove_bday(date, name, channel_id, id):
    #sql connection
    connection = sqlite3.connect("bday.db")
    cursor = connection.cursor()
    print(date, id, name)
    cursor.execute("DELETE FROM bday_details WHERE date==? AND user_id==? AND name==?", (date, id,name,))
    cursor.execute("DELETE FROM bday_wishes WHERE date==? AND user_id==? AND name==?", (date, id,name))
    client.chat_postMessage(channel=channel_id, text=f"{name}'s bday details removed")

    connection.commit()
    connection.close()


def joke(channel_id):
    f = r"http://api.icndb.com/jokes/random"
    data = requests.get(f)
    tt = json.loads(data.text)
    joke = tt["value"]["joke"]
    client.chat_postMessage(channel=channel_id, text=f"{joke}")


def weather(channel_id, city):
    f = f"https://weatherdbi.herokuapp.com/data/weather/{city}"
    data = requests.get(f)
    weather = json.loads(data.text)
    temp = weather["currentConditions"]["temp"]["c"]
    comment = weather["currentConditions"]["comment"]
    time = weather["currentConditions"]["dayhour"]
    degree = u"\N{DEGREE SIGN}"
    client.chat_postMessage(channel=channel_id, text=f"{time}, {temp}{degree} celsius, {comment}") 
    print(temp, city)

bday_wish()
# cursor.execute("DROP TABLE bday_wishes")
# cursor.execute("DROP TABLE bday_details")

cursor.execute("SELECT * FROM bday_details")
results = cursor.fetchall()
print(results)

cursor.execute("SELECT * FROM bday_wishes")
results = cursor.fetchall()
print(results)

#fetch messages from slack using slack api
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if(BOT_ID != user_id):
        if text.startswith("bday/"):
            get_bday_details(text, user_id, channel_id)
        
        elif text.startswith("rm-bday/"):
            details = text.split("/")
            date = details[1]
            name = details[2].lower()
            id = details[3]
            remove_bday(date, name, channel_id, id)


        elif text.startswith("show/"):
            show_bday(channel_id)
        
        elif text.startswith("joke/"):
            joke(channel_id)
        
        elif text.startswith("weather/"):
            city = text.split("/")
            city = city[1].lower()
            weather(channel_id, city)


connection.commit()
connection.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
