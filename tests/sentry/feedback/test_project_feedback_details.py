import datetime
import uuid

from django.urls import reverse
from rest_framework.exceptions import ErrorDetail

from sentry.feedback.models import Feedback
from sentry.testutils.cases import APITestCase


class ProjectFeedbackDetailTest(APITestCase):
    endpoint = "sentry-api-0-project-feedback-details"

    def setUp(self):
        super().setUp()
        self.login_as(user=self.user)
        self.replay_id_1 = uuid.uuid4().hex
        self.feedback_id_1 = uuid.uuid4().hex
        self.replay_id_2 = uuid.uuid4().hex
        self.feedback_id_2 = uuid.uuid4().hex

    def test_get_feedback_item(self):
        # Successful GET
        Feedback.objects.create(
            data={
                "environment": "production",
                "feedback": {
                    "contact_email": "colton.allen@sentry.io",
                    "message": "I really like this user-feedback feature!",
                    "replay_id": "ec3b4dc8b79f417596f7a1aa4fcca5d2",
                    "url": "https://docs.sentry.io/platforms/javascript/",
                },
                "platform": "javascript",
                "release": "version@1.3",
                "sdk": {"name": "sentry.javascript.react", "version": "6.18.1"},
                "tags": {"key": "value"},
                "user": {
                    "email": "username@example.com",
                    "id": "123",
                    "ip_address": "127.0.0.1",
                    "name": "user",
                    "username": "user2270129",
                },
                "dist": "abc123",
                "contexts": {},
            },
            date_added=datetime.datetime.fromtimestamp(1234456),
            feedback_id=self.feedback_id_1,
            url="https://docs.sentry.io/platforms/javascript/",
            message="I really like this user-feedback feature!",
            replay_id=self.replay_id_1,
            project_id=self.project.id,
            organization_id=self.organization.id,
        )

        Feedback.objects.create(
            data={
                "environment": "prod",
                "feedback": {
                    "contact_email": "michelle.zhang@sentry.io",
                    "message": "I also really like this user-feedback feature!",
                    "replay_id": "zc3b5xy8b79f417596f7a1tt4fffa5d2",
                    "url": "https://docs.sentry.io/platforms/electron/",
                },
                "platform": "electron",
                "release": "version@1.3",
                "request": {
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                    }
                },
                "sdk": {"name": "sentry.javascript.react", "version": "5.18.1"},
                "tags": {"key": "value"},
                "user": {
                    "email": "username@example.com",
                    "id": "123",
                    "ip_address": "127.0.0.1",
                    "name": "user",
                    "username": "user2270129",
                },
                "dist": "abc123",
                "contexts": {},
            },
            date_added=datetime.datetime.fromtimestamp(12344100333),
            feedback_id=self.feedback_id_2,
            url="https://docs.sentry.io/platforms/electron/",
            message="I also really like this user-feedback feature!",
            replay_id=self.replay_id_2,
            project_id=self.project.id,
            organization_id=self.organization.id,
        )

        with self.feature({"organizations:user-feedback-ingest": True}):
            # Get one feedback
            path = reverse(
                self.endpoint,
                args=[
                    self.organization.slug,
                    self.project.slug,
                    self.feedback_id_1,
                ],
            )
            response = self.client.get(path)
            assert response.status_code == 200, response.content
            feedback = response.data
            assert feedback["dist"] == "abc123"
            assert feedback["url"] == "https://docs.sentry.io/platforms/javascript/"
            assert feedback["message"] == "I really like this user-feedback feature!"
            assert feedback["feedback_id"] == uuid.UUID(self.feedback_id_1)
            assert feedback["platform"] == "javascript"
            assert feedback["sdk"]["name"] == "sentry.javascript.react"
            assert feedback["tags"]["key"] == "value"
            assert feedback["contact_email"] == "colton.allen@sentry.io"

            # Get the other feedback
            path = reverse(
                self.endpoint,
                args=[
                    self.organization.slug,
                    self.project.slug,
                    self.feedback_id_2,
                ],
            )
            response = self.client.get(path)
            assert response.status_code == 200
            feedback = response.data
            assert feedback["feedback_id"] == uuid.UUID(self.feedback_id_2)
            assert feedback["contact_email"] == "michelle.zhang@sentry.io"

    def test_no_feature_enabled(self):
        # Unsuccessful GET
        with self.feature({"organizations:user-feedback-ingest": False}):
            path = reverse(
                self.endpoint,
                args=[
                    self.organization.slug,
                    self.project.slug,
                    self.feedback_id_1,
                ],
            )
            get_response = self.client.get(path)
            assert get_response.status_code == 404

    def test_bad_slug_path(self):
        # Bad slug in path should lead to unsuccessful GET
        with self.feature({"organizations:user-feedback-ingest": True}):
            path = reverse(
                self.endpoint,
                args=[
                    "testslug1234555",
                    self.project.slug,
                    self.feedback_id_1,
                ],
            )
            get_response = self.client.get(path)
            assert get_response.status_code == 404
            assert get_response.data == {
                "detail": ErrorDetail(string="The requested resource does not exist", code="error")
            }

    def test_no_feedback_found(self):
        with self.feature({"organizations:user-feedback-ingest": True}):
            path = reverse(
                self.endpoint,
                args=[
                    self.organization.slug,
                    self.project.slug,
                    self.feedback_id_1,
                ],
            )
            response = self.client.get(path)
            assert response.status_code == 404

    def test_other_project(self):
        # Should not be able to query for another project's feedback
        with self.feature({"organizations:user-feedback-ingest": True}):
            Feedback.objects.create(
                data={
                    "environment": "prod",
                    "feedback": {
                        "contact_email": "michelle.zhang@sentry.io",
                        "message": "I also really like this user-feedback feature!",
                        "replay_id": "zc3b5xy8b79f417596f7a1tt4fffa5d2",
                        "url": "https://docs.sentry.io/platforms/electron/",
                    },
                    "platform": "electron",
                    "release": "version@1.3",
                    "request": {
                        "headers": {
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
                        }
                    },
                    "sdk": {"name": "sentry.javascript.react", "version": "5.18.1"},
                    "tags": {"key": "value"},
                    "user": {
                        "email": "username@example.com",
                        "id": "123",
                        "ip_address": "127.0.0.1",
                        "name": "user",
                        "username": "user2270129",
                    },
                    "dist": "abc123",
                    "contexts": {},
                },
                date_added=datetime.datetime.fromtimestamp(12344100333),
                feedback_id=self.feedback_id_2,
                url="https://docs.sentry.io/platforms/electron/",
                message="I also really like this user-feedback feature!",
                replay_id=self.replay_id_2,
                project_id=self.project.id,
                organization_id=self.organization.id,
            )

            path = reverse(
                self.endpoint,
                args=[
                    self.organization.slug,
                    "other_project",
                    self.feedback_id_1,
                ],
            )
            response = self.client.get(path)
            assert response.status_code == 404