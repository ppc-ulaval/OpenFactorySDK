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
      pip install git+https://github.com/openfactoryio/openfactory-core.git ; \
    else \
      pip install git+https://github.com/openfactoryio/openfactory-core.git@$OPENFACTORY_VERSION ; \
    fi

ENV APPLICATION_VERSION=${VERSION}
ENV APPLICATION_MANUFACTURER=${APPLICATION_MANUFACTURER}

WORKDIR /ofa
COPY tool_monitoring.py /ofa
COPY usage_duration.sql /ofa
COPY system_health.sql /ofa
COPY cleanup.sql /ofa
RUN chown -R appuser:appuser /ofa

USER ${UNAME}
CMD ["python3", "-u", "/ofa/tool_monitoring.py"]