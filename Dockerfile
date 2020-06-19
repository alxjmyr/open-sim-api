from python:3.7

COPY ./src /app/src
COPY ./setup.py /app/setup.py
WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -e .

EXPOSE 80

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]