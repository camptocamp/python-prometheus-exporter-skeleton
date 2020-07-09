# Python Prometheus exporter skeleton

A skeleton to build a prometheus exporter with [python library](https://github.com/prometheus/client_python).

## Prometheus overview

* [Overview](https://prometheus.io/docs/introduction/overview/#architecture)
* [Types of metrics](https://prometheus.io/docs/concepts/metric_types/)
* [Best pratices](https://prometheus.io/docs/practices/instrumentation/#counter-vs-gauge-summary-vs-histogram)

## Exporter

* Deamon with HTTP endpoint VS cron like script with pushgateway
* Libraries available for [several languages](https://prometheus.io/docs/instrumenting/clientlibs/)
* Exporter can be include in existing app or run a seperate app
* 4 ways to implements metrics:
  * `set()`, `inc()` method on metric object.
    [Example](https://github.com/camptocamp/python-prometheus-exporter-skeleton/blob/master/exporter/exporter.py#L30)
  * Using callback.
    [Example](https://github.com/camptocamp/python-prometheus-exporter-skeleton/blob/master/exporter/exporter.py#L15)
  * Usgin decorator.
    [Example](https://github.com/prometheus/client_python#three-step-demo)
  * Using a custom Collector.
    [Example](https://github.com/prometheus/client_python#custom-collectors)

## Test

Before deploying the exporter you need to test it. You can use a
docker composition to test exporter on workstation. You need:

  * promeheus
  * grafana
  * DB, ldap, minio, webserver or others componenents

Prometheus configuration is done with a [simple config
file](https://github.com/camptocamp/python-prometheus-exporter-skeleton/blob/master/docker/prometheus.yml).
This file is mounted at `/etc/prometheus/prometheus.yml`.

For grafana, you need to [setup datasource](https://github.com/camptocamp/python-prometheus-exporter-skeleton/blob/master/docker/grafana/datasource.yaml)
 and [dashboard discovery](https://github.com/camptocamp/python-prometheus-exporter-skeleton/blob/master/docker/grafana/dashboards.yaml).
Then you can mount [JSON dashboard](https://github.com/camptocamp/python-prometheus-exporter-skeleton/blob/master/docker/grafana/dashboard.json) at
`/var/lib/grafana/dashboards/`.

## Discovery of the new exporter

### Rancher

You need to add a labels on the service: `prometheus_port: '9351'`

```yaml
services:
  exporter:
    image: camptocamp/exporter
    environment:
      APP_URL: http://app/
      EXPORTER_PORT: 9351
    labels:
      io.rancher.scheduler.affinity:host_label: monitoring=true
      prometheus_port: '9351'
```

### Kubernetes

If the [prometheus exporter](https://github.com/coreos/prometheus-operator)
is installed, you need to either deploy a [ServiceMonitor](https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#servicemonitor) or a [PodMonitor](https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#podmonitor):

* `ServiceMonitor` monitor `Endpoints` associated to a Service. Should be named `EndpointsMonitor`. You can use if you have a `Service`.
* `Podmonitor` monitor `Pod`. Use this one if you don't have a `Service` in front of the Pods.

Both object use label selector to find `Pods` or `Endpoints`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: example-app
  labels:
    team: frontend
spec:
  selector:
    matchLabels:
      app: example-app
  endpoints:
  - port: web
```

## Alerting

With the Prometheus operator, you can define alerts based on your new metrics. The [PrometheusRule](https://github.com/coreos/prometheus-operator/blob/master/Documentation/api.md#prometheusrule) object is used to define:

* Alerts: condition on metrics, if true is trigger an alert.
* Recording rules: generate new metrics based on existing metrics.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: prometheus-postgres-backup
spec:
  groups:
  - name: backup
    rules:
      # pghoard
    - record: infra_federation:postgres_backup_last_upload
      expr: time() - pghoard_last_upload_age
    - record: infra_federation:postgres_backup_last_upload_age
      expr: pghoard_last_upload_age
      # wal-g
    - record: infra_federation:postgres_backup_last_upload
      expr: walg_last_upload
    - record: infra_federation:postgres_backup_last_upload_age
      expr: time() - walg_last_upload
  - name: postgres_alerts
    rules:
    - alert: LastBackup
      annotations:
        summary: Last backup is too old
      expr: |
        (time() - (infra_federation:postgres_backup_last_upload)) / 3600 > 24
      for: 1h
      labels:
        severity: critical
```

* `for` can be used to define some tolerance: `last_backup > 25h` VS `last_backup > 24h for 1h`
* Compare something that is human readable : hours instead of seconds.
 Change unit before comparing. Help to understand alerts: 25.13242 VS 90476
