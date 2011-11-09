import re
import sys
import select
import socket
import requests
import urlparse 
import pybonjour


#
# The Magic AirPlay tcp host
regtype = "_airplay._tcp"

_input = sys.argv[1] # Gets the Youtube Video url
timeout = 5 # 5 Seconds timeout on each request
resolved = []
queried = []
resolvedHosts = []


# 
# Data Model for a Youtube Video
#
class YoutubeVideo:
	def __init__(self, url, displayname):
		self.url = url
		self.displayname = displayname
		
#
# Data Model for a Air Play Device
#
class AirPlayDevice:
	def __init__(self, interfaceIndex, fullname, hosttarget, port):
		self.interfaceIndex = interfaceIndex
		self.fullname = fullname
		self.hosttarget = hosttarget
		self.port = port;
		self.displayname = hosttarget.replace(".local.", "")
		self.ip = 0



def htc(m):
    return chr(int(m.group(1),16))

def urldecode(url):
    rex = re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M)
    return rex.sub(htc,url)


def is_youtube_type(target):
	return "youtube" in target
#
# Parsing the Youtube query string to get the video Id
def get_youtube_id(vidUrl):
	return urlparse.parse_qs(urlparse.urlparse(vidUrl).query)["v"][0]

#
# Parsing the Youtube video info page
def parse_youtube_info(ytId):
	youtubeString = "http://www.youtube.com/get_video_info?video_id=%s" % (ytId)
	r = requests.get(youtubeString)
	content = r.content

	content = urlparse.parse_qs(content)
	content = content["url_encoded_fmt_stream_map"][0]

	content = content.split("url=")
	
	return content

#
# Gets all the supported formats from Youtube
def get_supported_formats(c):
	atvSupported = []
	
	for url in c:
		decodedURL = urldecode(url).replace(",", "")
		queryStrings = urlparse.parse_qs(urlparse.urlparse(decodedURL).query)
		if queryStrings:
			if queryStrings["type"][0] == "video/mp4":
				approvedURL = re.sub("&itag=([0-9])*$", "", decodedURL)
				approvedURL = re.sub("&fallback_host.*$", "", approvedURL)
				
				quality = queryStrings["quality"][0]
				displayname = ""
				if quality == "medium":
					displayname = "Medium"
				elif quality == "hd720":
					displayname = "720p"
				elif quality == "hd1080":
					displayname = "1080p"
				else:
					displayname = quality

				atvSupported.append(YoutubeVideo(approvedURL, displayname))
	
	if len(atvSupported) <= 0:
		print "No supported formats"
		sys.exit()
		return;
		
	return atvSupported

#
# Defines the Post message to play the selected video
def post_message(sel_vid):
	body = "Content-Location: %s\nStart-Position: 0\n\n" % (sel_vid)
	return "POST /play HTTP/1.1\n" \
		   "Content-Length: %d\n"  \
		   "User-Agent: MediaControl/1.0\n\n%s" % (len(body), body)

#
# Connecting to the selected AirPlay device
# and sends the video to it
def connect_to_socket(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))
	s.send(post_message(selectedVideo))
	s.close()

#
# Gets the IP from selected device
def query_record_callback(sdRef, flags, interfaceIndex, errorCode, fullname, rrtype, rrclass, rdata, ttl):
	if errorCode == pybonjour.kDNSServiceErr_NoError:
		resolved_ip = socket.inet_ntoa(rdata)
		for host in resolvedHosts:
			if host.hosttarget == fullname:
				host.ip = resolved_ip
				break
		
		queried.append(True)

#
# It found a device
def resolve_callback(sdRef, flags, interfaceIndex, errorCode, fullname, hosttarget, port, txtRecord):
	if errorCode == pybonjour.kDNSServiceErr_NoError:
		resolvedHosts.append(AirPlayDevice(interfaceIndex, fullname, hosttarget, port))
		resolved.append(True)

#
# Looking for devices
def browse_callback(sdRef, flags, interfaceIndex, errorCode, serviceName, regtype, replyDomain):
	if errorCode != pybonjour.kDNSServiceErr_NoError:
		return
		
	if not (flags & pybonjour.kDNSServiceFlagsAdd):
		return
	
	resolve_sdRef = pybonjour.DNSServiceResolve(0, interfaceIndex, serviceName, regtype, replyDomain, resolve_callback)
	
	try:
		while not resolved:
			ready = select.select([resolve_sdRef], [], [], timeout)
			if resolve_sdRef not in ready[0]:
				print 'Resolve timed out'
				break
			
			pybonjour.DNSServiceProcessResult(resolve_sdRef)
		else:
			resolved.pop()
			
	finally:
		resolve_sdRef.close()




### --- START --- ###

if is_youtube_type(_input):
	youtubeId = get_youtube_id(_input)
	content = parse_youtube_info(youtubeId)
	formats = get_supported_formats(content)


	### --- UNCOMMET TO LET USER CHOOSE VIDEO QUALITY --- ###
		#print "-----"
		#print "This video is available in the following formats:"
		#print "-----"
		#count = 1
		#for ytVideo in formats:
		#	print "%d: %s" % (count, ytVideo.displayname)
		#	count += 1
		#
		#print "-----\n"
		#selectedVideoIndex = int(raw_input("Select your video format...\n")) - 1

	### 
	if len(formats) == 0:
		sys.exit()
	
	
	selectedVideo = formats[0].url
else:
	selectedVideo = _input

browse_sdRef = pybonjour.DNSServiceBrowse(regtype = regtype, callBack = browse_callback)

try:
	try:
		ready = select.select([browse_sdRef], [], [])
		if browse_sdRef in ready[0]:
			pybonjour.DNSServiceProcessResult(browse_sdRef)
	except KeyboardInterrupt:
		pass
finally:
	browse_sdRef.close()

print "-----"
print "Available AirPlay Devices"
print "-----"
count = 1
for host in resolvedHosts:
	print "%d: %s" % (count, host.displayname)
	count += 1
	
print "-----"
selectedHost = int(raw_input("Select your airplay device...\n")) - 1

if selectedHost >= len(resolvedHosts):
	sys.exit("ERROR: There is no device at that index")

host = resolvedHosts[selectedHost]
print "Connecting to: %s" % (resolvedHosts[selectedHost].displayname)

query_sdRef = pybonjour.DNSServiceQueryRecord(interfaceIndex = host.interfaceIndex, fullname = host.hosttarget, rrtype = pybonjour.kDNSServiceType_A, callBack = query_record_callback)

try: 
	while not queried:
		ready = select.select([query_sdRef], [], [], timeout)
		if query_sdRef not in ready[0]:
			print "Query not in record"
			break
		pybonjour.DNSServiceProcessResult(query_sdRef)
	else:
		queried.pop()
		
finally:
	query_sdRef.close()


connect_to_socket(host.ip, host.port)
