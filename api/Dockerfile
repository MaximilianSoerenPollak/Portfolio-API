FROM tiangolo/uvicorn-gunicorn:python3.8-slim

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN \
    apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

CMD ["sh", "-c", "alembic upgrade head ; uvicorn main:app --host 0.0.0.0 --port 8000"]
# ENTRYPOINT ["bash", "/usr/src/app/entrypoint.sh"]
EXPOSE 8000