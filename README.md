# screenshot-service
A Python based scalable back-end service using RabbitMQ's pika library.

#####How to:
- Start the reader component: <br/>
  ``` python reader.py ```
- Start a couple of independent receiver components by assigning them an id: <br/>
  ``` python receiver.py 1 ``` , ``` python receiver.py 2 ``` etc.
- Start the sender component: <br/>
  ``` python sender.py ``` <br/>
   or <br/>
  ``` python sender.py <urls> ``` <br/>
  with ``` <urls> ``` being a file with urls, one per line.

- ``` receiver.py ``` receives the requests for downloading the screenshots and downloads them.
- Request a screenshot by querying it to ``` sender.py ``` as ```get <url>``` (\<url\> should be exactly the same as requested previously, or as in the ``` <urls> ``` file, otherwise it will not be found in the existing screenshots, and a new request for downloading will be issued.

#####Requirements:
- Linux
- RabbitMQ
- RabbitMQ (pika) for python
- gnome-web-photo should be already built-in in Linux.
