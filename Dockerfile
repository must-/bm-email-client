FROM must/pybitmessage # TODO: split into two containers, connecting to API over tcp

RUN locale-gen --no-purge en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -y update
RUN apt-get -y upgrade

RUN git clone https://github.com/must-/bmwrapper.git
CD bmwrapper
ADD . /bmwrapper

# forward logs to docker log collector
RUN ln -sf /dev/stdout /var/log/bmwrapper.log

ENV pop_port 12344
ENV smtp_port 12345

EXPOSE pop_port
EXPOSE smtp_port

WORKDIR /bmwrapper

CMD ["-l info"]

ENTRYPOINT ["bash bmwrapper.sh >/var/log/bmwrapper.log "]