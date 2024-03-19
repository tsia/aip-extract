#!/usr/bin/env python3
import base64
import img2pdf
import ocrmypdf
import requests
import tempfile
from bs4 import BeautifulSoup

BASE_URL = 'https://aip.dfs.de/basicVFR/'

images = []
seen = []

def fetch_url(url):
	session = requests.Session()
	response = session.get(url)
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
	items = html.find_all('a', class_=['folder-link', 'document-link'])

	for item in items:
		if 'folder-link' in item['class']:
			title = item.find(class_='folder-name', attrs={'lang': 'en'}).text
			print(title)
			fetch_folder(title, requests.compat.urljoin(BASE_URL, item.get('href')), depth + 1)
		if 'document-link' in item['class']:
			documenttitle = item.find(class_='document-name', attrs={'lang': 'en'}).text
			url = requests.compat.urljoin(BASE_URL, item.get('href'))
			if url not in seen:
				print(f'  {documenttitle}')
				fetch_document(documenttitle, url)
			else:
				print(f'  {documenttitle} (skipping, seen already)')

		if depth == 0 and len(images) > 0:
			generate_pdf(title.strip())

def fetch_document(documenttitle, documenturl):
	global images
	#print(documenturl)
	html = fetch_html(documenturl)
	image = html.main.find('img', id='imgAIP').get('src')
	imagedata = image.split('data:image/png;base64,')[1]
	images.append(base64.decodebytes(imagedata.encode('ascii')))
	seen.append(documenturl)

def generate_pdf(title):
	global images
	tmp = tempfile.NamedTemporaryFile(suffix='.pdf')
	layout= img2pdf.get_fixed_dpi_layout_fun((150, 150)) # Force 150dpi which results in A5
	tmp.write(img2pdf.convert(images, layout_fun=layout))
	print(f'  -> Running OCR on {title}')
	ocrmypdf.ocr(
		input_file=tmp.name,
		output_file=f'output/{title}.pdf',
		language=['eng', 'deu'],
		output_type='pdf',
		optimize=2,
		title=title,
		author='DFS Deutsche Flugsicherung GmbH',
		progress_bar=False,
	)
	tmp.close()
	images = []

# The original base URL redirects to the current version of the AIP
_, url = fetch_url(BASE_URL)
BASE_URL = url

fetch_folder('AIP', BASE_URL)
