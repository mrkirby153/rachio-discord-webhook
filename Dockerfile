FROM python:3.10-alpine as base

WORKDIR /app

FROM base as builder

RUN apk add --no-cache gcc libffi-dev musl-dev

RUN pip install poetry
RUN python -m venv /venv

COPY poetry.lock pyproject.toml ./

RUN poetry export -f requirements.txt --without dev | /venv/bin/pip install -r /dev/stdin

COPY . .
RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base as app

RUN apk add --no-cache libffi libpq
COPY --from=builder /venv /venv

COPY docker-entrypoint.sh wsgi.py manage.py ./
CMD ["./docker-entrypoint.sh"]