FROM python:3.6.6

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY app/ ./app/

COPY app_main.py ./app_main.py

COPY startup.sh ./startup.sh
RUN chmod 777 ./startup.sh && \
    sed -i 's/\r//' ./startup.sh

COPY VERSION ./VERSION

COPY case_28.zip ./case_28.zip
COPY case_35.zip ./case_35.zip
COPY case_43.zip ./case_43.zip
COPY case_50.zip ./case_50.zip
COPY case_58.zip ./case_58.zip

EXPOSE 5000

CMD ["./startup.sh"]
