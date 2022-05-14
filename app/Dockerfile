FROM python:3.10.0
ENV REFRESHED_AT 2014-07-01-5-49
ADD . /flask-deploy
WORKDIR /flask-deploy
RUN pip install -r requirements.txt
EXPOSE 5000
CMD gunicorn app:app --workers 2 --bind 0.0.0.0:5000 --timeout 800