FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /app/

COPY ./app/requirements.txt /app/
RUN pip install -r requirements.txt

COPY ./app /app
ENV PYTHONPATH=/app
