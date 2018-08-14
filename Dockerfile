FROM python:3

ADD . /

RUN pip install flask
RUN pip install pycrypto
RUN pip install flask_cors
RUN pip install requests

CMD ["python", "webnode.py"]
