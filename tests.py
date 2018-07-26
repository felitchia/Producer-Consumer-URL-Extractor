#!/usr/bin/env python3

import unittest
from unittest import mock
import os
import requests
import time
from queue import Queue
import url_extractor


def mock_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, content, status_code):
            self.content = content
            self.status_code = status_code

    if args[0] == 'http://t1':
        return MockResponse('<!DOCTYPE html><html><body><a href="www.test.com">url</a></body></html>', 200)
    elif args[0] == 'http://t2':
        return MockResponse(
            '<!DOCTYPE html><html><body><a href="www.test.com"><a href="www.test2.com">url2</a></body></html>', 200)
    elif args[0] == 'http://t3':
        return MockResponse('<!DOCTYPE html><html><body></body></html>', 200)

    return MockResponse(None)


class Tests(unittest.TestCase):
    def test_extract_markup_invalid_link(self):
        '''Invalid links should result in a RequestException'''
        self.assertRaises(requests.exceptions.RequestException, url_extractor.extract_markup('not_a_link'))

    @mock.patch('requests.get', side_effect=mock_requests_get)
    def test_extract_markup(self, mock_get):
        """Extracts markup from mock"""
        markup = url_extractor.extract_markup('http://t1')
        self.assertEqual(str(markup), '<!DOCTYPE html>\n<html><body><a href="www.test.com">url</a></body></html>')

    @mock.patch('requests.get', side_effect=mock_requests_get)
    def test_get_links_1_link(self, mock_get):
        """Extracts markup from mock and then 1 link"""
        markup1 = url_extractor.extract_markup('http://t1')
        links1 = url_extractor.get_links(markup1)
        self.assertEqual(links1, ['www.test.com'])

    @mock.patch('requests.get', side_effect=mock_requests_get)
    def test_get_links_2_links(self, mock_get):
        """Extracts markup from mock and then 2 links"""
        markup2 = url_extractor.extract_markup('http://t2')
        links2 = url_extractor.get_links(markup2)
        self.assertEqual(links2, ['www.test.com', 'www.test2.com'])

    @mock.patch('requests.get', side_effect=mock_requests_get)
    def test_get_links_no_links(self, mock_get):
        """Extracts markup from mock and then no links"""
        markup3 = url_extractor.extract_markup('http://t3')
        links3 = url_extractor.get_links(markup3)
        self.assertEqual(links3, [])

    def test_consumer(self):
        queue = Queue(1)
        hyperlinks = []
        consumer = url_extractor.Consumer(queue, hyperlinks)
        consumer.start()
        self.assertEqual(consumer.isAlive(), True)
        queue.put(None)
        time.sleep(0.2)
        self.assertEqual(consumer.isAlive(), False)


if __name__ == '__main__':
    unittest.main()
