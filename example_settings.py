
## Local File Settings:
# -- Core Dirs
GITMARK_BASE_DIR = 'gitmark_base' # base directory for gitmarks resources
PUBLIC_GITMARK_REPO_DIR = 'public' # public subdirectory for gitmarks local resources
PRIVATE_GITMARK_REPO_DIR = 'private' # private subdirectory for gitmarks local resources
CONTENT_GITMARK_DIR = 'content' #optional local content directories
# --Sub Dirs
BOOKMARK_SUB_PATH = 'bookmarks' #local bookmarks subdirectory
TAG_SUB_PATH = 'tags' #local tags data subdirectory
MSG_SUB_PATH = 'msg' #local messages/push data subdirectory
HTML_SUB_PATH = 'html' #local content subdirectory

## Remote Repository Info
REMOTE_PUBLIC_REPO = None
REMOTE_PRIVATE_REPO = None 
REMOTE_CONTENT_REPO = None #optional content repository

# Content fetch settings
CONTENT_AS_REPO = True
GET_CONTENT= True
CONTENT_CACHE_SIZE_MB = 400

# Gitmarks web portal info
GITMARKS_WEB_PORT = 44865

# TOOD: make config create or grab or fetch this info
USER_NAME ="Example Name"
USER_EMAIL="ExampleName@example.com"
MACHINE_NAME="Example Computer Name"

# Other Stuff
FAVORITE_COLOR = "Red"
UNLADEN_SWALLOW_GUESS = "I don't know"