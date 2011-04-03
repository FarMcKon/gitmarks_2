#!/usr/bin/env python
# encoding: utf-8
"""
gitmark_add.py

Functions and classes to grab friends data from their repo 

Based on gitmarks by Hilary Mason on 2010-09-24.
Copyright 2010 by Far McKon (intermediate while picking a opensource license)
"""

import json
import settings
import os 

#TODO: add to settings.py (or other settings) when this is out
# of beta stage
FRIENDS_JSON =  "friends.json"

class friend_scraper(object):
	""" Class for scraping data from friends off of other services."""

	services_json = "services.json"
	services = {}
	publicFriends = {}
	privateFriends = {}

	def __init__(self):
		print "creating a service scraper to look for friends updates"
		fh = open(self.services_json)
		if fh:
			jsonObj = fh.read()
			fh.close()
			del fh
			self.services = json.loads(jsonObj)

	def load_private_friends(self):
		print "load private friends"
		private_gitmarks_dir = os.path.join( settings.GITMARK_BASE_DIR, settings.PRIVATE_GITMARK_REPO_DIR)
		private_friends_file = os.path.join(private_gitmarks_dir, FRIENDS_JSON)
		
		fh = open(private_friends_file)
		if fh:
			jsonObj = fh.read()
			fh.close()
			del fh
			fr = json.loads(jsonObj)
			self.privateFriends.update(fr)
		else:
			print "ERROR: can't load friends"
		return 

	def load_public_friends(self):
		print "load public friends"
		public_gitmarks_dir = os.path.join( settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR)
		public_friends_file = os.path.join(public_gitmarks_dir, FRIENDS_JSON)
		
		fh = open(public_friends_file)
		if fh:
			jsonObj = fh.read()
			fh.close()
			del fh
			fr = json.loads(jsonObj)
			self.publicFriends.update(fr)
		else:
			print "ERROR: can't load friends"
		return 

	def print_friends(self):
		""" Debugging tool to print friend list. """
		print "== public friends =="
		print self.publicFriends
		print "== private friends =="
		print self.privateFriends

	def load_friends(self):
		self.load_private_friends()
		self.load_public_friends()


class friend_sender_receiver(object):
	""" Class for managing to send/receive message from friends. 
	Mostly this is for notifications of new updates from friends (or for friends)
	so that their gitmarks can fetch bookmarks from your repo.
	"""

if __name__ == "__main__":
	print "goddammed! Do some friend stuff here"
	print "THIS BETA CODE USING FILE NOT CREATED BY CONFIG"
	
	# -- load 'friend' file
	scraper = friend_scraper()
	scraper.load_friends()
		
	scraper.print_friends()
	# -- sort those friends by service
	
	#for each friend per service
		# check the service for new updates
		# pull or sync all the bookmarks you can 
		# log a datetime or info to indicate the last check
	

	