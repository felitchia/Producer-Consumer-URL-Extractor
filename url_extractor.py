#!/usr/bin/env python3

from threading import Thread
from queue import Queue
from bs4 import BeautifulSoup
import requests
import re
import os
import sys
import subprocess
import json

FILENAME = os.path.join(os.path.dirname(__file__), 'files/urls.txt')
QUEUE_BUFFER_SIZE = 10


class Producer(Thread):
    def __init__(self, input_queue, output_queue):
        """Initialized with a input_queue which is a list of urls and an output queue where the
        fetched data is put for the consumer."""
        Thread.__init__(self, name="producer_thread")
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        """Extracts the markup for each url and puts it on the queue for the consumer as a
        dictionary with the url as key and markup as value"""

        for url in self.input_queue:
            markup = extract_markup(url)
            url_markup = {}
            url_markup['url'] = url
            if markup != None:
                url_markup['markup'] = (markup)
                if not self.output_queue.full():
                    self.output_queue.put(url_markup)
                    print("Producing", url)
        self.output_queue.put(None)


class Consumer(Thread):
    def __init__(self, input_queue, hyperlinks):
        """Initialized with a input_queue with contains {'url':'markup'} dictionaries and
        hyperlinks which stores the hyperlinks extracted from the markup"""

        Thread.__init__(self, name="consumer_thread")
        self.input_queue = input_queue
        self.hyperlinks = hyperlinks

    def run(self):
        """For each markup on queue extracts the hyperlinks and saves them in a list of
        dictionaries of the form {'url':'hyperlink'}, until the producer announces its done"""

        while True:
            if not self.input_queue.empty():
                extracted_markup = self.input_queue.get()
                if extracted_markup is None:
                    break
                url_link = {}
                url_link['url'] = extracted_markup['url']
                markup = extracted_markup['markup']
                links = get_links(markup)
                url_link['hyperlinks'] = links
                self.hyperlinks.append(url_link)
                print("Consuming", extracted_markup['url'])


def extract_markup(url):
    """Receives a link and returns that link's whole markup"""

    user_agent = {'User-agent': 'Mozilla/5.0'}
    markup = None

    try:
        page = requests.get(url, headers=user_agent)
        markup = BeautifulSoup(page.content, 'html.parser')
        if re.match('4[0-9]{2}', str(page.status_code)) is not None or re.match('5[0-9]{2}',
                                                                                str(page.status_code)) is not None:
            with open("files/fetch.log", "a") as f:
                f.write("Fetched {0} with status code: {1}\n".format(str(url), page.status_code))

    except requests.exceptions.RequestException as e:
        with open("files/fetch.log", "a") as f:
            f.write("Failed to fetch {0}: {1}\n".format(str(url), str(e)))
            # print(e)

    return markup


def get_links(markup):
    """Receives html markup and returns the hyperlinks found"""

    links = []
    for link in markup.find_all('a', href=True):
        links.append(link['href'])

    return links


def read_file(inputfile):
    """reads from a file containing a list of urls separated by \n and
    outputs a list of those links"""
    with open(inputfile, 'r') as f:
        urls = f.read().splitlines()

    return urls


def write_file(list, outputfile):
    """writes a list os {'url':'hyperlinks'} dictionaries to a json file"""
    with open(outputfile, 'w') as f:
        json.dump(list, f)


def main():
    urls = read_file(FILENAME)

    with open("files/fetch.log", "w") as f:
        f.write("")

    queue = Queue(QUEUE_BUFFER_SIZE)
    hyperlinks = []

    producer = Producer(urls, queue)
    consumer = Consumer(queue, hyperlinks)

    producer.start()
    consumer.start()
    producer.join()
    consumer.join()

    write_file(consumer.hyperlinks, 'files/hyperlinks.json')


if __name__ == "__main__":
    if '--unittest' in sys.argv:
        subprocess.call([sys.executable, '-m', 'unittest', 'discover'])
    main()
