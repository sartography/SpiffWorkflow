FROM python:2-wheezy
RUN apt-get -y update && apt-get upgrade -yu
COPY . /tmp/SpiffWorkflow
RUN cd /tmp/SpiffWorkflow && make wheel && pip install dist/SpiffWorkflow*.whl
