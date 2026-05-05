FROM python:3.13-slim-bullseye

ARG UNAME=appuser
ARG UID=1200
ARG GID=1200
ARG VERSION=latest
ARG APPLICATION_MANUFACTURER=test_repo
ARG OPENFACTORY_VERSION=latest

LABEL openfactory.version="${OPENFACTORY_VERSION}" \
      application.version="${VERSION}" \
      source.repository="${APPLICATION_MANUFACTURER}"

RUN adduser --uid ${UID} --disabled-password --gecos "" ${UNAME}

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

RUN if [ "$OPENFACTORY_VERSION" = "latest" ]; then \
      pip install git+https://github.com/Demo-Smart-Factory-Concordia-University/OpenFactory.git ; \
    else \
      pip install git+https://github.com/Demo-Smart-Factory-Concordia-University/OpenFactory.git@$OPENFACTORY_VERSION ; \
    fi
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ENV APPLICATION_VERSION=${VERSION}
ENV APPLICATION_MANUFACTURER=${APPLICATION_MANUFACTURER}

WORKDIR /ofa
COPY wtvb01_spectrogram.py /ofa
COPY kafka_processor.py /ofa
COPY signal_processor.py /ofa
COPY spectrogram.sql /ofa
COPY spectrogram_cleanup.sql /ofa
RUN chown -R appuser:appuser /ofa

USER ${UNAME}
CMD ["python3", "-u", "/ofa/wtvb01_spectrogram.py"]