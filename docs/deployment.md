# Deployment

## Testing the local version of the service in ephemeral

[demo](https://asciinema.org/a/uMQESE4ay2ok7oQWr04slhuWw)

1. Install `bonfire`
```
❯ pip install crc-bonfire
```

2. Log into https://console-openshift-console.apps.c-rh-c-eph.8p0c.p1.openshiftapps.com/k8s/cluster/projects

```
❯ oc login --token=${TOKEN} --server=https://api.c-rh-c-eph.8p0c.p1.openshiftapps.com:6443
```

3. Reserve a namespace
```
❯ NAMESPACE=$(bonfire namespace reserve)
2022-09-15 16:17:08 [    INFO] [          MainThread] Attempting to reserve a namespace...
2022-09-15 16:17:09 [    INFO] [          MainThread] Checking for existing reservations for '{USER}'
2022-09-15 16:17:10 [    INFO] [          MainThread] processing namespace reservation
2022-09-15 16:17:10 [    INFO] [          MainThread] running (pid 62954): oc apply -f - 
2022-09-15 16:17:13 [    INFO] [           pid-62954]  |stdout| namespacereservation.cloud.redhat.com/bonfire-reservation-233828c7 created
2022-09-15 16:17:13 [    INFO] [          MainThread] waiting for reservation 'bonfire-reservation-233828c7' to get picked up by operator
2022-09-15 16:17:13 [    INFO] [          MainThread] namespace '{NAMESPACE}' is reserved by '{USER}' for '1h' from the default pool
2022-09-15 16:17:14 [    INFO] [          MainThread] namespace console url: https://console-openshift-console.apps.c-rh-c-eph.8p0c.p1.openshiftapps.com/k8s/cluster/projects/{NAMESPACE}
```

4. Deploy the renderer
```
bonfire deploy -c deploy/test.yaml -n $NAMESPACE insights-content-template-renderer
```

5. Make a request to the renderer
```
oc --namespace $NAMESPACE run curl -i --rm \
    --image=docker.io/curlimages/curl:latest  \
    --command -- sh -c "
        echo '[INFO] Downloading jq' && \
        wget -O /tmp/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 2>/dev/null && \
        chmod +x /tmp/jq && \
        echo '[INFO] Downloading a request data example' && \
        curl -s https://raw.githubusercontent.com/RedHatInsights/insights-content-template-renderer/main/insights_content_template_renderer/tests/request_data_example.json > /tmp/req.json && \
        echo '[INFO] Testing the service' && \
        curl -s -X POST -H 'Content-Type: application/json' -d @/tmp/req.json insights-content-template-renderer-svc:8000/rendered_reports | /tmp/jq && \
        echo '' && \
        echo '[INFO] Testing finished'
    "
```

You should see the generated report.

6. Delete the namespace
```
bonfire namespace release $NAMESPACE 
```
