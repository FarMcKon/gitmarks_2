
import subprocess
from subprocess import Popen, PIPE, STDOUT

def prettyPrintLocalSecretKeys():
	pipe = subprocess.Popen("gpg --list-keys", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
	stdout = pipe.stdout.read()

	lines = stdout.split('\n')
		
if __name__ == '__main__':
	prettyPrintLocalSecretKeys()
	
	