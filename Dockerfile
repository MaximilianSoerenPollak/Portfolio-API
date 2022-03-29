FROM python:3.8.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD bash -c "alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port 8000"
