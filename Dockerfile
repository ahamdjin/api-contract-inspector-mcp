FROM golang:1.25 AS oasdiff-build
RUN go install github.com/oasdiff/oasdiff@v1.34.0

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=oasdiff-build /go/bin/oasdiff /usr/local/bin/oasdiff
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN pip install --no-cache-dir . && useradd --system --no-create-home --shell /usr/sbin/nologin inspector
USER inspector
ENTRYPOINT ["api-contract-inspector-mcp"]
