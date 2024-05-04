FROM python:3.11.9-alpine3.19

WORKDIR /app
COPY . /app
RUN apk update
RUN apk add gcc libc-dev g++ libffi-dev libxml2 unixodbc-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install --no-cache-dir -r requirements.txt

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["python3", "main.py"] 