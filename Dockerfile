FROM python:3

ENV APP /app

RUN mkdir $APP
WORKDIR $APP

COPY requirements.txt .
RUN pip install -r requirements.txt

# Rest of codebase as this will change frequently, whereas the Python modules
# will not
COPY . .

EXPOSE 5000
ENTRYPOINT ["python", "./web-app.py"]
