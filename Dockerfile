FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV DB_HOST=postgres
ENV DB_USER=postgres
ENV DB_PASS=postgres
ENV DB_NAME=postgres
ENV DB_PORT=5432
ENV LOG_LEVEL=info

RUN apt-get update && apt-get install -y postgresql-client
COPY ./prestart.sh /app/prestart.sh
COPY ./start-reload.sh /start-reload.sh
COPY ./start.sh /start.sh
RUN chmod +x /app/prestart.sh /start-reload.sh /start.sh

COPY ./requirements.txt /app/requirements.txt
COPY ./alembic.ini /app/alembic.ini

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY app/ /app/app
COPY migrations /app/migrations

RUN mkdir /app/static
COPY ./userscript /app/static/userscript
