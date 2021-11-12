FROM python:3.9

WORKDIR /insights-content-template-renderer

COPY ./requirements.txt /insights-content-template-renderer/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /insights-content-template-renderer

EXPOSE 8000

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--pythonpath", "app", "main:app"]
