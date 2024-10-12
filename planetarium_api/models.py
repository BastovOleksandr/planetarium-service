import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.utils.text import slugify


class PlanetariumDome(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    class Meta:
        ordering = (Lower("name"),)

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class ShowTheme(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = (Lower("name"),)

    def __str__(self):
        return self.name


def astronomy_show_image_file_path(instance: "AstronomyShow", filename):
    _, extension = os.path.splitext(filename)
    return os.path.join(
        "uploads/astronomy_shows/",
        f"{slugify(instance.title)}-{uuid.uuid4()}{extension}",
    )


class AstronomyShow(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    themes = models.ManyToManyField(ShowTheme, related_name="astronomy_shows")
    image = models.ImageField(null=True, upload_to=astronomy_show_image_file_path)

    class Meta:
        ordering = (Lower("title"),)

    def __str__(self):
        return self.title


class ShowSession(models.Model):
    show_time = models.DateTimeField()
    astronomy_show = models.ForeignKey(AstronomyShow, on_delete=models.CASCADE)
    planetarium_dome = models.ForeignKey(PlanetariumDome, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-show_time",)

    def __str__(self):
        return f"{self.astronomy_show.title} at {self.show_time}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Reservation by {self.user.email}. Created at: {self.created_at}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    show_session = models.ForeignKey(
        ShowSession, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("show_session", "row", "seat")
        ordering = (
            "row",
            "seat",
        )

    @staticmethod
    def validate_row_seat(seat: int, row: int, show_session, error_to_raise):
        for ticket_attr_value, ticket_attr_name, planetarium_dome_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(
                show_session.planetarium_dome, planetarium_dome_attr_name
            )
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {planetarium_dome_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_row_seat(
            self.seat, self.row, self.show_session, ValidationError
        )

    def save(
        self,
        *args,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.show_session}:\n(row: {self.row}, seat: {self.seat})"
