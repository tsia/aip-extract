FROM ubuntu:24.04

RUN apt update \
    && apt -y install ca-certificates

RUN sed -e 's/http:/https:/g' -i /etc/apt/sources.list /etc/apt/sources.list.d/*

RUN apt update \
    &&  apt -y install \
        tesseract-ocr \
        tesseract-ocr-deu \
        tesseract-ocr-eng \
        python3 \
        python3-pip \
        python3-venv \
        ghostscript \
        pngquant \
        unpaper \
        jbig2 \
    &&  apt clean \
    &&  apt autoremove

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv venv && ./venv/bin/pip3 install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY main.py .

CMD [ "./venv/bin/python3", "/app/main.py" ]
