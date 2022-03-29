FROM python:3.8.13-slim 

WORKDIR /usr/src/app

COPY requirements.txt ./


RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

ENTRYPOINT ["streamlit", "run"]
CMD ["frontend.py"]
EXPOSE 8501