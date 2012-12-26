#!/usr/bin/env python
# encoding: utf-8
"""
delicious_import.py

Created by Hilary Mason on 2010-11-28.
Copyright (c) 2010 Hilary Mason. All rights reserved.
"""

import sys
import urllib
import logging
from xml.dom import minidom
from xml.parsers import expat

from gitmark import gitMark
from gitmark_add import addToRepo, addToPublicRepo

def cache_to_local_file(local_file, content):
	"""Save content in local file"""
	h = open(local_file, 'w')
	h.write(content)
	h.close()


def import_delicious_to_local_git(username, password='', url=None, doCache=True):
	""" imports a delicious file to the local git system. If url is not set
	a delicious API url is generated. if url is set (for a file, for example) 
	that file is imported."""
	if not url:
		# API URL: https://user:passwd@api.del.icio.us/v1/posts/all
		url = "https://%s:%s@api.del.icio.us/v1/posts/all" % (username, password)
		#re: = urllib2.Request(url, headers={'Accept':'application/xml'})
		h = urllib.urlopen(url)
	else:
		# Url is actually a local file in this case
		url = urllub.pathname2url(url)	
		h = open(url)
	content = h.read()	
	h.close()

	#--enable to cache a copy of the file to test using
	#cache_to_local_file('delicious_cache.htm', content):

	# check for signs of a yahoo error page, with causes minidom to flip out
	if( len(content) >=6 and content[:5] == '<!-- ' ):
		logging.error(content)
		logging.error("yahoo error, no data fetched")
		return
	
	try:
		x = minidom.parseString(content)
	except expat.ExpatError, e:
		saveFile = "minidom_freakout.xml"
		fh = open(saveFile, "w")
		logging.error("== Above content caused minidom to flipped out\n %s" % (e))
		logging.error("Saving problematic file as %s" % (saveFile))
		if(fh):
			fh.write(content)
			fh.close()
			logging.error("Saved problematic file as %s" % (saveFile))
		return -1
	# sample post: <post href="http://www.pixelbeat.org/cmdline.html" hash="e3ac1d1e4403d077ee7e65f62a55c406" description="Linux Commands - A practical reference" tag="linux tutorial reference" time="2010-11-29T01:07:35Z" extended="" meta="c79362665abb0303d577b6b9aa341599" />

	post_list = x.getElementsByTagName('post')
	
	newMarksList = []
	
	if doCache:
		logging.warning("Caching data. This may be slow")
	
	for post_index, post in enumerate(post_list):
		try:
			url = post.getAttribute('href')
			desc = post.getAttribute('description')
			timestamp = post.getAttribute('time')
			raw_tags  = post.getAttribute('tag')
			extended =	post.getAttribute('extended')
			meta	 =	post.getAttribute('meta')
			# turn a comma separated list of tags into a real list of tags
			tags = [tag.lstrip().rstrip() for tag in raw_tags.split()]
			privateString = post.getAttribute('private')
			
			g = gitMark(url, 'delicious:'+ str(username))
			g.description = desc 
			g.tags = tags
			g.time = timestamp
			g.rights = None 
			g.meta = meta
			g.extended = extended
			
			if(privateString == "0" or privateString==""):
				g.private = False
			g.parseTitle() 
			newMarksList.append(g)
			#break here for single test without data resetting/fixing

		except (KeyboardInterrupt, SystemExit):
			print >>sys.stderr, ("backup interrupted by KeyboardInterrupt/SystemExit" )
			logging.error( ("backup interrupted by KeyboardInterrupt/SystemExit" ) )
			return 
		except Exception as e:
			print >> sys.stderr, ("unknown exception %s" %(e))
			logging.error(("unknown exception %s" %(e)))

	logging.info("all kinds of new gitmarks!!")
	logging.info("we have %d new marks" % len(newMarksList))
	
	for mark in newMarksList:
		# FUTURE: speeed this up, by passing a whole list
		if mark.title is None: mark.title = "Untitiled bookmark"
		logging.info("adding mark %s to repo %s" %(str(mark.title), str(mark.private) ))
		if doCache:
			mark.getContent()
			print '.'
		err = addToRepo(mark,doPush=False)
		if (err > 0):
				logging.info("mark add error %s" %str(err) )
	return 0

# -- hack test main for when yahoo sucks and I need to test
if __name__ == '__offfline_main__':
	x = {"extended": "",
		"hash": "082d479d946d5e9ebd891509446d9cbc",
		"description": "SSH and SCP: Howto, tips & tricks \u00ab Linux Tutorial Blog",
		"rights": None,
		"creator": "delicious:farmckon",
		"uri": "http://www.linuxtutorialblog.com/post/ssh-and-scp-howto-tips-tricks",
		"private": False,
		"meta": "09f8b3205ee44cac3a94305db4337a7b",
		"time": "2011-02-05T21:16:48Z",
		"tags": ["ssh", "scp", "linux_tutorial","howto"]}

	g = gitMark(x['uri'], x['creator'])
	g.description = x['description']
	g.tags = x['tags']
	g.time = x['time']
	g.rights = None
	g.meta = x["meta"]
	g.extended = x['extended']
	g.private = x['private']
	addToPublicRepo(g)


if __name__ == '__main__':
	usage = """
		Usage: python delicious_import.py cached-page-uri
		OR
		Usage: python delicious_import.py username password 
		***Password and username are sent as HTTPS***"
		"""

	if (len(sys.argv) == 2):
		import getpass
		import socket

		username = getpass.getuser()
		host = socket.gethostname()
		username = '%s@%s' % (str(username), str(host))
		import_delicious_to_local_git(username, password=None, url=sys.argv[1])
	elif (len(sys.argv) == 3):
		try:
			(username, password) = sys.argv[1:]
		except ValueError as e:
			print e
			logging.error(e)
		import_delicious_to_local_git(username, password)
	else:
		print usage
