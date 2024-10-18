import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from planetarium_api.models import AstronomyShow
from planetarium_api.serializers import (
    AstronomyShowListSerializer,
    AstronomyShowDetailSerializer,
)

ADMIN_ID = 1
REGULAR_USER_ID = 2
NO_IMAGE_SHOW_ID = 4
SHOW_LIST_URL = reverse("planetarium_api:astronomyshow-list")
SHOW_DETAIL_URL = reverse(
    "planetarium_api:astronomyshow-detail", args=[NO_IMAGE_SHOW_ID]
)
SHOW_IMAGE_UPLOAD_URL = reverse(
    "planetarium_api:astronomyshow-upload-image", args=[NO_IMAGE_SHOW_ID]
)
SHOW_SESSION_URL = reverse("planetarium_api:showsession-list")


class AstronomyShowImageUploadTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loaddata", "fixture.json")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.get(pk=ADMIN_ID)
        )
        self.astronomy_show = AstronomyShow.objects.get(pk=NO_IMAGE_SHOW_ID)

    def tearDown(self):
        self.astronomy_show.refresh_from_db()
        self.astronomy_show.image.delete()

    def test_upload_image_to_astronomy_show(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                SHOW_IMAGE_UPLOAD_URL, {"image": ntf}, format="multipart"
            )
        self.astronomy_show.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.astronomy_show.image.path))

    def test_upload_not_image_bad_request(self):
        res = self.client.post(
            SHOW_IMAGE_UPLOAD_URL, {"image": "not image"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_astronomy_show_list(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                SHOW_LIST_URL,
                {
                    "title": "Title",
                    "description": "Description",
                    "themes": [1],
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(title="Title")
        self.assertFalse(astronomy_show.image)

    def test_image_url_is_shown_on_astronomy_show_detail(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                SHOW_IMAGE_UPLOAD_URL, {"image": ntf}, format="multipart"
            )

        res = self.client.get(SHOW_DETAIL_URL)

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_astronomy_show_list(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                SHOW_IMAGE_UPLOAD_URL, {"image": ntf}, format="multipart"
            )

        res = self.client.get(SHOW_LIST_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_show_session_detail(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(
                SHOW_IMAGE_UPLOAD_URL, {"image": ntf}, format="multipart"
            )

        res = self.client.get(SHOW_SESSION_URL)

        self.assertIn("astronomy_show_image", res.data[0].keys())


class UnauthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(SHOW_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loaddata", "fixture.json")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.get(id=REGULAR_USER_ID)
        )

    def test_should_return_all_astronomy_shows_list(self):
        response = self.client.get(SHOW_LIST_URL)
        astronomy_shows = AstronomyShow.objects.all()
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_filter_astronomy_shows_by_themes(self):
        no_themes_show = AstronomyShow.objects.get(id=1)
        no_themes_show.themes.clear()
        no_themes_serializer = AstronomyShowListSerializer(no_themes_show)
        serializer_with_themes_1 = AstronomyShowListSerializer(
            AstronomyShow.objects.get(id=4)
        )
        serializer_with_themes_2 = AstronomyShowListSerializer(
            AstronomyShow.objects.get(id=5)
        )

        response = self.client.get(SHOW_LIST_URL, {"themes": "11"})

        self.assertIn(serializer_with_themes_1.data, response.data)
        self.assertIn(serializer_with_themes_2.data, response.data)
        self.assertNotIn(no_themes_serializer.data, response.data)

    def test_filter_astronomy_shows_by_title(self):
        serializer_matched_1 = AstronomyShowListSerializer(
            AstronomyShow.objects.get(id=1)
        )
        serializer_matched_2 = AstronomyShowListSerializer(
            AstronomyShow.objects.get(id=2)
        )
        serializer_not_matched = AstronomyShowListSerializer(
            AstronomyShow.objects.get(id=3)
        )

        response = self.client.get(SHOW_LIST_URL, {"title": "L"})

        self.assertIn(serializer_matched_1.data, response.data)
        self.assertIn(serializer_matched_2.data, response.data)
        self.assertNotIn(serializer_not_matched.data, response.data)

    def test_retrieve_astronomy_show_detail(self):
        response = self.client.get(SHOW_DETAIL_URL)

        serializer = AstronomyShowDetailSerializer(
            AstronomyShow.objects.get(id=NO_IMAGE_SHOW_ID)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "test show",
            "description": "test description",
            "themes": [1, 2, 3],
        }

        response = self.client.post(SHOW_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAstronomyShowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loaddata", "fixture.json")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            get_user_model().objects.get(id=ADMIN_ID)
        )

    def test_create_astronomy_show_with_themes(self):
        payload = {
            "title": "test show",
            "description": "test description",
            "themes": [1, 2, 3],
        }

        response = self.client.post(SHOW_LIST_URL, payload)
        show = (
            AstronomyShow.objects.filter(id=response.data["id"])
            .prefetch_related("themes")
            .first()
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(show.title, payload["title"])
        self.assertEqual(show.description, payload["description"])
        self.assertCountEqual(
            list(show.themes.values_list("id", flat=True)), payload["themes"]
        )

    def test_create_astronomy_show_without_themes_should_return_400(self):
        payload = {
            "title": "test show",
            "description": "test description",
            "themes": [],
        }

        response = self.client.post(SHOW_LIST_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_astronomy_show_not_allowed(self):
        response = self.client.delete(SHOW_DETAIL_URL)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
