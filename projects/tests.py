from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project, ProjectComment

User = get_user_model()


class SystemAnalyticsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=self.user)

    def test_system_analytics_returns_summary_and_popular_project(self):
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="StrongPass123!",
        )

        project_one = Project.objects.create(
            user=self.user,
            title="AI Portfolio",
            description="First project",
            file=SimpleUploadedFile("one.pdf", b"%PDF-1.4", content_type="application/pdf"),
        )
        Project.objects.create(
            user=other_user,
            title="Design System",
            description="Second project",
            file=SimpleUploadedFile("two.pdf", b"%PDF-1.4", content_type="application/pdf"),
        )
        project_one.likes.add(other_user)
        ProjectComment.objects.create(project=project_one, user=other_user, content="Great work")

        response = self.client.get(reverse("system-analytics"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["summary"]["total_projects"], 2)
        self.assertEqual(response.data["summary"]["total_users"], 2)
        self.assertEqual(response.data["summary"]["total_comments"], 1)
        self.assertEqual(response.data["popular_project"]["title"], "AI Portfolio")
        self.assertEqual(response.data["popular_project"]["likes"], 1)
        self.assertTrue(any(item["email"] == self.user.email for item in response.data["top_uploaders"]))
