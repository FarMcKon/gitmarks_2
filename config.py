
import settings
import os
import subprocess


# Arguments are passed directly to git, not through the shell, to avoid the
# need for shell escaping. On Windows, however, commands need to go through the
# shell for git to be found on the PATH, but escaping is automatic there. So
# send git commands through the shell on Windows, and directly everywhere else.
USE_SHELL = os.name == 'nt'

def configure_gitmarks():

download_needed_software()
#	dict = config_settings_from_user()
#	
#	#debug printout
#	print "debugging printout of values:"
#	print dict	
#
#
#	cont = getYesNoFromUser("Store Settings, Setup up local stuff from above settings??",True)
#	if not cont:
#		print" ok. goodbye. Share and Enjoy"
#		return 0
#	
#	# -- store updated settings to settings.py, and reload
#	success = replace_value_in_file(dict,'settings.py')
#	if success :	
#		reload(settings) #TRICKY: we are reloading settings from a file we just wrote
#						#we do this, because we love danger!
#	else:
#		print "failed to store updated settings " + str(dict)
#		return -5

	create_local_gitmarks_folders()

def download_needed_software():
	# wget http://python-gnupg.googlecode.com/files/python-gnupg-0.2.6.tar.gz
	# or get gpg or pgp instead?
	
def create_local_gitmarks_folders():

	# -- Create our local 'private' repository`
	private_gitmark_dir = os.path.join(settings.GITMARK_BASE_DIR, settings.PRIVATE_GITMARK_REPO_DIR)
	if not folder_is_git_repo(private_gitmark_dir) :
		ret = clone_to_local(settings.GITMARK_BASE_DIR, private_gitmark_dir, settings.REMOTE_PRIVATE_REPO)		
		#print 'hack exit'
		#return
		
		if(ret != 0):
			print "clone to local failed"
			return -9
		make_gitmark_subdirs(private_gitmark_dir, [settings.BOOKMARK_SUB_PATH, 
		settings.TAG_SUB_PATH, settings.MSG_SUB_PATH])
	else :
		print "failsauce on creating private repo\ndir:\t%s\nrepo:\t%s" %  (private_gitmark_dir, settings.REMOTE_PRIVATE_REPO)

	# -- Create our local 'public' repository`
	public_gitmark_dir = os.path.join(settings.GITMARK_BASE_DIR, settings.PUBLIC_GITMARK_REPO_DIR)
	if not folder_is_git_repo(public_gitmark_dir) :
		ret = clone_to_local(settings.GITMARK_BASE_DIR, public_gitmark_dir, settings.REMOTE_PUBLIC_REPO)		
		if(ret != 0):
			print "clone to local failed"
			return -9
		make_gitmark_subdirs(public_gitmark_dir, [settings.BOOKMARK_SUB_PATH, 
		settings.TAG_SUB_PATH, settings.MSG_SUB_PATH])

	else :
		print "failsauce on creating public repo\ndir:\t%s\nrepo:\t%s" %  (public_gitmark_dir, settings.REMOTE_PUBLIC_REPO)

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

	

	
def clone_to_local(baseDir, folderName, remoteGitRepo):
	""" clones a repository at remoteGitRepo to a local directory """
	print "cloning repository %s to directory %s" %(remoteGitRepo, folderName)
	#swizzle our process locaiton so that we get added to the right repo
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

	base_dir = getStringFromUser('At what base directories do you want your repos?',
	settings.GITMARK_BASE_DIR)
	
	get_content= getYesNoFromUser('do you want to pull down the content of a page when you download a bookmark?', settings.GET_CONTENT)
	
	content_cache_mb = getIntFromUser('do you want to set a maximum MB of content cache?', settings.CONTENT_CACHE_SIZE_MB)
	
	remote_pub_repo = getStringFromUser('Specify a remote git repository for your public bookmarks',settings.REMOTE_PUBLIC_REPO)

	remote_private_repo = getStringFromUser('Specify a remote git repository for your private bookmarks?',settings.REMOTE_PRIVATE_REPO)
	
	remote_content_repo = None
	content_as_reop= getYesNoFromUser('do you want your content folder to be stored as a repository?',settings.CONTENT_AS_REPO)
	
	if content_as_reop is True:
		remote_content_repo = getStringFromUser('what is the git repository for your content?', settings.REMOTE_CONTENT_REPO)

	fav_color= getStringFromUser('what is your favorite color?',settings.FAVORITE_COLOR)

	wv_u_swallow = getStringFromUser('what is the windspeed velocity of an unladen swallow?',settings.UNLADEN_SWALLOW_GUESS)

	dict = { 'GITMARK_BASE_DIR':base_dir, 'GET_CONTENT':get_content,
	'CONTENT_CACHE_SIZE_MB':content_cache_mb,
	'CONTENT_AS_REPO':content_as_reop,
	'REMOTE_PUBLIC_REPO':remote_pub_repo, 'REMOTE_PRIVATE_REPO': remote_private_repo,
	'SAVE_CONTENT_TO_REPO':content_as_reop, 'REMOTE_CONTENT_REPO':remote_content_repo,
	'FAVORITE_COLOR':fav_color, 'UNLADEN_SWALLOW_GUESS':wv_u_swallow,
	"PUBLIC_GITMARK_REPO_DIR":settings.PUBLIC_GITMARK_REPO_DIR,
	'PRIVATE_GITMARK_REPO_DIR':settings.PRIVATE_GITMARK_REPO_DIR,
	'CONTENT_GITMARK_DIR':settings.CONTENT_GITMARK_DIR, 'BOOKMARK_SUB_PATH':settings.BOOKMARK_SUB_PATH,
	'TAG_SUB_PATH':settings.TAG_SUB_PATH, 'MSG_SUB_PATH':settings.MSG_SUB_PATH,
	'HTML_SUB_PATH':settings.HTML_SUB_PATH}

	return dict
		
	
