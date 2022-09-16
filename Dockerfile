FROM registry.access.redhat.com/ubi8/python-39:1-73 

WORKDIR /insights-content-template-renderer

COPY . /insights-content-template-renderer
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install .

EXPOSE 8000

CMD ["insights-content-template-renderer", "--config", "docker_config.yml"]
