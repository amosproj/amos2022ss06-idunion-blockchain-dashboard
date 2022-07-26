FROM bcgovimages/von-image:next-1

RUN pip install pynacl

ADD fetch_status_prometheus.py .
ADD networks.json .

ENTRYPOINT ["bash", "-c", "python3 fetch_status_prometheus.py $@", "--"]
