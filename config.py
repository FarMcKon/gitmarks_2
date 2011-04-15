#!/usr/bin/env python
# encoding: utf-8
"""
Configuration script for gitmarks.py

This script is a quick setup function for getting basic settings good
for running gitmarks
"""

import example_settings

import sys
import os
import subprocess
import shutil

from gitmarks_exceptions import InputError, SettingsError, GitError
from config_helpers import get_int, get_string, get_yes_or_no

# Arguments are passed directly to git, not through the shell, to avoid the
# need for shell escaping. On Windows, however, commands need to go through the
# shell for git to be found on the PATH, but escaping is automatic there. So
# send git commands through the shell on Windows, and directly everywhere else.
USE_SHELL = os.name == 'nt'


def main():
    """Main"""

    print """
        Wecome to gitmarks configurator. This will setup a couple of local
        repositories for you to use as your gitmarks system.  Gitmarks will
        maintain 2-3 repositories.
         - 1 for public use (world+dog read)
         - 1 for friends use (with some encryption)
         - 1 (optional) for content. This can be non-repo, or nonexistant.
    """

    if not get_yes_or_no("Ready to start?"):
        print "Goodbye! Share and Enjoy."
        return 0

    return configure_gitmarks()


def configure_gitmarks():
    """
    This function does the basic configuration of gitmarks. It tries to
    download needed software, get settings from users, and spawns the basic
    on-disk files for the bookmarks.
    """

    # Pull needed libraries from Internet
    download_needed_software()

    # Generate our configuration settings
    user_settings = config_settings()

    try:
        cont = get_yes_or_no("Setup up local environment from " + \
                                        "above settings?")
    except InputError, err:
        print str(err)
        return -1

    if not cont:
        print "You must store settings in beta, can't continue without them."
        return -1

    # Store user settings in settings.py, use example_settings.py as starting
    # point
    create_or_update_settings(user_settings, 'settings.py',
                              'example_settings.py')

    create_local_gitmarks_folders()

    print "Setup complete."
    return 0


def download_needed_software():
    """Not implemented"""
    # wget http://python-gnupg.googlecode.com/files/python-gnupg-0.2.6.tar.gz
    # or get gpg or pgp instead?
    pass


def setup_repo(remote_repo, base_dir, local_dir, subdirs):
    """
    Setup repository in local directory and populate it with given
    subdirectories
        remote_repo - Name of remote repo
        base_dir    - Full path to base directory for repo
        local_dir   - Name of local directory (subdirectory within the base_dir
                      to put repo
        subdirs      - List of sub directories to populate repo with
    """

    repo_dir = os.path.join(base_dir, local_dir)

    # If we have remote public repo, try to git-clone to create local copy.
    if (remote_repo != None):
        if not folder_is_git_repo(repo_dir):
            ret = clone_to_local(base_dir, repo_dir, remote_repo)
            if(ret != 0):
                raise GitError("Remote public clone to local failed")

    # No remote public repo, make a dir and git-init it as needed
    else:
        abs_repo_dir = os.path.abspath(repo_dir)

        # Create a dir if we need to
        if not os.path.isdir(abs_repo_dir):
            os.makedirs(abs_repo_dir)

        # Init the new git repo
        ret = init_git_repo(abs_repo_dir)
        if(ret != 0):
            raise GitError("Initializing '%s' failed" % (abs_repo_dir))

        # Create our sub-dirs
        make_gitmark_subdirs(abs_repo_dir, subdirs)


def create_local_gitmarks_folders():
    """
    This function creates local repository folders. If we have a remote
    repo name, it will try to sync that data to this place.  If the settings
    remote repository info is "None" it will just create a local repo without a
    remote connection.
        - Raises GitError if problems cloning local repos
        - Raises ImportError if unable to import settings.py
    """

    # Now we can load the settings we just created
    try:
        import settings
    except ImportError, err:
        print "Failed loading settings.py module"
        raise err

    abs_base_dir = os.path.abspath(settings.GITMARK_BASE_DIR)

    # List of subdirectories to populate repos with
    subdirs = [settings.BOOKMARK_SUB_PATH, settings.TAG_SUB_PATH,
                settings.MSG_SUB_PATH]

    # Create a base directory if we need to
    if not os.path.isdir(abs_base_dir):
        print "Creating base directory, '%s', for gitmarks" % (abs_base_dir)
        os.makedirs(abs_base_dir)

    # Setup the public repo locally
    setup_repo(settings.REMOTE_PUBLIC_REPO, settings.GITMARK_BASE_DIR,
               settings.PUBLIC_GITMARK_REPO_DIR, subdirs)

    # Setup the private repo locally
    setup_repo(settings.REMOTE_PRIVATE_REPO, settings.GITMARK_BASE_DIR,
               settings.PRIVATE_GITMARK_REPO_DIR, subdirs)

    # Create our local content directory and repo, even if we never use it
    content_dir = os.path.join(settings.GITMARK_BASE_DIR,
                                settings.CONTENT_GITMARK_DIR)
    if not os.path.isdir(content_dir):
        print "Creating content directory, '%s', for gitmarks" % (content_dir)
        os.makedirs(content_dir)

    init_git_repo(content_dir)


def clone_to_local(base_dir, folder_name, remote_git_repo):
    """Clones a repository at remote_git_repo to a local directory"""

    print "Cloning repository '%s' to directory '%s'" % (remote_git_repo,
                                                        folder_name)

    #swizzle our process location so that we get added to the right repo
    base_dir = os.path.abspath(base_dir)
    cwd_dir = os.path.abspath(os.getcwd())
    os.chdir(os.path.abspath(base_dir))
    ret = subprocess.call(['git', 'clone', remote_git_repo, folder_name],
                            shell=USE_SHELL)
    os.chdir(cwd_dir)
    return ret


