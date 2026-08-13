# tests/test_app.py

import os
import unittest
from unittest.mock import MagicMock, patch

os.environ["TESTING"] = "true"

from app import app, TimelinePost  # noqa: E402


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        TimelinePost.delete().execute()

    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>Huzaifa Fareed</title>" in html
        assert "MLH Production Engineering Fellow" in html
        assert "About Me" in html
        assert "Education" in html
        assert "Work Experience" in html
        assert "Concordia University" in html
        assert "Places I've Visited" in html

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        json = response.get_json()
        assert "timeline_posts" in json
        assert len(json["timeline_posts"]) == 0

        post_response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "content": "Hello world, I'm John!",
            },
        )
        assert post_response.status_code == 200
        assert post_response.is_json
        created = post_response.get_json()
        assert created["name"] == "John Doe"
        assert created["email"] == "john@example.com"
        assert created["content"] == "Hello world, I'm John!"
        assert "id" in created

        response = self.client.get("/api/timeline_post")
        json = response.get_json()
        assert len(json["timeline_posts"]) == 1
        assert json["timeline_posts"][0]["name"] == "John Doe"

        page_response = self.client.get("/timeline")
        assert page_response.status_code == 200
        page_html = page_response.get_data(as_text=True)
        assert "Timeline" in page_html
        assert 'id="timeline-form"' in page_html

    def test_health(self):
        # NGINX_STATUS_URL is patched rather than read from the environment so
        # this passes both locally and inside the production container.
        with patch("app.NGINX_STATUS_URL", None):
            response = self.client.get("/health")

        assert response.status_code == 200
        assert response.is_json
        payload = response.get_json()
        assert payload["status"] == "ok"
        assert payload["checks"]["database"]["status"] == "ok"
        assert payload["checks"]["database"]["timeline_posts"] == 0
        # Unset outside production, where there is no nginx container: the
        # check reports itself as skipped instead of failing the endpoint.
        assert payload["checks"]["nginx"]["status"] == "skipped"
        assert "duration_ms" in payload

    def test_health_reads_nginx_status(self):
        stub_status = (
            "Active connections: 7 \n"
            "server accepts handled requests\n"
            " 12 12 30 \n"
            "Reading: 0 Writing: 1 Waiting: 6 \n"
        )
        nginx_response = MagicMock()
        nginx_response.read.return_value = stub_status.encode()
        nginx_response.__enter__.return_value = nginx_response

        with patch("app.NGINX_STATUS_URL", "http://nginx:8080/nginx_status"), patch(
            "urllib.request.urlopen", return_value=nginx_response
        ):
            response = self.client.get("/health")

        assert response.status_code == 200
        nginx = response.get_json()["checks"]["nginx"]
        assert nginx["status"] == "ok"
        assert nginx["active_connections"] == 7

    def test_health_reports_a_failing_dependency(self):
        def unreachable():
            raise RuntimeError("connection refused")

        with patch.dict("app.HEALTH_CHECKS", {"database": unreachable}):
            response = self.client.get("/health")

        assert response.status_code == 503
        payload = response.get_json()
        assert payload["status"] == "unhealthy"
        database = payload["checks"]["database"]
        assert database["status"] == "error"
        assert "connection refused" in database["error"]

    def test_metrics(self):
        response = self.client.get("/metrics")
        assert response.status_code == 200
        body = response.get_data(as_text=True)
        # Request metrics from the exporter, dependency gauges from our own
        # collector — Prometheus needs both from this one endpoint.
        assert "flask_http_request_total" in body
        assert 'portfolio_dependency_up{dependency="database"} 1.0' in body

    def test_nav_hides_operational_routes(self):
        html = self.client.get("/").get_data(as_text=True)
        assert 'href="/hobbies"' in html
        assert 'href="/health"' not in html
        assert 'href="/metrics"' not in html

    def test_malformed_timeline_post(self):
        # POST request missing name
        response = self.client.post(
            "/api/timeline_post",
            data={
                "email": "john@example.com",
                "content": "Hello world, I'm John!",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html

        # POST request with empty content
        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "john@example.com",
                "content": "",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html

        # POST request with malformed email
        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "not-an-email",
                "content": "Hello world, I'm John!",
            },
        )
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html
