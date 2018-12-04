# First stage of multi-stage build: building wheels
FROM python:3.6-alpine as python-base
COPY requirements.txt .
# postgresql-dev required to build psycopg2 with pip
RUN set -eux; \
    apk add --no-cache \
	  linux-headers \
      ca-certificates \
      build-base \
      libxml2-dev \
      libxslt-dev \
      postgresql-dev \
      su-exec \
      xmlsec-dev

RUN pip wheel -r requirements.txt --wheel-dir=/tmp/wheels/


# Final stage of multi-stage build: the app itself
FROM python:3.6-alpine
# Copy over our compiled packages into the image
COPY --from=python-base /tmp/wheels /tmp/wheels

# Simplified installation
RUN set -eux; \
	chmod 777 -R /tmp/wheels; \
    mkdir -p /app; \
    mkdir -p /usr/src/static; \
    mkdir -p /app/logs; \
    addgroup -g 1000 app; \
    adduser -D -G app -u 1000 app; \
    chown app:app /app /usr/src/static /app/logs

USER app
WORKDIR /app

ENV PATH="/home/app/.local/bin:$PATH"

COPY requirements.txt /app/
# TODO: See if we can copy the installed python packages from first stage to this one 
#		without dealing with any wheels at all besides in the first stage
RUN pip install --user --no-index --no-cache -r requirements.txt --find-links=/tmp/wheels/

COPY . /app
COPY container/start.sh /start.sh

EXPOSE 8000

CMD ["/start.sh"]

