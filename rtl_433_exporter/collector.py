import threading
import time

import prometheus_client.core


class RTL433Collector(object):

    def __init__(self, events=None, labels=None, persist=None):
        self.events = events
        self.labels = set(labels or ())
        self.persist = float(persist or 0)
        self._prefix = "rtl_433_"
        self._lock = threading.RLock()
        self._events = []

        self.labels.update([
            "id", "sensor_id", "protocol", "type", "brand", "model", "subtype",
            "channel"])

    def add_event(self, event):
        with self._lock:
            self._events.append(event)

    def expire(self, t):
        def expired(event):
            return event["time"] + self.persist < t
        with self._lock:
            self._events = [e for e in self._events if not expired(e)]

    def make_metric(self, _name, _documentation, _value,
                    **_labels):
        cls = prometheus_client.core.GaugeMetricFamily
        label_names = list(_labels.keys())
        metric = cls(
            self._prefix + _name, _documentation or "No Documentation",
            labels=label_names)
        metric.add_metric([str(_labels[k]) for k in label_names], _value)
        return metric

    def event_to_metrics(self, event):
        labels = {}
        metrics = {}
        for k, v in event.items():
            if k in ("time",):
                continue
            if not isinstance(v, (int, float, str)):
                continue
            if k in self.labels or isinstance(v, str):
                labels[k] = str(v)
            else:
                metrics[k] = v
        for k, v in metrics.items():
            yield (k, tuple(sorted(labels.items()))), v

    def _collect_locked(self):
        self.expire(time.time())
        deduped = {}
        events = sorted(self._events, key=lambda e: e.get("time"))
        for event in events:
            for k, v in self.event_to_metrics(event):
                deduped[k] = v
        for k, v in deduped.items():
            name, label_items = k
            labels = dict(label_items)
            yield self.make_metric(name, None, v, **labels)

    def collect(self):
        with self._lock:
            return list(self._collect_locked())
