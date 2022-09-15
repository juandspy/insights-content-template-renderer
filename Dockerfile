FROM registry.access.redhat.com/ubi8/python-39:1-73 

WORKDIR /insights-content-template-renderer

COPY ./requirements.txt /insights-content-template-renderer/requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /insights-content-template-renderer
RUN pip install .

EXPOSE 8000

CMD ["insights-content-template-renderer", "--config", "docker_config.yml"]
