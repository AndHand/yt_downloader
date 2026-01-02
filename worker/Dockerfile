FROM python:3.13
WORKDIR /usr/local

RUN apt-get -y update
RUN apt-get -y install ffmpeg

COPY ./worker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./worker ./app/worker
COPY ./shared ./app/shared
COPY ./.env.docker ./app/worker/.env

RUN useradd worker
RUN mkdir -p ./app/data
RUN chown -R worker:worker ./app
RUN chmod -R 755 ./app

ENV PYTHONPATH=/usr/local/app

USER worker

CMD ["python", "-u", "app/worker/worker.py"]