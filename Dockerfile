FROM ubuntu:24.04

RUN apt-get update \
    &&  apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-deu \
        python3 \
        python3-pip \
        ghostscript \
        pngquant \
        unpaper \
        jbig2 \
    &&  apt-get clean \
    &&  apt-get autoremove

WORKDIR /app
COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

COPY main.py .

CMD [ "python3", "/app/main.py" ]
