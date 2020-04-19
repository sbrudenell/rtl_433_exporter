FROM ubuntu:rolling

RUN apt-get update && \
    apt-get install -y rtl-433 python3-pip

COPY . /src

RUN pip3 install --upgrade /src

COPY run.sh /run.sh

EXPOSE 9433

ENTRYPOINT ["/run.sh"]
