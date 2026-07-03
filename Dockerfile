FROM python:3.7-bullseye

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Node.js and pnpm
RUN curl -L https://raw.githubusercontent.com/tj/n/master/bin/n -o /tmp/n \
    && bash /tmp/n 18 \
    && npm -g install pnpm \
    && rm -f /tmp/n

# Install Poetry
RUN pip install --no-cache-dir "poetry==1.5.1"

# Python dependency cache
COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Frontend dependency cache
COPY pinry-spa/package.json /app/pinry-spa/package.json

RUN cd /app/pinry-spa \
    && pnpm install --no-frozen-lockfile

# Copy full source
COPY . /app

# Build Vue SPA
RUN cd /app/pinry-spa \
    && pnpm build

EXPOSE 80

CMD ["sh", "-lc", "python manage.py migrate --noinput || true; python manage.py collectstatic --noinput || true; python manage.py runserver 0.0.0.0:80"]
