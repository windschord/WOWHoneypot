FROM python:3.8.1

COPY ./ /usr/src/WOWHoneypot/

RUN apt-get update &&\
    apt-get upgrade -y &&\
    apt-get clean &&\
    rm -rf /var/lib/apt/lists/* &&\
    pip install -r /usr/src/WOWHoneypot/requirements.txt

WORKDIR /usr/src/WOWHoneypot
ENTRYPOINT ["/usr/local/bin/python"]
CMD ["wowhoneypot.py"]