import os
import json
import time

# https://github.com/slackapi/python-slackclient
# pip install slackclient
from slackclient import SlackClient

# This script invites all full members of a workspace to a particular channel

# To use this script:
# 1. set the channel ID below
# 2. set a desired delay, or 0 if none is desired
# 3. get yourself a test token at Slack (guard it with your life)
# https://api.slack.com/custom-integrations/legacy-tokens
# Then, call the script with the following on the command line, passing the token as a environment
# variable:
# SLACK_API_TOKEN="your-token" python slack-invite.py 

# The channel ID. You can find this in the URL when using the web client, e.g. CBLS8CSAJ
channel_id = ''

# Delay - if you don't want to flood the API (in seconds) - some calls have rate limits
api_call_delay = .5


def main():
	# grab the token from the command line (so don't use this script on shared computers)
	slack_token = os.environ["SLACK_API_TOKEN"]
	sc = SlackClient(slack_token)
	invite_all(sc, api_call_delay, channel_id)

# Invite a single user to a channel
# The user name is just for printing, it could be blank

def invite_user(sc, user_id, user_name, channel_id):
	print('Inviting ' + user_name + ' with ID: ' + user_id + ' to channel ' + channel_id)

	response = sc.api_call(
		"channels.invite",
		channel = channel_id,
		user = user_id)

	if response['ok']:
		print('Success')
	else:
		print('Could not add ' + user_name + ' with ID: ' + user_id + ' to channel ' + channel_id + ' Error Message: ' + response['error'])

# Invite all full members of a workspace to a particular channel
# Skip if they are bots, deleted, restricted (multi-channel guest)
# or ultra_restricted (single-channel guests)

def invite_all(sc, delay, channel):
	# https://api.slack.com/methods/users.list
	response = sc.api_call(
  		"users.list",
	)

	if response['ok']:
		users = [(u['id'], u['name'], u['deleted'], u['is_restricted'], u['is_ultra_restricted'], u['is_bot']) for u in response['members']]

		for user_id, user_name, deleted, is_restricted, is_ultra_restricted, is_bot in users:
			if (deleted or is_restricted or is_ultra_restricted or is_bot):
				next
			else:
				invite_user(sc, user_id, user_name, channel)
				time.sleep(api_call_delay)

	else:
		print('Could not get all users. Error Message: ' + response['error'])

main()
