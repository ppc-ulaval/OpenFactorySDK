FROM ubuntu:latest
LABEL author="Rolf Wuthrich" 
LABEL organisation="Concordia University"
LABEL description="Docker image for OpenFactory Virtual CNC"
LABEL documentation="https://github.com/Demo-Smart-Factory-Concordia-University/OpenFactory-SDK"

ARG UNAME=ofa
ARG UID=1200
ARG GID=1200

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update
RUN apt-get -y install python3 python3-pip python3-venv git

RUN groupadd --gid $GID $UNAME
RUN useradd --create-home --uid $UID --gid $GID $UNAME

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# python dependencies
RUN pip install git+https://github.com/Demo-Smart-Factory-Concordia-University/MTCAdapters.git
RUN pip install asyncua

WORKDIR /home/$UNAME
USER $UNAME

COPY adapter.py .

CMD ["python3", "-u", "adapter.py"]