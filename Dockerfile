FROM python:3.12
MAINTAINER Maximilian Thoma
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app .
EXPOSE 2222
CMD ["gunicorn", "--bind", "0.0.0.0:2222", "--access-logfile", "-", "--error-logfile", "-", "app:app"]