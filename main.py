#!/usr/bin/env python3
import requests
import re
import sys
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
	#print(response.status_code)
	items = html.main.find_all('li')

	for item in items:
		if 'folder-item' in item['class']:
			title = item.find(class_="folder-name", attrs={"lang": "en"}).text
			print(title)
			fetch_folder(title, BASE_URL + re.sub(r'[^/]+\.html$', '', url) + item.find(class_="folder-link")['href'], depth + 1)
		if 'document-item' in item['class']:
			documenttitle = item.find(class_="document-name", attrs={"lang": "en"}).text
			print(documenttitle)
			fetch_document(documenttitle, BASE_URL + re.sub(r'[^/]+\.html$', '', url) + item.find(class_="document-link")['href'])

		if depth == 0:
			generate_pdf(title.split(' ')[0])

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
url = re.search(r'.*url=([^\s]+).*', html.head.find(attrs={"http-equiv": "Refresh"})['content']).group(1)

fetch_folder("AIP", BASE_URL + url)
