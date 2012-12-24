#!/usr/bin/env python
# encoding: utf-8
"""
gitmark_add.py

Functions and classes to add data to a local gitmarks directory. 

Based on gitmarks by Hilary Mason on 2010-09-24.
Copyright 2010 by Far McKon (intermediate while picking a opensource license)
"""

import sys, os
import urllib, httplib
import re
import csv
import subprocess
import time
from optparse import OptionParser
import json
import logging
# -- Our own gitmarks settings
import settings
from gitmark import gitMark
from gitmark import USE_SHELL


def canHazWebs(): 
	""" Returns true/false if I can't ping google,
	which is used as a 'can I reach the internet?' test """
	try:
		h = urllib.urlopen("http://google.com")
		#todo switch this to a smarter ping system, and use other than google.
		data = h.read()
		h.close()
		return True
	except	:
		logging.error("fail to get google url")
	return False

def process_gitmarks_cmd(opts, args):
	""" processes a gitmarks command opts is list of options. 
	args is 1 or more URL's to process. """

	# -- each arg is a URL. 	
	for arg in args:
		g = gitmark(arg,settings.USER_NAME)
		if 'tags' in opts.keys():			g.addTags(opts['tags'])
		if 'private' in opts.keys():		g.setPrivacy(opts['private'])

		# -- get content, and autogen title 
		if canHazWebs():
			g.getContent()
			g.parseTitle()
		else:
			logging.error("no netz! overriding push to false!")
			opts['push'] = False
		
		doPush = opts['push'] if 'push' in opts.keys() else 'False'  	
		updateRepoWith(g, doPush)
		
def updateRepoWith(gitmarksObj, doPush = True):
	""" Update a repository with the passed gitmarksObject. This can also be flagged
	to push that update to the remote repository."""
	# -- see if we need to add or update the mark
	if not isInGitmarkPublicRepo(gitmarksObj):		
		return addToRepo(gitmarksObj, doPush)
	else:
		logging.warning("This bookmark is already in our repo. update?")
		#TODO: write/run/do system to update gitmark
		return updateExistingInRepo(gitmarksObj, doPush)
	return -1; 
		
def updateExistingInRepo(gitmarksObj, doPush = True):
	""" Updates an existing gitmark file(s) on disk. """
	if(gitmarksObj.private != True):
		updateToPublicRepo(gitmarksObj, doPush)
	updateToPrivateRepo(gitmarksObj, doPush)

def updateToPublicRepo(gitmarksObj, doPush):
	""" Updates an existing gitmark file(s) in a public repo. """
	#TODO: set this a pep8 private function name
	logging.info("HACK: Do we want to push/pull before/after doing this operation?"	)
	# -- TODO: decide if we want to pull before doing this operation,
	# and/or push after doing this operation
	
	filename = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR, 
		settings.BOOKMARK_SUB_PATH, gitmarksObj.hash)

	# -- Check for tags differences
	oldMark = gitmark.cls_hydrate(filename)
		# -- TODO add new tags
		# -- TODO remove old tags
	# -- TODO check for description differences
	# -- TODO check for content md5 differences
		# -- TODO update local content if turned on, and content is different
	exit(-3)

def updateToPrivateRepo(gitmarksObj, doPush):
	#TODO: set this a pep8 private function name
	logging.warning("no such thing to update private repo, encryption not yet installed")
	exit(-5)

	
	
def addToRepo(gitmarksObj, doPush = True):		
	""" addToRepo function that does all of the heavy lifting"""
	if(gitmarksObj.private != True):
		return addToPublicRepo(gitmarksObj, doPush)
	logging.info("adding mark %s to private repo" %str(gitmarksObj))
	return  addToPrivateRepo(gitmarksObj, doPush)

		
def addToPrivateRepo(gitmarksObj, doPush = True):
	#TODO: set this a pep8 private function name
	""" add to the public repository """
	if gitmarksObj.private != True:
		logging.error("this is a public mark. Use 'addToPublicRepo for this")
		return -1
	# -- add to our public 'bookmarks'
	filename = os.path.join(settings.GITMARK_BASE_DIR, settings.PRIVATE_GITMARK_REPO_DIR, 
		settings.BOOKMARK_SUB_PATH, gitmarksObj.hash)
	filename = os.path.normpath(filename)
	filename = os.path.abspath(filename)
	# -get our string
	gitmarksObj.setTimeIfEmpty()
	bm_string = gitmarksObj.JSONBlock() 
	gitmarksBaseDir = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR)


	fh = open(filename,'a')
	if(fh):
		# TRICKY:Set the authoring date of the commit based on the imported
		# timestamp. git reads the GIT_AUTHOR_DATE environment var.
		os.environ['GIT_AUTHOR_DATE'] = gitmarksObj.time
		logging.info(bm_string)
		fh.write(bm_string)
		fh.close()
		del fh
		gitmark.gitAdd([filename,],gitmarksObj.time,gitmarksBaseDir)

	# -- add to each of our our public 'tags' listings
	tag_info_string = gitmarksObj.miniJSONBlock()

	tagFilesWrittenSuccess = []
	for tag in gitmarksObj.everyPossibleTagList():
		filename = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR, 
		settings.TAG_SUB_PATH, tag)
		filename = os.path.normpath(filename)
		filename = os.path.abspath(filename)
		logging.info('tags filename' + str(filename))
		fh = open(filename,'a')
		if(fh):
			fh.write(tag_info_string)
			fh.close()
			tagFilesWrittenSuccess.append(filename)
			del fh
	gitmark.gitAdd(tagFilesWrittenSuccess,gitmarksObj.time, gitmarksBaseDir)


	# -- if we should get content, go get it and store it locally
	if settings.GET_CONTENT and gitmarksObj.noContentSet() == False:
		logging.info("get content? Don't mind of I do...")
		filename = os.path.join(settings.GITMARK_BASE_DIR, settings.CONTENT_GITMARK_DIR, 
		settings.HTML_SUB_PATH, gitmarksObj.hash)
		#check if we have a cache directory
		c_dir  = os.path.join(settings.GITMARK_BASE_DIR, settings.CONTENT_GITMARK_DIR, 
		settings.HTML_SUB_PATH)
		if os.path.isdir(c_dir) == False:
			subprocess.call(['mkdir','-p',c_dir],shell=USE_SHELL)
		gitmarksObj.cacheContent(filename)
		
	#TOOD: do something about committing our changes
	logging.info("git commit (local)? Don't mind if i do....")
	msg = "auto commit from delicious import beta test %s" %time.strftime("%Y-%m-%dT%H:%M:%SZ")
	gitmark.gitCommit(msg, gitmarksBaseDir )

	if doPush:
		logging.info("git push (external)? Don't mind if i do....")
		gitmark.gitPush(gitmarksBaseDir )
	
			
