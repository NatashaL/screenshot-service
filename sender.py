#!/usr/bin/env python
import pika
import sys
import os
from utils import *
from threading import Thread

#
# Parse responses. Response can be:
#   - ACK: containing the worker's id (path to worker's db)
#   - filepath: a response from the reader, containing the full path to the requested screenshot
#
class Sender:
	#
	# Initialize connections, start thread that reads 'responses'
	#
	def __init__(self):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue='requests',durable=True)					#queue for sending requests
		self.channel.queue_declare(queue='responses',durable=True)					#queue for receiving responses
		self.channel.queue_declare(queue='reads',durable=True)						#queue for sending screenshot filepath requests

		self.workers = [] if not os.path.isfile('./workers') else self.loadWorkers()
		print self.workers
		self.urls = []		
		self.thread = Thread(target = self.recv_ack)
		self.thread.start()
		
	def loadWorkers(self):
		f = open('workers','r')
		workers = eval(f.read())
		f.close()
		return workers

	#
	# Parse the file sent as commandline argument.
	#
	def setURLsFromFile(self, filename):
		inputfile = open(filename,'r')
		self.urls = [url.strip() for url in inputfile.readlines()]
		inputfile.close()	
	#
	#send a request to the workers for each of the urls from the file
	#
	def getScreenshots(self):
		for url in self.urls:
			mymsg = {URL:url}
			self.sendRequest(mymsg)

	#
	# Send a screenshot request to workers (receive.py)
	#
	def sendRequest(self, message):
		self.channel.basic_publish(exchange='',
				           routing_key='requests',
				           body=str(message),
				           properties=pika.BasicProperties(delivery_mode = 2,))
		print " [x] Push to queue = 'requests': "
		printmsg(message)

	#
	# Keeps sender.py alive and expects user input
	#
	def wait(self):
		self.processUserRequests()

		self.thread.join()
		if self.connection.is_open:
			self.connection.close()



	#
	# Read 'get' requests from user commandline input.
	# 'get' requests show be formatted as: "get <url>" (url must be exactly the same as before)
	#
	def processUserRequests(self):
		while self.thread.isAlive():
			user_input = raw_input()
			if user_input.strip() == '': continue
		
			args = user_input.split()
			if args[0].lower() == 'get':
				mymsg = {TYPE: REQ_SCREENSHOT_FILEPATH,
					 URL: args[1].strip(),
					 WORKERS:self.workers}

				print " [x] Push to queue = 'reads': "
				printmsg(mymsg)
				
				self.channel.basic_publish(exchange='',
					      routing_key='reads',
					      body=str(mymsg),
					      properties=pika.BasicProperties(delivery_mode = 2,))
			elif args[0].lower() == 'quit':
				self.channel.stop_consuming(consumer_tag=SENDER)
				

	def recv_ack(self):
		def callback(ch, method, properties, body):
			msg = eval(body)
			print " [x] Received:"
			printmsg(msg)

			if TYPE not in msg:
				raise Exception("Invalid message format. Field TYPE is missing.")

			if msg[TYPE] == RES_SCREENSHOT_ACK:
				if msg[ID] not in self.workers:
					self.workers += [msg[ID]]
			elif msg[TYPE] == RES_SCREENSHOT_FILEPATH:
				if EXISTS in msg and msg[EXISTS] == False: 
					print
					print 'Screenshot of url: %s not in database. Try requesting again.' % msg[URL]
					print

					mymsg = {TYPE:REQ_SCREENSHOT,
						 URL:msg[URL]}
					self.sendRequest(mymsg)				
				else:
					print
					print 'Screenshot of %s is located at %s' % (msg[URL],msg[FILEPATH])
					print

					msg[FILEPATH] = msg[FILEPATH].replace(' ','\ ')
					os.popen('gnome-open ' + msg[FILEPATH]).read()
			else:
				raise Exception("Invalid message format. Field TYPE has an unexpected value.")
				
			ch.basic_ack(delivery_tag = method.delivery_tag)

		self.channel.basic_consume(callback, queue='responses',consumer_tag=SENDER)
		self.channel.start_consuming()

	def saveWorkers(self):
		f = open('workers','w')
		f.write(str(self.workers))
		f.close()

sender = None
def __main__():
	global sender
	sender = Sender()
	if len(sys.argv) > 1:
		sender.setURLsFromFile(sys.argv[1])					#get screenshots for the urls provided in the file 'urls'
	sender.getScreenshots()
	sender.wait()
	sender.saveWorkers()
try:
	__main__()

except KeyboardInterrupt:
	sender.connection.close()
