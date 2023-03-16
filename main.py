#!/usr/bin/env python3
import requests
import re
import os
import io
import ocrmypdf
import base64
import tempfile
from PIL import Image
from bs4 import BeautifulSoup

BASE_URL = 'https://aip.dfs.de/basicVFR/'

images = []

def fetch_folder(foldertitle, folderurl, depth = 0):
	#print(folderurl)
	response = requests.get(folderurl)
	html = BeautifulSoup(response.text, 'lxml')
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
	response = requests.get(documenturl)
	html = BeautifulSoup(response.text, 'lxml')
	#print(response.status_code)
	image = html.main.find('img')
	imagedata = base64.b64decode(re.sub(r'^data:image/png;base64,', '', image['src']))
	images.append(Image.open(io.BytesIO(imagedata)).convert('RGB'))

def generate_pdf(title):
	global images
	first_image = images[0]
	images.pop(0)
	tmpfile = tempfile.mkstemp()[1]
	first_image.save(tmpfile, format='pdf', save_all=True, append_images=images)
	images = []
	ocrmypdf.ocr(input_file = tmpfile, output_file = f'output/{title}.pdf')
	os.unlink(tmpfile)

response = requests.get(BASE_URL)
html = BeautifulSoup(response.text, 'lxml')
# The original base URL redirects to the current version of the AIP
BASE_URL = response.url

fetch_folder("AIP", BASE_URL)
