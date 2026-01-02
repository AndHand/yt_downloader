FROM python:3.13
WORKDIR /usr/local

COPY ./YT_Downloader/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./YT_Downloader ./app/YT_Downloader
COPY ./shared ./app/shared
COPY ./.env.docker ./app/YT_Downloader/.env
EXPOSE 8000

ENV PYTHONPATH=/usr/local/app

RUN useradd web
USER web

CMD ["python", "./app/YT_Downloader/manage.py", "runserver", "0.0.0.0:8000"]