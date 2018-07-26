# Producer/Consumer URL Extractor

Python 3.6.

## Install Requirements

`pip install -r requirements.txt`

## Run program

`python url_extractor.py`

## Run program after the tests

`python url_extractor.py --unittests`

## Run tests

`python tests.py`


* urls.txt contain urls used for inpus (more_urls.txt contains a bigger sample)
* hyperlinks.json is outputted with the extracted hyperlinks for each of the urls
* fetch.log are registered links whose request resulted in failure or that were fetched but with a client or server request error.