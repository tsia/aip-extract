#!/usr/bin/env python3
import requests
import re
import os
import io
import ocrmypdf
import base64
import tempfile
import img2pdf
from bs4 import BeautifulSoup

BASE_URL = 'https://aip.dfs.de/basicVFR/'

images = []

def fetch_url(url):
	response = requests.get(url)
	# The AIP website sends us a misleading header `Content-Type: text/html`
	# which results in the default ISO-8859-1 encoding. Hence we override
	# encoding by an educated guess
	response.encoding = 'utf-8'
	#print(f'Fetching {url} ({response.status_code})')
	return response.text, response.url

def fetch_html(url):
	return BeautifulSoup(fetch_url(url)[0], 'lxml')

def fetch_folder(foldertitle, folderurl, depth = 0):
	#print(folderurl)
	html = fetch_html(folderurl)
	items = html.main.find_all('a', class_=['folder-link', 'document-link'])

	for item in items:
		if 'folder-link' in item['class']:
			title = item.find(class_='folder-name', attrs={'lang': 'en'}).text
			print(title)
			fetch_folder(title, requests.compat.urljoin(BASE_URL, item.get('href')), depth + 1)
		if 'document-link' in item['class']:
			documenttitle = item.find(class_='document-name', attrs={'lang': 'en'}).text
			print(f'  {documenttitle}')
			fetch_document(documenttitle, requests.compat.urljoin(BASE_URL, item.get('href')))

		if depth == 0:
			generate_pdf(title.strip())

def fetch_document(documenttitle, documenturl):
	global images
	#print(documenturl)
	html = fetch_html(documenturl)
	image = html.main.find('img', id='imgAIP').get('src')
	imagedata = image.split('data:image/png;base64,')[1]
	images.append(base64.decodebytes(imagedata.encode('ascii')))

def generate_pdf(title):
	global images
	tmp = tempfile.NamedTemporaryFile(suffix='.pdf')
	tmp.write(img2pdf.convert(images))
	ocrmypdf.ocr(input_file=tmp.name, output_file=f'output/{title}.pdf')
	tmp.close()
	images = []

# The original base URL redirects to the current version of the AIP
_, url = fetch_url(BASE_URL)
BASE_URL = url

fetch_folder("AIP", BASE_URL)
