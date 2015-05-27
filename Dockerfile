FROM debian:8

RUN locale-gen --no-purge en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:fuzzgun/pybitmessage
RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-get install pybitmessage # TODO split into separate container

RUN git clone https://github.com/must-/bmwrapper.git
CD bmwrapper
ADD . /bmwrapper

# forward logs to docker log collector
RUN ln -sf /dev/stdout /var/log/pybitmessage.log
RUN ln -sf /dev/stdout /var/log/bmwrapper.log

ENV bm_api_host 0.0.0.0
ENV bm_api_port 8442
ENV bm_api_username bm-user
ENV bm_api_password placeholder

RUN echo "daemon = true\n"+\
    "apienabled = true\n"+\
    "apiinterface = $bm_api_host\n"+\
    "apiport = $bm_api_port\n"+\
    "apiusername = $bm_api_username\n"+\
    "apipassword = $bm_api_password\n"\
    >>  ~/.config/PyBitmessage/keys.dat

EXPOSE 8444

RUN pybitmessage >/var/log/pybitmessage.log 2>&1 &

ENV pop_port 12344
ENV smtp_port 12345

EXPOSE pop_port
EXPOSE smtp_port

WORKDIR /bmwrapper

CMD ["-l info"]

ENTRYPOINT ["bash bmwrapper.sh >/var/log/bmwrapper.log "]