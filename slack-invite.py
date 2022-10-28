import os
import json
import time

# https://github.com/slackapi/python-slack-sdk
# python3 -m venv <your installation directory>
# source bin/activate
# pip install slack_sdk
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# This script invites all full members of a workspace to a particular channel

# To use this script:
# 1. set the channel ID below
# 2. set a desired delay, or 0 if none is desired
# 3. create an app here: https://api.slack.com/apps
# 4. Set user scopes as needed. The list of user scopes required can be found in the documentation:
# 	https://api.slack.com/methods/conversations.members
# 	https://api.slack.com/methods/conversations.invite
# Then, call the script with the following on the command line, passing the token as a environment
# variable:
# SLACK_API_TOKEN="your-token" python slack-invite.py 

# The channel ID. You can find this in the URL when using the web client, e.g. CBLS8CSAJ
channel_id = ''

# The source channel ID (if used). You can find this in the URL when using the web client, e.g. CBLS8CSAJ
source_channel_id = ''

# Delay - if you don't want to flood the API (in seconds) - some calls have rate limits
api_call_delay = .5


def main():

	# grab the token from the command line (so don't use this script on shared computers)
	slack_token = os.environ["SLACK_API_TOKEN"]
	client = WebClient(token=slack_token)

	# invite all workspace users to a channel
	invite_all(client, api_call_delay, channel_id)

	#members = list_all_channel_members(client, channel_id)
	#print(members)

	#copy_members_between_channels(client, api_call_delay, channel_id, source_channel_id)

	# invite all members of one (private) source channel to another channel
	#invite_private_channel_members(sc, api_call_delay, channel_id, source_channel_id)


#------------------------------------------------------------------------------
#
# Invite all full members of a workspace to a particular channel
#
#------------------------------------------------------------------------------

def invite_all(client, delay, channel_id):

	users = list_all_users(client)

	# this batches the invites and is faster, but an error could stop one of the
	# batches from being imported
	invite_multiple_users_to_channel(client, delay, channel_id, users)


	# this invites users individually
	for u in users:
		invite_user(client, u['id'], u['name'], channel_id)
		time.sleep(delay)


#------------------------------------------------------------------------------
#
# Invite multiple members to a channel
#
#------------------------------------------------------------------------------

def invite_multiple_users_to_channel(client, delay, channel_id, users):

	user_ids = []

	# grab just the IDs of the users
	for u in users:
		user_ids.append(u['id'])

	chunks = list(split(user_ids, 200))

	for chunk in chunks:
		invite_users(client, ','.join(chunk), channel_id)
		time.sleep(delay)


#------------------------------------------------------------------------------
#
# Invite a single user to a channel
# The user name is just for printing, it could be blank
#
#------------------------------------------------------------------------------

def invite_user(client, user_id, user_name, channel_id):

	try:
		print('Inviting ' + user_name + ' with ID: ' + user_id + ' to channel ' + channel_id)
		client.conversations_invite(channel=channel_id, users=user_id)

	except SlackApiError as e:
		print('Could not add ' + user_name + ' with ID: ' + user_id + 'to channel ' + channel_id + " Error: {}".format(e))

#------------------------------------------------------------------------------
#
# Invite multiple users to a channel
# users is a string of IDs, separated by commas
#
#------------------------------------------------------------------------------

def invite_users(client, users, channel_id):

	try:
		print('Inviting ' + str(len(users.split(","))) + ' users to channel ' + channel_id)
		client.conversations_invite(channel=channel_id, users=users)

	except SlackApiError as e:
		print('Could not add users to channel ' + channel_id + " Error: {}".format(e))

#------------------------------------------------------------------------------
#
# Invite all members of a specific, private channel to another public channel
#
#------------------------------------------------------------------------------

def copy_members_between_channels(client, delay, channel_id, source_channel_id):

	source_channel_members = list_all_channel_members(client, source_channel_id)

	for user_id in source_channel_members:
		invite_user(client, user_id, 'user', channel_id)
		time.sleep(delay)

#------------------------------------------------------------------------------
#
# Return a list of all regular members (no bots, single channel, etc.)
#
#------------------------------------------------------------------------------

def list_all_users(client):

	users = []
	full_members = []

	try:
		# get list of members
		users = list_users_with_pagination(client, users, False)

		# filter out single channel members, etc.
		for u in users:
			if (u['deleted'] or u['is_restricted'] or u['is_ultra_restricted'] or u['is_bot']):
				next
			else:
				full_members.append(u)

		return full_members

	except SlackApiError as e:
		print("Error: {}".format(e))


#------------------------------------------------------------------------------
#
# Return a list of all users, supports pagination for larger result sets
#
#------------------------------------------------------------------------------

def list_users_with_pagination(client, users, cursor):

	limit = 500

	try:
		# get list of members
		if (cursor):
			response = client.users_list(limit=limit, cursor=cursor)
			users = users + response["members"]

		else:
			response = client.users_list(limit=limit)
			users = users + response["members"]

		if response['response_metadata']:
			cursor = response['response_metadata']['next_cursor']
			if cursor:
				users = list_users_with_pagination(client, users, cursor)
			else:
				return users

	except SlackApiError as e:
		print("Error: {}".format(e))	

	return users

#------------------------------------------------------------------------------
#
# Return a list of all members from a channel
#
#------------------------------------------------------------------------------

def list_all_channel_members(client, channel_id):

	users = []

	try:
		# get list of members
		users = list_channel_members_with_pagination(client, channel_id, users, False)

		return users

	except SlackApiError as e:
		print("Error: {}".format(e))


#------------------------------------------------------------------------------
#
# Return a list of all members from a channel, supports pagination
# for larger result sets
#
#------------------------------------------------------------------------------

def list_channel_members_with_pagination(client, channel_id, users, cursor):

	limit = 200

	try:
		# get list of members
		if (cursor):
			response = client.conversations_members(channel=channel_id, limit=limit, cursor=cursor)
			users = users + response["members"]

		else:
			response = client.conversations_members(channel=channel_id, limit=limit)
			users = users + response["members"]

		if response['response_metadata']:
			cursor = response['response_metadata']['next_cursor']
			if cursor:
				users = list_channel_members_with_pagination(client, channel_id, users, cursor)
			else:
				return users

	except SlackApiError as e:
		print("Error: {}".format(e))	

	return users

#------------------------------------------------------------------------------
#
# Split a list of users into chunks
#
#------------------------------------------------------------------------------

def split(list_a, chunk_size):

  for i in range(0, len(list_a), chunk_size):
    yield list_a[i:i + chunk_size]


main()
