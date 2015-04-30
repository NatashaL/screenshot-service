#!/usr/bin/env python
import pika
import time
import md5
import sys
import os
from utils import * 
class Receiver:
	
	#
	# Initialize connections and database
	#
	def __init__(self,index):
		self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
		self.channel = self.connection.channel()
		self.channel.queue_declare(queue='requests', durable=True)				#queue for receiving requests
		self.channel.queue_declare(queue='responses', durable=True)				#queue for sending responses

		self.initDB(index)

	#
	# Initialize local database. Or do nothing if it already exists.
	#
	def initDB(self,index):
		self.dbname = 'DB' + index

		dirs = os.listdir('.')
		for d in dirs:
			if self.dbname in d: 
				return

		os.mkdir('./'+self.dbname)
	
	#
	# Get and save a screenshot from the given url.
	#
	def saveScreenshot(self,url):
		os.system('gnome-web-photo -t 0 --mode=photo %s %s/%s 2> out && rm out' % (url,self.dbname,md5.new(url).hexdigest()))
		return True

	#
	# Parse messages from the 'requests' queue, forwarding the work to 'saveScreenshot' method.
	#
	def work(self):
		def callback(ch, method, properties, msgbody):
			msg = eval(msgbody)

			print " [x] Received: "
			printmsg(msg)
			
			mymsg = {}
			mymsg[TYPE] = RES_SCREENSHOT_ACK
			mymsg[SUCCESS] = self.saveScreenshot(msg[URL])
			mymsg[ID] = os.getcwd()+'/'+self.dbname

			self.channel.basic_publish(exchange='', routing_key='responses', body=str(mymsg),properties=pika.BasicProperties(delivery_mode = 2,))

			print " [x] Push to queue = 'responses':"
			printmsg(mymsg)

			ch.basic_ack(delivery_tag = method.delivery_tag)

		self.channel.basic_qos(prefetch_count=1)
		self.channel.basic_consume(callback, queue='requests')
		self.channel.start_consuming()
rcv = None
def __main__():
	global rcv
	rcv = Receiver(sys.argv[1])
	rcv.work()

try:
	__main__()

except KeyboardInterrupt:
	rcv.connection.close()
