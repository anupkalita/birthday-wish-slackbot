# birthday-wish-slackbot
Birthday wish slack bot using python

## Features:
1. It can read messages from the slack channel
2. It can post messages to the slack channel
3. It can get the birthday details from the user and store it in the database.
4. It can send birthday wishes to the user in the slack channel
5. It can View Birthday details
6. It can remove Birthday details
7. It can used to read jokes
8. It can get weather report of a particular city

## Usage:
* User has to give their birthday details and user name as a message in the slack channel in this format-
`bday/<day>-<month>/<username>`
* To show Bday Details - `show/`
* To remove Bday Details - `rm-bday/<date>/<name>/<user_id>`
* To See Jokes - `joke/`
* To get weather report of a particular city - `weather/<city>`

## Tech Used
1. Python
2. ngrok - It is the server which will listen to the slack events
3. slackeventsapi - It is used to access the slack api. eg: messages, user_id etc