def replace_value_in_file(dict,setings_filename):	
	""" 
	Does some magic to read a settings file, and replace the values in-line,
	and then write the new values back to the settings file.
	"""
	fh = open(setings_filename,'r')
	raw_settings = fh.readlines()
	fh.close()
	newlines = []
	for line in raw_settings:
		newline = line
		#print 'cur line: ' + line
		if '=' in line:
			#print 'has ='
			val = line.split('=')[0]
			comment = None
			if( line.split('#') < 1 ):
				comment = line.split('#')[-1]
			#print 'has comment ' + str(comment)
			val = val.lstrip().rstrip()
			if val in dict:
				newline = val + ' = ' + str(dict[val])
				if comment != None:
					newline += ' # ' + comment
		#print 'new line = ' + newline
		newlines.append(newline)
	if len(newlines) == len(raw_settings):
		fh = open(setings_filename +".tmp",'w')
		fh.write(newlines)
		fh.close()
		return True
	else:
		print "settings size did not match! Abandon the ship!"
		return False
	return False
	

def getIntFromUser(message, value=''):
	""" get an int value from the command line"""
	msg2 = ' '.join([message,' (',str(value),') (int): ']) 
	value = raw_input(msg2)
	try:
		return int(value)
	except:
		print "int decoe fail for %s" %value
	return None

def getStringFromUser(message,value=''):
	""" get a string value from the command line"""
	msg2 = ''.join([message,' (',str(value),') (string): ']) 
	value = raw_input(msg2)
	return value
	
def getYesNoFromUser(message,value=''):
	""" get a yes/no value from the command line"""
	msg2 = ''.join([message,' (',str(value),') (Y,n): ']) 
	value = raw_input(msg2)
	
	if(value == 'Y' or value == 'Yes' or value == 'y'):
		return True
	elif(value == 'n' or value == 'no' or value == 'N'):
		return False
	return None
	
if __name__ == '__main__':
	""" geneirc main statement"""
	configure_gitmarks()	