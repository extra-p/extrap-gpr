FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y python3

wget https://zenodo.org/records/10085298/files/fastest.tar.gz

wget https://zenodo.org/records/10086772/files/extrap.zip
