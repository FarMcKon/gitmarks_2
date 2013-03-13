========
Gitmarks
========
Gitmarks is:

* A peer to peer web bookmark manager. This tool is a way to privately share bookmarks to your friends, without using a centralized server.  

* A local webpage cache system, so you can track websites over time, and keep copies of old content, along with an md5 hash, and other metadata to verify that the page is what you expect/know.

* A tool to pull bookmarks from a system like Delicious, and save them into gitmarks, so you do not lose existing bookmarks you may have saved in other systems. 

=======
Quickstart:
=======

1) Download gitmarks:
The best way is to get it via git.  Browse to a diretory to install it in, and run:  
 'git clone git://github.com/FarMcKon/gitmarks_2.git'

2) Run setup:
To setup what repository system you want to use for storing your gitmarks, you will need to run the setup program. You can do that at the command line (in your gitmarks code directory) by running.
  'python config.py'
You will be promoted to create a github account and directories if you use defaults. 

3) Start adding bookmarks!
You can import your delicious bookmarks via 
 'python delicious_import.py'
Or you can add bookmarks directly at the command line by running 
 'gitmark.py [options] uri'

====
Details
====
Gitmarks uses 2 git repositories for your bookmarks. One stores public bookmarks (called 'public' ) and the second stores private bookmarks ( called 'private') a 3rd optional repository 'cache' can be used to store a local cache of all of your bookmark files.  The cache will be update <TBD>

Each time you bookmark a URL gitmarks will:
 - Create a bookmark file from the bookmark and tags
 - Generate a bit of bookmark metadata (you can tweak how much) in the 'tags' directory.
 - Cache a local file of that page (if you have cache enabled)
 - If you have more than 20 un-committed changes, gitmarks will commit those changes to the local repository.
 - If you bookmark something to a person, it will send your bookmark (unencrypted for now) to that 
 person. 
 
 You can use git as usual to see who committed what and when, or you can grep your way to bookmark happiness on the command line.

It's great for groups to collaboratively collect bookmarks in one spot (thanks to git itself!)


=====
Usage
=====

python gitmark_add.py [url]

options:
	-p = do not push to origin (store bookmark locally only)
	-m = description of the bookmark
	-t = a comma-delimited list of tags
	
Example:

python gitmark.py -m 'my site' -t me,hilary_mason,code,bookmarks http://www.hilarymason.com






===============
OMG Delicious?!
===============

Yes, you can import your delicious bookmarks!

Usage:

python delicious_import.py [username] [password]

(be patient if you have a lot of them.)


=============================
Using the Browser Bookmarklet
=============================

First, run the gitmark_web server:

python gitmark_web.py

Then, go to the following URL and drag the bookmarklet into your browser's toolbar:

http://localhost:44865/

(where 44865 is the port you set in settings.py)


=======
License
=======
Copyright 2011 Far McKon.  Based on code that is Copyright 2010 Hilary Mason.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
