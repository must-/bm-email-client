FROM ubuntu:14.04 # TODO use a smaller base image

RUN locale-gen --no-purge en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8
RUN update-locale
ENV DEBIAN_FRONTEND noninteractive

RUN add-apt-repository ppa:fuzzgun/pybitmessage
RUN apt-get -y update
RUN apt-get -y upgrade

RUN apt-get install pybitmessage # TODO split into separate container

RUN git clone https://github.com/must-/bmwrapper.git
CD bmwrapper
ADD . /bm-email-client

# forward logs to docker log collector
RUN ln -sf /dev/stdout /var/log/pybitmessage.log
RUN ln -sf /dev/stdout /var/log/bmwrapper.log

ENV bm_api_username bmwrapper
ENV bm_api_password placeholder
RUN echo "daemon = true\n"+\
    "apienabled = true\n"+\
    "apiinterface = 127.0.0.1\n"+\
    "apiport = 8442\n"+\
    "apiusername = $bm_api_username\n"+\
    "apipassword = $bm_api_password\n"\
    >>  ~/.config/PyBitmessage/keys.dat
RUN pybitmessage >/var/log/pybitmessage.log 2>&1 &

WORKDIR /bmwrapper

ENTRYPOINT ["bash bmwrapper.sh >/var/log/bmwrapper.log "]
CMD []