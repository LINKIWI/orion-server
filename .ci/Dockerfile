FROM docker.internal.kevinlin.info/infra/ci-base:0.1.1

RUN sudo apt-get update && sudo apt-get install -y python-dev libmysqlclient-dev

COPY sample-config.json /etc/orion/config.json
