"""
File contains the gitmarks object clas.
"""

import sys, os
import urllib, httplib
import re
import csv
import subprocess
import time
from optparse import OptionParser
import json
import hashlib
# -- Our own gitmarks settings
import settings

#our version of gitmarks
GITMARK_VER_STRING = 'gitmark.0.2'

# Arguments are passed directly to git, not through the shell, to avoid the
# need for shell escaping. On Windows, however, commands need to go through the
# shell for git to be found on the PATH, but escaping is automatic there. So
# send git commands through the shell on Windows, and directly everywhere else.
USE_SHELL = os.name == 'nt'


class gitmark(object):
	
	# -- GitMarks members
	# If you add member variables you don't want in a gitmark, delete them in JOSNBlock below
	# Otherwise self.__dict__ works rong.
	uri = None #string
	hash = None #hash value 
	summary = None #string
	description = None #string 
	tags = [] #list of strings of tags
	time = None #ISO8601 absolute date time
	creator = None
	rights = None #creative commons rights string
	tri = [] #transitionary resource locator. IRL bit.ly, goo.gl, etc
	content = ''  #content of the site. Lazyloads and should do smart local/away fetch
	title = None
	extended = None
	meta = None
	private = None
	ver = GITMARK_VER_STRING

	def __init__(self,uri, creator=None, dictValues=None):
		# -- temp. Force build deafults before overriding
		self.uri = uri
		self.hash = self.generateHash(uri)
		self.time = time.strftime("%Y-%m-%dT%H:%M:%SZ")
		self.creator  = creator
		self.rights = 'CC BY'
		self.private = True	 #default to private for safety
		
		if dictValues:
			#DANGER: this is a security danger
			self.__dict__
		#TODO: Do I want to return self?
		
		
	def addTags(self, stringList):
		#if we have more than 1 quote, split by quotes
		if(stringList.count('"') > 1):
			print 'has qouted string! We fail'
		else :
			list = stringList.split(',')
			list = [ l.lstrip().rstrip() for l in list]
			#TODO: do some smart string hacking, for different strings
			# of data formatting
			self.tags.extend(list)
					
	def noContentSet(self):
		"""
		returns true of this gitmark is set to 'get no content'
		"""
		#TODO menoize this result, and kill the menoize if we get
		# a change to the tag. Maybe menoize to a hash of the list,
		# and if the hash changes, re-calculate?
		if 'no content' in self.tags:
			return True
		elif 'no_content' in self.tags:
			return True
		return False
	
	def __str__(self):
		return '<gitmark obj for "%s" by "%s"\n>' %(self.uri, self.creator)
	
	def setPrivacy(self, privacy):
		""" Set this gitmark to be private """
		self.private = privacy
		
	def generateHash(self, uri = None):
		"""generates a hash for our URI (or the passed
		URI if it is not null"""
		if(uri == None): 
			uri = self.uri
		m = hashlib.md5()
		m.update(uri)
		return m.hexdigest()

	def parseTitle(self, content=None):
		""" parses the tile from html content, sets it to 
		our local title value, and returns the title to the caller"""
		if(content == None):
			content = self.content
		self.title = self.cls_parseTitle(content)
		return self.title
		
	def getContent(self, uri=None):
		"""
		Get content from the web, and store it to our local 
		content structure. IF we have a uri, gets contents from 
		there instead of our local uri.
		"""
		if( uri == None):
			uri = self.uri
		#FUTURE: do we want to allow a different URI to get passed in?			
		self.content = self.cls_getContent(uri)
		 
	def uncacheContent(self, target_file):
		"""
		Reads content from our local cache	if we have it, 
		otherwise it will fetch that content from the web (not 
		store it) and save it to the local gitmark.
		"""		
		if os.path.isfile(target_file) :	
			fh = open(target_file,"r")
			self.content = fh.read()
			del fh
		else:
			print >>sys.stderr, ("Warning: no local content for this gitmark."
				"tryig to read from web")					
			self.getContent() 

	def setTimeIfEmpty(self):
		if self.time == None :
			self.time = time.strftime("%Y-%m-%dT%H:%M:%SZ")

	def cacheContent(self, target_file, content=None):
		""" 
		Write this gitmarks content to the target file. If this
		content is specified, then that content is written instead
		of the content in this gitmark
		"""
		# -- lazily git store any existing file if necessary
		if os.path.isfile(target_file) :
			#check the md5 sum of the contet of this file, 
			#if it does NOT match our new content, then 
			print "do magic here to md5 sum, and cache file if needed"
		if content == None:
			content = self.content 
		self.cls_saveContent(target_file, content)
			
	def addMyselfLocally(self, localGitmarkDir, localTagsDir):
		"""
		This method causes a gitmark to
		add itself to the local repository.
		""" 
		print "not used. old code. Use for reference only"
		exit(-5)
		
		print "adding myself to the local repository"
		if(self.private != False):
			print "this is a private mark. Encrypting not yet enabled. Do not store"
		else :
			# -- write gitmark
			fname = os.path.join(localGitmarkDir,self.hash)
			#fp = open(fname,"w")
			print 'debug fwrite of file "%s"' % fp
			print '---'
			print self.JSONBlock()
			print '---'
			#fwrite(self.JOSNBlock())
			#fclose(fp)
			# add git add here
			
			# -- write tags
			fname = os.path.join(localGitmarkDir,self.hash)
			fp = open(fname,"w")
			prettyTags = self.prettyTags() 
			uglyTags = self.uglyTags()
			tags = set(uglyTags.append(prettyTags))			
			for tag in tags:
				fname = os.path.join(localGitmarkDir,self.hash)
				print 'tag filename "%s" ' %fname	
				# add git add here
			settings.TAG_SUB_PATH
						

			
	def JOSNBlock(self):	
		"""creates and retuns a JSON text block of 
		current members of this gitMark. """
		d = self.__dict__
		if 'content' in d.keys() :
			del d['content'] #remove content, we don't want that
		return json.dumps(d,indent=4)
	
	def miniJSONBlock(self):
		""" creates and returns a minimun json block, used for tag files """
		d = {'hash':self.hash, 'title':self.title, 'uri':self.uri,
			'creator':self.creator,	 'ver':self.ver }
		return json.dumps(d,indent=4)
			
		
	def prettyTags(self):
		""" tags, cleaned from delicious and make nicer looking"""
		g = []
		for t in self.tags:
			print t
			if '_' in t:
				g.append(t.replace('_',' '))
			else:
				g.append(t)
			print g
		return g
			
	def uglyTags(self):
		""" tags as gotten raw, un-prettied for search and use"""
		return self.tags
		
		
	def everyPossibleTagList(self):
		allTags = self.prettyTags()
		allTags.extend(self.uglyTags())
		allTags = set(allTags)
		return allTags

	@classmethod	
	def cls_hydrate(cls, filename):
		""" 
		Create a gitmark object from files on the local filesystem. 
		"""
		f = open(filename,'r')
		if(f):
			jsonObj = f.read()
			f.close()
			del f
			obj = json.loads(jsonObj)
			print obj
			mark = gitmark(settings.USER_NAME)
			print "INCOMPLETE FUNCTION cls_hydrate"
		else:
			print "failed to read/load %s" %filename
		return None
	
	@classmethod
	def cls_saveContent(cls, filename, content):
		"""
		"""
		f = open(filename, 'w')
		f.write(content)
		f.close()
		return filename
		
	@classmethod
	def cls_generateHash(cls, text):
		m = hashlib.md5()
		m.update(text)
		return m.hexdigest()
		
	@classmethod
	def cls_getContent(cls, url):
		try:
			h = urllib.urlopen(url)
			content = h.read()
			h.close()
			h = urllib.urlopen(url)
		except IOError, e:
			print >>sys.stderr, ("Error: could not retrieve the content of a"
			" URL. The bookmark will be saved, but its content won't be"
			" searchable. URL: <%s>. Error: %s" % (url, e))
			content = ''
		except httplib.InvalidURL, e: #case: a redirect is giving me www.idealist.org:, which causes a fail during port-number search due to trailing :
			print >>sys.stderr, ("Error: url or url redirect contained an"
			"invalid  URL. The bookmark will be saved, but its content"
			"won't be searchable. URL: <%s>. Error: %s" % (url, e))
			content=''
		return content
	
	@classmethod
	def cls_parseTitle(cls, content):
		re_htmltitle = re.compile(".*<title>(.*)</title>.*")
		t = re_htmltitle.search(content)
		try:
			title = t.group(1)
		except AttributeError:
			title = '[No Title]'
		return title
		
	@classmethod
	def gitAdd(cls, files, forceDateTime=None, gitBaseDir=None):
		""" add this git object's files to the local repository"""
		# TRICKY:Set the authoring date of the commit based on the imported timestamp. git reads the GIT_AUTHOR_DATE environment var.
		# TRICKTY: sets the environment over to the base directory of the gitmarks base
		cwd_dir = os.path.abspath(os.getcwd())
	
		if gitBaseDir: os.chdir(os.path.abspath(gitBaseDir))
		if forceDateTime :	os.environ['GIT_AUTHOR_DATE'] = forceDateTime
		subprocess.call(['git', 'add'] + files, shell=USE_SHELL)
		if forceDateTime : del os.environ['GIT_AUTHOR_DATE']
		if gitBaseDir: 	os.chdir(cwd_dir)

	@classmethod
	def gitCommit(cls, msg, gitBaseDir = None):
		""" commit the local repository to the server"""
		# TRICKTY: sets the environment over to the base directory of the gitmarks base
		cwd_dir = os.path.abspath(os.getcwd())
		if gitBaseDir: os.chdir(os.path.abspath(gitBaseDir))
		subprocess.call(['git', 'commit', '-m', msg], shell=USE_SHELL)
		if gitBaseDir: 	os.chdir(cwd_dir)

	@classmethod
	def gitPush(cls, gitBaseDir = None):
		""" push the local origin to the master"""
		# TRICKTY: sets the environment over to the base directory of the gitmarks base
		cwd_dir = os.path.abspath(os.getcwd())
		if gitBaseDir: os.chdir(os.path.abspath(gitBaseDir))
		print os.getcwd()
		pipe = subprocess.Popen("git push origin master", shell=True) #Tricky: shell must be true
		pipe.wait()
		if gitBaseDir: 	os.chdir(cwd_dir)
	 
		 
