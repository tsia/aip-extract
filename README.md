# AIP Extractor

As the DFS now publishes the AIP-VFR online but each page only as an image and doesn't allow to print multiple pages, search the content and so on this tool scrapes the website and creates a nice PDF file.

## Features
- PDF creation: Pull the AIP-VFR and create one single PDF
- OCR: Convert it from pictures to a PDF with searchable text
- Docker: Optionally run the tool as a Docker container

## Use standalone
Install the requirements, these are: `python3 python3-pip Ghostscript Tesseract jbig2enc pngquant unpaper`
As well as the python packages with `pip install -r requirements.txt` to install dependencies. Then run `main.py`. this will scrape the DFS website, fetch all AIP VFR pages thate are provided as images (!), stick them together into PDF files and run OCR on it.

PDFs will be stored in the `output` folder.

Example code on Ubuntu:
```bash
sudo apt install python3  python3-pip Ghostscript Tesseract, jbig2enc, pngquant, unpaper
pip3 install -r requirements.txt
mkdir output
python3 main.py
```

## Docker container
Clone project and cd into folder. Then build container.
```bash
cd aip-extract
docker build -t aip-extract:latest .
```
Run the container once
```bash
docker run -it --rm -v "./output:/app/output" --name aip-extract aip-extract:latest
```
Or on Windows:
```bash
docker run -it --rm -v ".\output:/app/output" --name aip-extract aip-extract:latest
```

Please note that neither this repository nor the DockerHub image are actively managed. And sure, using ubuntu:24.04 results in a huge image, so I'm open for suggestions on that side.

## Performance
OCR processing runs on my personal machine at approx. 5 pages/second. The complete process for all ~1300 pages therefore takes about 20 to 30 minutes. As the script keeps most of the files in RAM one has to expect a high RAM usage as well as 100% CPU usage during the process.
