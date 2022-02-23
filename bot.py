from datetime import datetime
import slack
from flask import Flask
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter("SLACK_EVENT_TOKEN", "/slack/events", app)

client = slack.WebClient(token="SLACK_BOT_TOKEN")
# client.chat_postMessage(channel="#random", text="Hi")
BOT_ID = client.api_call("auth.test")["user_id"]

# get current date
x = datetime.now()
current_date = str(x.day) + "-" +str(x.month)
print(current_date)

#fetch messages from slack using slack api
@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if(BOT_ID != user_id):
        if text.startswith("bday/"):
            msg = "Happy Birtday"
            user_details = text.split("/")
            user_details.append(user_id)
            user_details.append(msg)
            print(user_details)

            if user_details[1] == current_date:
                client.chat_postMessage(channel=channel_id, text=f"happy birthday {user_details[2]}")
        # else:
        #     client.chat_postMessage(channel=channel_id, text=text)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
