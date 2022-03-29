FROM python:3.8.13-slim AS builder

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN \
    apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .


CMD ["until pg_isready -q -h postgres; do sleep 1; done"]
RUN ["alembic", "upgrade", "head"]
RUN ["uvicorn" ,"main:app" ,"--host" ,"0.0.0.0" ,"--port" ,"8000"]
# ENTRYPOINT ["bash", "/usr/src/app/entrypoint.sh"]
EXPOSE 8000