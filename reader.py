#!/usr/bin/env python
import pika
import time
import md5
import sys
import os
from utils import *

class Reader:
	
	#
	# Initialize connection and queues
	#
	def __init__(self):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()

		self.channel.queue_declare(queue='reads',durable=True)				#queue for receiving filepath requests
		self.channel.queue_declare(queue='responses', durable=True)			#queue for sending filepath responses

	#
	# Checks if <filename> exists in database <dbname>
	#
	def fileExists(self,dbname, filename):
		return os.path.isfile('%s/%s' % (dbname,filename))

	#
	# Callback function for each "reads" message
	# Scans databases for the screenshot requested, and responds with the filepath if it exists.
	#
	def openEntry(self,ch, method, properties, msgbody):
		msg = eval(msgbody)

		print " [x] Received:"
		printmsg(msg)

		filename = md5.new(msg[URL]).hexdigest()
		workers = msg[WORKERS]		
		exists = False
		for db in workers:
			if self.fileExists(db, filename):		
				self.respond(msg[URL],db,filename)
				exists = True

		if not exists:
			self.respond(msg[URL],'','',False)

		ch.basic_ack(delivery_tag = method.delivery_tag)

	#
	# Psuh a message to the "responses" queue, corresponding to the "read" requests
	#
	def respond(self,url,db,filename,exists=True):
		mymsg = {TYPE:RES_SCREENSHOT_FILEPATH,
			 EXISTS:exists,
			 URL:url}

		if exists:
			mymsg[FILEPATH] = db+'/'+filename

		print " [x] Push to queue = 'responses': "
		printmsg(mymsg)

		self.channel.basic_publish(exchange='', routing_key='responses', body=str(mymsg),properties=pika.BasicProperties(delivery_mode = 2,))

	#
	# Pop messages from queue "reads"
	#
	def work(self):
		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(self.openEntry, queue='reads')
		self.channel.start_consuming()
reader = None
def __main__():
	global reader
	reader = Reader()
	reader.work()

try:
	__main__()

except KeyboardInterrupt:
	reader.connection.close()
