FROM python:2.7.11

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -yq \
    libmemcached-dev \
    build-essential \
    libffi-dev \
    python-dev \
    nano

run apt-get install --force-yes -yq libssl-dev=1.0.1k-3+deb8u5 libssl1.0.0=1.0.1k-3+deb8u5 openssl=1.0.1k-3+deb8u5

ADD . /datadrivendota

WORKDIR /datadrivendota

RUN pip install -r requirements/local.txt

CMD ['/bin/bash']
