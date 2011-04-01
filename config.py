#!/usr/bin/env python
# encoding: utf-8
"""
Configuration script for gitmarks.py
"""

import example_settings
import os
import subprocess
import shutil

# Arguments are passed directly to git, not through the shell, to avoid the
# need for shell escaping. On Windows, however, commands need to go through the
# shell for git to be found on the PATH, but escaping is automatic there. So
# send git commands through the shell on Windows, and directly everywhere else.
USE_SHELL = os.name == 'nt'

def configure_gitmarks():
	# -- pull needed libraries from the net
	download_needed_software()
	
	# -- generate our configuration settings
	dict = config_settings_from_user()

	cont = getYesNoFromUser("Store Settings, Setup up local stuff from above settings??",True)
	if not cont:
		print" Note: In beta, you must store setting. Can't continue without them"
		print "sorry. Beta and all, you know how it is. Share and Enjoy"
		return 0
	
	# -- store updated settings to settings.py, and reload
	success = create_or_update_settings(dict,'settings.py', 'example_settings.py')
	if success:
		# -- well, we got this far. Lets make some folders
		ret = create_local_gitmarks_folders()
		if ret:
			print "We think we just setup your local system. God knows, we may have succeeded!"
		else:
			print "Problem creating local gitmarks folders, error code: %d" % (ret)
	else:
		print "failed to store updated settings " + str(dict)
		print " sorry our beta sucks. We are working on it! "
		return -5
		


def download_needed_software():
	# wget http://python-gnupg.googlecode.com/files/python-gnupg-0.2.6.tar.gz
	# or get gpg or pgp instead?
	print "TODO: Download prerequsite software"
	pass
	
def create_local_gitmarks_folders():
	""" This function creates local repository folders. If we have a remote repo name, it will try to sync that data to this place.  If the settings remote repository info is "None" it will just create a local repo without a remote connection"""
	
	# Now we can load the settings we just created
	try:
		import settings
	except ImportError, e:
		print "Failed loading settings.py module"
		raise e

	abs_base_dir =  os.path.abspath(settings.GITMARK_BASE_DIR)

	# -- Create a base directory if we need to 
	if not os.path.isdir(abs_base_dir):
		print " creating base directory for gitmarks"
		os.makedirs(abs_base_dir)

	public_gitmarks_dir = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR)

	# -- if we have a remote public repo, try to git-clone to create a local copy.
	if(settings.REMOTE_PUBLIC_REPO != None):
		if not folder_is_git_repo(public_gitmarks_dir) :
			ret = clone_to_local(settings.GITMARK_BASE_DIR, public_gitmarks_dir, 	settings.REMOTE_PUBLIC_REPO)				
			if(ret != 0):
				print "remote public clone to local failed"
				return -9
	# -- no remote public repo, make a dir and git-init it as needed
	else: 	
		abs_public_gitmarks_dir = os.path.abspath(public_gitmarks_dir)
		# -- create a dir if we need to.
		if not os.path.isdir(abs_public_gitmarks_dir):	
			subprocess.call(['mkdir', abs_public_gitmarks_dir], shell=USE_SHELL)
		# -- init the new git repo in that dir
		cwd_dir = os.path.abspath(os.getcwd())
		os.chdir(os.path.abspath(abs_public_gitmarks_dir))
		ret =  subprocess.call(['git', 'init', '.', ], shell=USE_SHELL)
		os.chdir(cwd_dir)
		# -- create our sub-dirs if needed
		make_gitmark_subdirs(abs_public_gitmarks_dir, [settings.BOOKMARK_SUB_PATH, 	settings.TAG_SUB_PATH, settings.MSG_SUB_PATH])


	private_gitmarks_dir = os.path.join(settings.GITMARK_BASE_DIR, settings.PRIVATE_GITMARK_REPO_DIR)


	# -- if we have a remote private repo, try to git-clone to create a local copy.
	if(settings.REMOTE_PRIVATE_REPO != None):
		if not folder_is_git_repo(private_gitmarks_dir) :
			ret = clone_to_local(settings.GITMARK_BASE_DIR, private_gitmarks_dir, 	settings.REMOTE_PRIVATE_REPO)				
			if(ret != 0):
				print "remote public clone to local failed"
				return -9
	# -- no remote private repo, make a dir and git-init it as needed
	else: 	
		abs_private_gitmarks_dir = os.path.abspath(private_gitmarks_dir)
		# -- create a dir if we need to.
		if not os.path.isdir(abs_private_gitmarks_dir):	
			subprocess.call(['mkdir', abs_private_gitmarks_dir], shell=USE_SHELL)
		# -- init the new git repo in that dir
		cwd_dir = os.path.abspath(os.getcwd())
		os.chdir(os.path.abspath(abs_private_gitmarks_dir))
		ret =  subprocess.call(['git', 'init', '.', ], shell=USE_SHELL)
		os.chdir(cwd_dir)
		# -- create our sub-dirs if needed
		make_gitmark_subdirs(abs_private_gitmarks_dir, [settings.BOOKMARK_SUB_PATH, 	settings.TAG_SUB_PATH, settings.MSG_SUB_PATH])

	# -- Create our local content directory and repo, even if we never use it
	content_dir =  os.path.join(settings.GITMARK_BASE_DIR, settings.CONTENT_GITMARK_DIR)
	if not os.path.isdir(content_dir):
		subprocess.call(['mkdir',content_dir],shell=USE_SHELL)
	else :
			print 'content dir already exists at "' + str(content_dir) +'"'
	cwd_dir = os.path.abspath(os.getcwd())
	os.chdir(os.path.abspath(content_dir))
	ret =  subprocess.call(['git', 'init', '.', ], shell=USE_SHELL)
	os.chdir(cwd_dir)

	return 0
	

	
