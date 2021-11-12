FROM python:3.10-alpine

WORKDIR /usr/src/app
COPY requirements.txt .
RUN apk update && \
    apk add ffmpeg && \
    pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python","-m", "bot"]