FROM python:3.11-slim-bookworm as requirements-stage

RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock /
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without=dev

FROM python:3.11-slim-bookworm

COPY --from=requirements-stage /requirements.txt /requirements.txt
COPY ./pyproject.toml ./gunicorn_conf.py /
COPY ./app /app

RUN python3 -m pip install --no-cache-dir --upgrade -r requirements.txt

RUN mkdir -p /tmp/shm && mkdir /.local

ENV PORT 8000
EXPOSE 8000

ENTRYPOINT ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn_conf.py", "app.main:app"]