def clone_to_local(baseDir, folderName, remoteGitRepo):
	"""Clones a repository at remoteGitRepo to a local directory"""
	print "cloning repository %s to directory %s" %(remoteGitRepo, folderName)

	#swizzle our process location so that we get added to the right repo
	baseDir = os.path.abspath(baseDir)
	cwd_dir = os.path.abspath(os.getcwd())
	os.chdir(os.path.abspath(baseDir))
	ret =  subprocess.call(['git', 'clone', remoteGitRepo, folderName], shell=USE_SHELL)
	os.chdir(cwd_dir)
	return ret
	
def make_gitmark_subdirs(folderName, subdirsList):
	""" makes a stack of gitmarks subdirectories at the folder listed """
	for newDir in subdirsList:
		newDir =  os.path.join(folderName, newDir)
		newDir = os.path.abspath(newDir)
		subprocess.call(['mkdir', newDir], shell=USE_SHELL)
		#TODO: appears git does not add empty dirs. If it did, we would add that here
	return
	

def folder_is_git_repo(folderName):
	git_folder = os.path.join(folderName, '/.git/')
	return os.path.isdir(git_folder)

def config_settings_from_user():
	"""returns a dict of config settings set interactivly by the user. 
		returns none on error """
	print """
	Wecome to gitmarks configurator. This will setup a couple of local
	repositories for you to use as yor gitmarks system.	 Gitmarks will
	maintain 2-3 repositories.
	 - 1 for public use (world+dog read)
	 - 1 for friends use (with some encryption)
	 - 1 (optional) for content. This can be non-repo, or nonexistant 
	 
	 """
	ret = getYesNoFromUser("Ready to start?",True)
	if ret is None:
		print "invalid choice"
		return None
	elif ret is False:
		print "Goodbye! Share and Enjoy."
		return None

	base_dir = getStringFromUser('At what base directories do you want your repos (relative to current directory)?', example_settings.GITMARK_BASE_DIR)
	
	get_content= getYesNoFromUser('do you want to pull down the content of a page when you download a bookmark?', example_settings.GET_CONTENT)
	
	content_cache_mb = getIntFromUser('do you want to set a maximum MB of content cache?', example_settings.CONTENT_CACHE_SIZE_MB)
	
	remote_pub_repo = getStringFromUser('Specify a remote git repository for your public bookmarks',example_settings.REMOTE_PUBLIC_REPO)

	remote_private_repo = getStringFromUser('Specify a remote git repository for your private bookmarks?',example_settings.REMOTE_PRIVATE_REPO)
	
	remote_content_repo = None
	content_as_reop= getYesNoFromUser('do you want your content folder to be stored as a repository?',example_settings.CONTENT_AS_REPO)
	
	if content_as_reop is True:
		remote_content_repo = getStringFromUser('what is the git repository for your content?', example_settings.REMOTE_CONTENT_REPO)

	print "-- Pointless Info --"
	fav_color= getStringFromUser('what is your favorite color?',example_settings.FAVORITE_COLOR)
	wv_u_swallow = getStringFromUser('what is the windspeed velocity of an unladen swallow?',example_settings.UNLADEN_SWALLOW_GUESS)

	print "-- User Info --"
	user_name = getStringFromUser("what username do you want to use?", example_settings.USER_NAME)
	user_email = getStringFromUser("what email do you want to use?", example_settings.USER_EMAIL)
	machine_name = getStringFromUser("what is the name of this computer?", example_settings.MACHINE_NAME)




	dict = { 'GITMARK_BASE_DIR':base_dir, 'GET_CONTENT':get_content,
	'CONTENT_CACHE_SIZE_MB':content_cache_mb,
	'CONTENT_AS_REPO':content_as_reop,
	'REMOTE_PUBLIC_REPO':remote_pub_repo, 'REMOTE_PRIVATE_REPO': remote_private_repo,
	'SAVE_CONTENT_TO_REPO':content_as_reop, 'REMOTE_CONTENT_REPO':remote_content_repo,
	'FAVORITE_COLOR':fav_color, 'UNLADEN_SWALLOW_GUESS':wv_u_swallow,
	"PUBLIC_GITMARK_REPO_DIR":example_settings.PUBLIC_GITMARK_REPO_DIR,
	'PRIVATE_GITMARK_REPO_DIR':example_settings.PRIVATE_GITMARK_REPO_DIR,
	'CONTENT_GITMARK_DIR':example_settings.CONTENT_GITMARK_DIR,
	'BOOKMARK_SUB_PATH':example_settings.BOOKMARK_SUB_PATH,
	'TAG_SUB_PATH':example_settings.TAG_SUB_PATH, 'MSG_SUB_PATH':example_settings.MSG_SUB_PATH,
	'HTML_SUB_PATH':example_settings.HTML_SUB_PATH,
	'USER_NAME':user_name,
	'USER_EMAIL':user_email,
	'MACHINE_NAME':machine_name
	}
	return dict
		
	
