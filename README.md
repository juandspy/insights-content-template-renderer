# insights-content-template-renderer

This service provides the endpoint for rendering the report messages based on the DoT.js templates from content data and report details.
For that purpose it uses the implementation of [DoT.js framework in Python](https://github.com/lucemia/doT).

## Running the service

The service can be run either locally:

`pip3 install -r requirements.txt && ./run.sh`

Or you can run the service as the Docker container. In that case make sure you have a Docker engine installed and running. Then you can create a Docker image with

`docker build -t insights-content-template-renderer .`

and create a Docker container via

`docker run -d --name renderer -p 8000:8000 insights-content-template-renderer`

## Endpoints

As said, the service has the single endpoint:

### [POST] /rendered-reports

The service takes JSON data as input in the format

```
{
	"content": ... data from content service endpoint /content ...
	"report-data": ... data from aggregator service endpint /clusters/{clusterIds}/reports ...
}
```

And returns the rendered reports.
