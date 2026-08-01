from __future__ import annotations

import hmac
import json
import os
from pathlib import Path

from flask import Flask, jsonify, request

from .models import EventValidationError, ForwardEvent


class Publisher:
    def publish(self, payload: dict) -> None:
        project = os.getenv("GOOGLE_CLOUD_PROJECT")
        topic = os.getenv("PUBSUB_TOPIC")
        if project and topic:
            from google.cloud import pubsub_v1

            client = pubsub_v1.PublisherClient()
            topic_path = client.topic_path(project, topic)
            client.publish(
                topic_path,
                json.dumps(payload).encode("utf-8"),
            ).result(timeout=2)
            return

        spool = Path(os.getenv("LOCAL_SPOOL_PATH", "/tmp/forward_events.jsonl"))
        spool.parent.mkdir(parents=True, exist_ok=True)
        with spool.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, separators=(",", ":")) + "\n")


def create_app() -> Flask:
    app = Flask(__name__)
    publisher = Publisher()

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok", "schema": "FTL_V2"})

    @app.post("/webhook")
    def webhook():
        expected = os.getenv("WEBHOOK_SHARED_TOKEN", "")
        supplied = request.args.get("token", "")
        if expected and not hmac.compare_digest(expected, supplied):
            return jsonify({"status": "rejected", "reason": "unauthorized"}), 401

        value = request.get_json(silent=True)
        if not isinstance(value, dict):
            return jsonify({"status": "rejected", "reason": "invalid_json"}), 400
        value.pop("auth_token", None)

        try:
            event = ForwardEvent.from_mapping(value)
            publisher.publish(event.to_dict())
        except EventValidationError as exc:
            return jsonify({"status": "rejected", "reason": str(exc)}), 422
        except Exception:
            app.logger.exception("publish failed")
            return jsonify({"status": "retry", "reason": "queue_unavailable"}), 503

        return jsonify({"status": "accepted", "event_id": event.event_id}), 202

    return app


app = create_app()
