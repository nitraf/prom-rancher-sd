# Prometheus-Rancher Service Discovery Bridge

## Forked from [DanielDent/prom-rancher-sd](https://github.com/DanielDent/prom-rancher-sd) - all credit to Daniel Dent

This utility was created to integrate prometheus monitoring to application & node_exporter running in Docker containers.
prom-rancher-sd polls [Rancher's metadata service](http://docs.rancher.com/rancher/metadata-service/) By default it generates config for services. In order to filter service name you can use **JOB_REGEX** environment variable. It supports regular expressions.

A configuration file suitable for use by [Prometheus](http://prometheus.io/) is written to enable services to be monitored automatically. Configuration file name is `rancher.json`. Here is and example of generated file:

```json
[
  {
    "targets": [
      "10.42.24.234:8085"
    ],
    "labels": {
      "instance": "stretch",
      "__metrics_path__": "/metrics",
      "__meta_rancher_container_name": "test-stack-test-nginx-1",
      "__meta_rancher_service_name": "test-nginx",
      "__meta_rancher_stack": "test-stack",
      "__meta_rancher_job_name": "stack-nginx"
    }
  }
]
```

The configuration file will be written to the directory /prom-rancher-sd-data by default, use the **OUTPUT_FOLDER** environment variable to change the directory.

Interval that specifies how often the discovery process is repeated by default set to 5. Set **DISCOVERY_TIME** environment variable to chanage this setting.

Log level could be set via **LOGLEVEL** environment variable. Value of this variable could be INFO,WARN,DEBUG and so on.

I changed a bit the cowhand approach by enriching the labels and assigning some sensible defaults.

One application running in container will be published in Prom configuration if it has the `com.prometheus.monitoring` label set to `true`.

Prometheus will scrape `/metrics` (default value) or the value specified by `com.prometheus.metricspath` label via HTTP by connecting to the container's primary IP on the 8083 port (default) or on the port specified by the `com.prometheus.port` label.

The [Let it Crash](http://c2.com/cgi/wiki?LetItCrash) design used implies that this software should be operated under a process supervisor. Docker and Rancher's automatic container restart facilities are believed adequate.

## License

Copyright 2016 [Daniel Dent](https://www.danieldent.com/).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use these files except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Third-party contents included in builds of the image are licensed separately.