def addToPublicRepo(gitmarksObj, doPush = True):
	#TODO: set this a pep8 private function name
	""" Adds a gitmark to the local public repository """

	if(gitmarksObj.private != False):
		logging.info("this is a private mark. Use 'addToPrivateRepo for this")
		return -1

	# -- add to our public 'bookmarks'
	filename = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR, 
		settings.BOOKMARK_SUB_PATH, gitmarksObj.hash)
	filename = os.path.normpath(filename)
	filename = os.path.abspath(filename)
	# -get our string
	gitmarksObj.setTimeIfEmpty()
	bm_string = gitmarksObj.JSONBlock() 
	gitmarksBaseDir = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR)


	fh = open(filename,'a')
	if(fh):
		# TRICKY:Set the authoring date of the commit based on the imported
		# timestamp. git reads the GIT_AUTHOR_DATE environment var.
		os.environ['GIT_AUTHOR_DATE'] = gitmarksObj.time
		logging.info(bm_string)
		fh.write(bm_string)
		fh.close()
		del fh
		gitmark.gitAdd([filename,],gitmarksObj.time,gitmarksBaseDir)

	# -- add to each of our our public 'tags' listings
	tag_info_string = gitmarksObj.miniJSONBlock()

	tagFilesWrittenSuccess = []
	for tag in gitmarksObj.everyPossibleTagList():
		filename = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR, 
		settings.TAG_SUB_PATH, tag)
		filename = os.path.normpath(filename)
		filename = os.path.abspath(filename)
		logging.info('tags filename' + str(filename))
		fh = open(filename,'a')
		if(fh):
			fh.write(tag_info_string)
			fh.close()
			tagFilesWrittenSuccess.append(filename)
			del fh
	gitmark.gitAdd(tagFilesWrittenSuccess,gitmarksObj.time, gitmarksBaseDir)


	# -- if we should get content, go get it and store it locally
	if settings.GET_CONTENT and gitmarksObj.noContentSet() == False:
		logging.info("get content? Don't mind of I do...")

		filename = os.path.join(settings.GITMARK_BASE_DIR, settings.CONTENT_GITMARK_DIR, 
		settings.HTML_SUB_PATH, gitmarksObj.hash)
		#check if we have a cache directory
		c_dir  = os.path.join(settings.GITMARK_BASE_DIR, settings.CONTENT_GITMARK_DIR, 
		settings.HTML_SUB_PATH)
		if os.path.isdir(c_dir) == False:
			subprocess.call(['mkdir','-p',c_dir],shell=USE_SHELL)
		gitmarksObj.cacheContent(filename)
		
	#TOOD: do something about committing our changes
	logging.info("git commit (local)? Don't mind if i do....")
	msg = "auto commit from delicious import beta test %s" %time.strftime("%Y-%m-%dT%H:%M:%SZ")
	gitmark.gitCommit(msg, gitmarksBaseDir )

	if doPush:
		logging.info("git push (external)? Don't mind if i do....")
		gitmark.gitPush(gitmarksBaseDir )
		
	
def isInGitmarkPublicRepo(gitmarkObj):
	""" Checks if a gitmarks object is already in the public repository
	by checking for it's' hash in our public bookmarks directory. """
	if(gitmarkObj.hash == None):
		return False		
	filename = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR, 
	settings.BOOKMARK_SUB_PATH, gitmarkObj.hash)
	return os.path.isfile(filename) 


if __name__ == '__main__':
	""" Function to run if we are running at the commandline"""
	# -- parse command line options
	parser = OptionParser("usage: %prog [options] uri")

	parser.add_option("-s", "--share", dest="push", action="store_true", default=False, help="push data to remote gitmarks share point if possible")
	parser.add_option("-t", "--tags", dest="tags", action="store", default='notag', help="comma seperated list of tags")
	parser.add_option("-m", "--message", dest="msg", action="store", default=None, help="specify a commit message (default is 'adding [url]')")
	parser.add_option("-c", "--skipcontent", dest='content', action='store_false', default=True, help="do not try to fetch content to store locally for search")
	parser.add_option("-p", "--private", dest="private", action="store_true", default=False, help="Mark this as a private tag, not to share except with for:XXX recepiants")

	if len(sys.argv) <= 1:
		parser.print_usage()
		exit(0)

	(options, args) = parser.parse_args()
	opts = {'push': options.push, 'tags': options.tags, 'msg': options.msg, 'content':options.content, 'private':options.private}
		
	g = process_gitmarks_cmd(opts, args)
