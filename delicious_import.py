#!/usr/bin/env python
# encoding: utf-8
"""
delicious_import.py

Created by Hilary Mason on 2010-11-28.
Copyright (c) 2010 Hilary Mason. All rights reserved.
"""

import sys, os
import urllib2
from xml.dom import minidom
from xml.parsers import expat
from optparse import OptionParser

from gitmark import *
from gitmark_add import *	

def cache_to_local_file(local_file, content):
	h = open(local_file, 'w')
	h.write(content)
	h.close()


def import_delicious_to_local_git(username, password='', url=None):
	""" imports a delicious file to the local git system. If url is not set
	a delicious API url is generated. if url is set (for a file, for example) that file is imported."""
	if not url:
			# API URL: https://user:passwd@api.del.icio.us/v1/posts/all
		url = "https://%s:%s@api.del.icio.us/v1/posts/all" % (username, password)
		#req = urllib2.Request(url, headers={'Accept':'application/xml'})
		h = urllib.urlopen(url)
	else:
		url = urllub.pathname2url(url)  #url is actually a local file in this case
		h = open(url)
	content = h.read()	
	h.close()
	#--enable to cache a copy of the file to test using
	#cache_to_local_file('delicious_cache.htm', content):

	# check for signs of a yahoo error page, with causes minidom to flip out
	if( len(content) >=6 and content[:5] == '<!-- ' ):
		print content
		print "yahoo error, no data fetched "
		return
	
	try:
		x = minidom.parseString(content)
	except expat.ExpatError, e:
		print content
		saveFile = "minidom_freakout.xml"
		fh = open(saveFile, "w")
		print "== Above content caused minidom to flipped out\n %s" % (e)
		print "Saving problematic file as %s" % (saveFile)
		if(fh):
			fh.write(content)
			fh.close()
			print "Saved problematic file as %s" % (saveFile)
			
		return
	
	# sample post: <post href="http://www.pixelbeat.org/cmdline.html" hash="e3ac1d1e4403d077ee7e65f62a55c406" description="Linux Commands - A practical reference" tag="linux tutorial reference" time="2010-11-29T01:07:35Z" extended="" meta="c79362665abb0303d577b6b9aa341599" />

	post_list = x.getElementsByTagName('post')
	
	newMarksList = []
	
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
			
			g = gitmark(url, 'delicious:'+ str(username))
			g.description = desc 
			g.tags = tags
			g.time = timestamp
			g.rights = None 
			g.meta = meta
			g.extended = extended
			
			if(privateString == "0" or privateString==""):
				g.private = False

			newMarksList.append(g)
			#break here for single test without data resetting/fixing

		except (KeyboardInterrupt, SystemExit):
			print >>sys.stderr, ("backup interrupted by KeyboardInterrupt/SystemExit" )
			return 
		except Exception as e:
			print >> sys.stderr, ("unknown exception %s" %(e))

	print "all kinds of new gitmarks!!"
	print "we have %d new marks" % len(newMarksList)
	
	for mark in newMarksList:
		# FUTURE: speeed this up, by passing a whole list
		print "adding mark %s to repo %s" %(str(mark.title), str(mark.private) )
		err = addToRepo(mark,doPush=False)
		print "mark add error %s" %str(err)	

# -- hack test main for when yahoo sucks and I need to test
if __name__ == '__offfline_main__':


	x = {    "extended": "", 
    "hash": "082d479d946d5e9ebd891509446d9cbc", 
    "description": "SSH and SCP: Howto, tips & tricks \u00ab Linux Tutorial Blog", 
    "rights": None, 
    "creator": "delicious:farmckon", 
    "uri": "http://www.linuxtutorialblog.com/post/ssh-and-scp-howto-tips-tricks", 
    "private": False, 
    "meta": "09f8b3205ee44cac3a94305db4337a7b", 
    "time": "2011-02-05T21:16:48Z", 
    "tags": [
        "ssh", 
        "scp", 
        "linux_tutorial", 
        "howto"
    ]
}

	g = gitmark(x['uri'], x['creator'])
	g.description = x['description'] 
	g.tags = x['tags']
	g.time = x['time']
	g.rights = None 
	g.meta = x["meta"]
	g.extended = x['extended']
	g.private = x['private']
	addToPublicRepo(g)

	
# -- real main. 

if __name__ == '__main__':
 
	usage =	 "Usage: python delicious_import.py cached-page-uri\nOR\nUsage: python delicious_import.py username password\n***Password and username are sent as HHTTPS***"

	if( len(sys.argv) == 2): 
		import getpass
		import socket
		username = getpass.getuser()
		host = socket.gethostname()
		username = '%s@%s' %(str(username), str(host))

		import_delicious_to_local_git(username, password=None, url=sys.argv[1])
	elif(len(sys.argv) == 3):
		try:
			(username, password) = sys.argv[1:]
		except ValueError:
			print usage
		import_delicious_to_local_git(username, password)
	else:
		print usage
 
