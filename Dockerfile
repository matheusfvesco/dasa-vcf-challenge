FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY pyproject.toml .
COPY .python-version .
COPY uv.lock .

COPY Snakefile .

COPY src .

RUN apt update \
    && apt install -y gcc \
    && rm -rf /var/lib/apt/lists/* \
    && uv sync \
    && uv clean

CMD ["uv", "run", "snakemake"]