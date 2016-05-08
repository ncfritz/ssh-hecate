FROM python:2.7-alpine

MAINTAINER ncfritz@ncfritz.net

# Install git
RUN apk --update add \
    git \
    gcc \
    g++ \
    make \
    libffi-dev \
    openssl-dev

# Clone our source and install the 3P Python libraries we need
RUN mkdir -p /hecate
RUN git clone https://github.com/ncfritz/ssh-hecate.git /hecate
RUN pip install -r /hecate/requirements.txt

WORKDIR /hecate
ENTRYPOINT ["./bin/hecate-invoker"]