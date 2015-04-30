#
#message types
#
REQ_SCREENSHOT = "REQUEST_SCREENSHOT"
REQ_SCREENSHOT_FILEPATH = "REQUEST_SCREENSHOT_FILEPATH"

RES_SCREENSHOT_ACK = "SCREENSHOT_ACK"
RES_SCREENSHOT_FILEPATH = "SCREENSHOT_FILEPATH"

#
#
#
TYPE = "TYPE"
URL = "URL"
WORKERS = "WORKERS"
SUCCESS = "SUCCESS"
ID = "ID"
EXISTS = "EXISTS"
FILEPATH = "FILEPATH"


#
#message structure
#
request_screenshot = {
	TYPE:None,
	URL:None,
}
request_screenshot_filepath = {
	TYPE:None,
	URL:None,
	WORKERS:None,
}
response_screenshot_ack = {
	TYPE: None,
	SUCCESS:None,
	ID:None,
}
response_screenshot_filepath = {
	TYPE: None,
	EXISTS:None,
	FILEPATH:None,		#only if EXISTS == True
}
#
#pika consumer tags
#
SENDER = "SENDER"
RECEIVER = "RECEIVER"
READER = "READER"

def printmsg(msg):
	if type(msg) == str:
		msg = eval(msg)

	for k in msg:
		print '\t',k,':',msg[k]