#	 @classmethod
#	 def saveTagData(cls, tag, url, title, base_filename):
#		 tag_filename = os.path.join(TAG_PATH, tag)
#		 tag_writer = csv.writer(open(tag_filename, 'a'))
#		 tag_writer.writerow([url, title, base_filename])
#		 return tag_filename
#
#	 @classmethod
#	 def parseTitle(cls, content):
#		 re_htmltitle = re.compile(".*<title>(.*)</title>.*")
#		 t = re_htmltitle.search(content)
#		 try:
#			 title = t.group(1)
#		 except AttributeError:
#			 title = '[No Title]'
#		 
#		 return title
# 
#	 @classmethod
#	 def getContent(cls, url):
#		 try:
#			 h = urllib.urlopen(url)
#			 content = h.read()
#			 h.close()
#			 h = urllib.urlopen(url)
#		 except IOError, e:
#			 print >>sys.stderr, ("Error: could not retrieve the content of a"
#				 " URL. The bookmark will be saved, but its content won't be"
#				 " searchable. URL: <%s>. Error: %s" % (url, e))
#			 content = ''
#		 except httplib.InvalidURL, e: #case: a redirect is giving me www.idealist.org:, which causes a fail during port-number search due to trailing :
#			 print >>sys.stderr, ("Error: url or url redirect contained an"
#			 "invalid  URL. The bookmark will be saved, but its content"
#			 "won't be searchable. URL: <%s>. Error: %s" % (url, e))
#			 content=''
#		 return content


class gitmarkRepoManager(object):

	def __init__(self):
		print "initalizing a repo manager"
		
	