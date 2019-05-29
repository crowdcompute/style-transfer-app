FROM tensorflow/tensorflow

EXPOSE 3000

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    git \
    python-pil \
    python-scipy \
    python-numpy \
    ffmpeg \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

# Libraries for style transfer app
RUN pip install \
    transform \
    moviepy

# Downloads the git code 
RUN cd / && \
    git clone https://github.com/lengstrom/fast-style-transfer.git /style-transfer-app

# For the web app
RUN pip install flask-restful \
                imagehash

WORKDIR /style-transfer-app/

COPY ["checkpoint", "checkpoint"]
COPY style_transfer.py style_transfer.py

ENTRYPOINT ["python","style_transfer.py"]