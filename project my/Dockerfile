FROM python:3.6-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN touch debug.txt
RUN chmod 777 debug.txt
RUN chmod 777 script.sh
# ENTRYPOINT [ "python", "-u", "runner.py" ]
CMD bash script.sh