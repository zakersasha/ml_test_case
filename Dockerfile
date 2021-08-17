FROM python:3.8
ADD . /ml_test_case
WORKDIR /ml_test_case
RUN pip install -r requirements.txt
CMD python app.py