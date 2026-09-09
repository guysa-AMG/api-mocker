FROM astral/uv:python3.14-trixie

COPY . .

RUN uv sync

ENTRYPOINT [ "uv", "run", "fastapi", "run", "src/api_mocker/main.py"]
