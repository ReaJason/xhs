FROM --platform=$TARGETPLATFORM mcr.microsoft.com/playwright/python:v1.38.0-jammy

LABEL authors="ReaJason"
LABEL mail="reajason1225@gmail.com"

WORKDIR /app
COPY app.py .

RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl


# reference -> https://playwright.dev/python/docs/ci#via-containers
RUN python -m pip install --upgrade pip \
    && pip install Flask gevent xhs playwright \
    && rm -rf /var/lib/apt/lists/*ç

RUN curl --insecure -L -o stealth.min.js  https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js

EXPOSE 5005

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5005"]
