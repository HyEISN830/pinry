FROM node:18-bookworm-slim AS frontend-build

WORKDIR /app/pinry-spa

RUN npm install -g pnpm

COPY pinry-spa/package.json pinry-spa/pnpm-lock.yaml ./

RUN pnpm install --frozen-lockfile

COPY pinry-spa ./

RUN pnpm build


FROM python:3.7-bullseye

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Poetry and Python runtime dependencies. Keep this before COPY . so
# Docker can reuse dependency layers when only application code changes.
RUN pip install --no-cache-dir "poetry==1.5.1"

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main \
    && pip install --no-cache-dir "django-extensions==3.1.5" \
    && rm -rf /root/.cache/pypoetry /root/.cache/pip

COPY . /app

COPY --from=frontend-build /app/pinry/static/spa /app/pinry/static/spa
COPY --from=frontend-build /app/pinry/templates/index.html /app/pinry/templates/index.html

EXPOSE 80

CMD ["sh", "-lc", "python manage.py migrate --noinput || true; python manage.py collectstatic --noinput || true; python manage.py runserver 0.0.0.0:80"]