def create_or_update_settings(dict,settings_filename, opt_example_file=None):	
	""" 
	Does some magic to read a settings file, and replace the values in-line,
	and then write the new values back to the settings file.
	"""
	if not (os.path.isfile(settings_filename)):
		if not (opt_example_file):
			print "can't update a nonexistant file, no existing %s. Add an example file"
			exit(-10); #FAIL
		shutil.copy(opt_example_file, settings_filename)
	
	fh = open(settings_filename,'r')
	raw_settings = fh.readlines()
	fh.close()
	newlines = []
	for line in raw_settings:
		newline = line.rstrip()
		if '=' in line:
			comment = None
			val = None
			var = None
			print 'on line "' + newline + '"'
			if( line.split('#') < 1 ):
				comment = line.split('#')[-1]
				print '\thas comment ' + str(comment)				
			var = line.split('=')[0]
			val = ''.join(line.split('=')[1:])
			var = var.lstrip().rstrip()
			val = val.lstrip().rstrip()
			print '\tupdating var ' + str(var) +' old val ' +str(val) 
			if var in dict:
				if type(dict[var]) is str: 
					newline = var + " = '" + str(dict[var]) + "'"
				else:
					newline = var + " = " + str(dict[var])

				if comment:
					newline += ' # ' + comment
			print 'updated line "' + newline + '"'
		else:
			print 'no update on "' + newline + '"'
		newlines.append(newline)
	if len(newlines) == len(raw_settings):
		fh = open(settings_filename,'w')
		#debugging fh = open(settings_filename +".tmp",'w')
		fh.write('\n'.join(newlines))
		fh.close()
		return True
	else:
		print "settings size did not match! Abandon the ship!"
		return False
	return False
	

def getIntFromUser(message, value=''):
	""" Prompts a user for an input int. Uses the default value if no
		value is entered by the user. Uses default value of parse error happens 
	"""
	msg2 = ' '.join([message,' (',str(value),') (int): ']) 
	newValue = raw_input(msg2)
	if(newValue =="" or newValue == "\n"):
		return int(value)	

	try:
		return int(newValue)
	except:
		print "int decode fail for " +str(newValue) +" Using default value of" + str(value)
		return int(value)
	return None

def getStringFromUser(message,value=''):
	""" get a string value from the command line"""
	msg2 = ''.join([message,' (',str(value),') (string): ']) 
	value = raw_input(msg2)
	return value
	
def getYesNoFromUser(message,value=''):
	""" get a yes/no value from the command line"""
	msg2 = ''.join([message,' (',str(value),') (Y,n): ']) 
	newValue = raw_input(msg2)
	if(newValue =="" or newValue == "\n"):
		return value
	if(newValue == 'Y' or newValue == 'Yes' or newValue == 'y'):
		return True
	elif(newValue == 'n' or newValue == 'no' or newValue == 'N'):
		return False
	return None
	
if __name__ == '__main__':
	""" geneirc main statement"""
	configure_gitmarks()