def init_git_repo(directory):
    """Initalize git repo in directory (absolute path)"""

    # Change directory and init
    cwd_dir = os.path.abspath(os.getcwd())
    os.chdir(os.path.abspath(directory))
    ret = subprocess.call(['git', 'init', '.', ], shell=USE_SHELL)

    # Change back to what we were
    os.chdir(cwd_dir)

    return ret


def make_gitmark_subdirs(folder_name, subdirs_list):
    """ makes a stack of gitmarks subdirectories at the folder listed """
    for new_dir in subdirs_list:
        new_dir = os.path.join(folder_name, new_dir)
        new_dir = os.path.abspath(new_dir)
        os.makedirs(new_dir)
        #TODO: appears git does not add empty dirs. If it did, we would add
        #      that here
    return


def folder_is_git_repo(folder_name):
    """Determine if a given folder is a valid git repository"""
    git_folder = os.path.join(folder_name, '/.git/')
    return os.path.isdir(git_folder)


def config_settings():
    """Returns dict of config settings set interactivly by user"""

    base_dir = get_string('What base directories do you want ' + \
                    'for your repos?', example_settings.GITMARK_BASE_DIR)

    get_content = get_yes_or_no('Do you want to pull down ' + \
                    'content of page when you download a bookmark?',
                    example_settings.GET_CONTENT)

    content_cache_mb = get_int('Do you want to set a maximum MB ' + \
                    'of content cache?',
                    example_settings.CONTENT_CACHE_SIZE_MB)

    remote_pub_repo = get_string('Specify remote git repository ' + \
                        'for your public bookmarks',
                        example_settings.REMOTE_PUBLIC_REPO)

    remote_private_repo = get_string('Specify remote git ' + \
                        'repository for your private bookmarks?',
                        example_settings.REMOTE_PRIVATE_REPO)

    remote_content_repo = None
    content_as_reop = get_yes_or_no('Do you want your content ' + \
                        'folder to be stored as a repository?',
                        example_settings.CONTENT_AS_REPO)

    if content_as_reop is True:
        remote_content_repo = get_string('What is git ' + \
                                'repository for your content?',
                                example_settings.REMOTE_CONTENT_REPO)

    print "-- User Info --"
    user_name = get_string("What username do you want to use?",
                    example_settings.USER_NAME)
    user_email = get_string("What email do you want to use?",
                    example_settings.USER_EMAIL)
    machine_name = get_string("What is the name of this computer?",
                    example_settings.MACHINE_NAME)

    return {'GITMARK_BASE_DIR': base_dir,
            'GET_CONTENT': get_content,
            'CONTENT_CACHE_SIZE_MB': content_cache_mb,
            'CONTENT_AS_REPO': content_as_reop,
            'REMOTE_PUBLIC_REPO': remote_pub_repo,
            'REMOTE_PRIVATE_REPO': remote_private_repo,
            'SAVE_CONTENT_TO_REPO': content_as_reop,
            'REMOTE_CONTENT_REPO': remote_content_repo,
            'PUBLIC_GITMARK_REPO_DIR':
                example_settings.PUBLIC_GITMARK_REPO_DIR,
            'PRIVATE_GITMARK_REPO_DIR':
                example_settings.PRIVATE_GITMARK_REPO_DIR,
            'CONTENT_GITMARK_DIR': example_settings.CONTENT_GITMARK_DIR,
            'BOOKMARK_SUB_PATH': example_settings.BOOKMARK_SUB_PATH,
            'TAG_SUB_PATH': example_settings.TAG_SUB_PATH,
            'MSG_SUB_PATH': example_settings.MSG_SUB_PATH,
            'HTML_SUB_PATH': example_settings.HTML_SUB_PATH,
            'USER_NAME': user_name,
            'USER_EMAIL': user_email,
            'MACHINE_NAME': machine_name}


def create_or_update_settings(user_settings, settings_filename,
                              opt_example_file=None):
    """
    Default all settings to the ones in the example settings file (if exists)
    and overwrite defaults with setting from user
    """

    if not os.path.isfile(settings_filename) and not opt_example_file:
        raise SettingsError("Add example_settings.py or settings.py")

    # Default all user settings to example settings file if one is given
    shutil.copy(opt_example_file, settings_filename)

    fh = open(settings_filename, 'r')
    raw_settings = fh.readlines()
    fh.close()

    # Lines to be written to settings file with mesh of default and user
    # settings as requested
    newlines = []

    # Parse lines of settings file and override with user-supplied setting if
    # it exists otherwise, leave the setting alone (all settings are defaulted
    # with example above)
    for line in raw_settings:
        newline = line.rstrip()

        # Skip comment lines and lines that don't have a setting specified
        if line.startswith('#') or '=' not in line:
            newlines.append(line)
            continue

        # File is key=value format, but just need the key to see if the user
        # specified it
        var = line.split('=')[0].lstrip().rstrip()

        # Overwrite default setting if user specified it otherwise just write
        # default one
        if var in user_settings:
            if type(user_settings[var]) is str:
                newline = var + " = '" + str(user_settings[var]) + "'"
            else:
                newline = var + " = " + str(user_settings[var])

        newlines.append(newline)

    # We better have written every line of the example file, otherwise we
    # missed something and have a SW bug
    if len(newlines) == len(raw_settings):
        fh = open(settings_filename, 'w')
        fh.write('\n'.join(newlines))
        fh.close()
    else:
        raise SettingsError("Settings size did not match")


if __name__ == '__main__':
    sys.exit(main())
