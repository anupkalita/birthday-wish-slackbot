from datetime import datetime
import slack
from flask import Flask
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter("5b3f3da259964d55f4af3a68bd6ccc3f", "/slack/events", app)

client = slack.WebClient(token="xoxb-3140197001491-3153889557873-COM2kYTjSErrlhWsWzXyfn5a")
# client.chat_postMessage(channel="#random", text="Hi")
BOT_ID = client.api_call("auth.test")["user_id"]
x = datetime.now()
current_date = str(x.day) + "-" +str(x.month)
print(current_date)
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
