FROM python:3.9-slim-buster

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

WORKDIR /app

COPY . /app

ENV FLASK_APP=app/main.py
ENV FLASK_ENV=development

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
