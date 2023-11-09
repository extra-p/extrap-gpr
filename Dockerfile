FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get upgrade -y

# install python
RUN apt-get install -y python3-pip

# install wget
RUN apt-get install -y wget

# install git
RUN apt-get install -y git

# install unzip
RUN apt-get install -y unzip

# clone github repo with analysis scripts
RUN git clone https://github.com/extra-p/extrap-gpr.git

# download the extra-p version used for the evaluation
RUN wget https://zenodo.org/records/10086772/files/extrap.zip

# install extra-p
RUN unzip extrap.zip -d extrap
RUN pip install -e extrap/extrap-vNext/
RUN rm extrap.zip

# install custom pycubexr version
RUN wget https://zenodo.org/records/10092353/files/pycubexr-master.zip
RUN unzip pycubexr-master.zip -d pycubexr
RUN pip install -e pycubexr/pycubexr-master/
RUN rm pycubexr-master.zip

# download the performance measurement datasets
RUN wget https://zenodo.org/records/10085298/files/fastest.tar.gz
RUN wget https://zenodo.org/records/10085298/files/kripke.tar.gz
RUN wget https://zenodo.org/records/10085298/files/lulesh.tar.gz
RUN wget https://zenodo.org/records/10085298/files/minife.tar.gz
RUN wget https://zenodo.org/records/10085298/files/quicksilver.tar.gz
RUN wget https://zenodo.org/records/10085298/files/relearn.tar.gz
RUN tar -xzf fastest.tar.gz
RUN tar -xzf kripke.tar.gz
RUN tar -xzf lulesh.tar.gz
RUN tar -xzf minife.tar.gz
RUN tar -xzf quicksilver.tar.gz
RUN tar -xzf relearn.tar.gz
RUN rm fastest.tar.gz kripke.tar.gz lulesh.tar.gz minife.tar.gz quicksilver.tar.gz relearn.tar.gz

# install pip package dependencies
RUN pip install sympy
RUN pip install scikit-learn
RUN pip install natsort
RUN pip install pandas

# install latex dependency for plot creation
RUN apt-get install -y texlive texlive-latex-extra texlive-fonts-recommended dvipng
RUN apt-get install -y cm-super
RUN pip install latex
