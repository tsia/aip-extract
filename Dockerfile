FROM ubuntu:22.10
RUN apt-get update \
    && apt-get install tesseract-ocr \
    python3 \
    python3-pip \
	ghostscript \
	pngquant \
	unpaper \
    -y \	
    && apt-get clean \
    && apt-get autoremove

ADD . /home/App
WORKDIR /home/App

COPY requirements.txt ./

RUN pip3  install --no-cache-dir -r requirements.txt
RUN PATH=""
COPY . .

CMD [ "python3", "./main.py" ]
