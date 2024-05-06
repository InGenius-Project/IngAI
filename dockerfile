FROM python:3.11.9-alpine3.19

COPY . /app
WORKDIR /app
RUN apk update
RUN apk --no-cache add curl gnupg
COPY "mssql-bundle/*" .

RUN curl https://packages.microsoft.com/keys/microsoft.asc  | gpg --import -
RUN gpg --verify msodbcsql18_18.3.3.1-1_amd64.sig msodbcsql18_18.3.3.1-1_amd64.apk
RUN gpg --verify mssql-tools18_18.3.1.1-1_amd64.sig mssql-tools18_18.3.1.1-1_amd64.apk

#Install the package(s)
RUN apk add --allow-untrusted msodbcsql18_18.3.3.1-1_amd64.apk
RUN apk add --allow-untrusted mssql-tools18_18.3.1.1-1_amd64.apk

USER root
RUN chmod 777 -R /opt/microsoft/msodbcsql18/

RUN apk add gcc libc-dev g++ libffi-dev libxml2 unixodbc-dev openssl
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install --no-cache-dir -r requirements.txt

ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["python3", "main.py"] 