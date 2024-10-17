from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from planetarium_api.models import (
    ShowTheme,
    PlanetariumDome,
    AstronomyShow,
    Ticket,
    Reservation,
    ShowSession,
)


class ShowThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowTheme
        fields = ("id", "name")


class PlanetariumDomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanetariumDome
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class AstronomyShowImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = ("image",)


class AstronomyShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = AstronomyShow
        fields = (
            "id",
            "title",
            "description",
            "themes",
        )


class AstronomyShowDetailSerializer(AstronomyShowSerializer):
    themes = ShowThemeSerializer(many=True)
    image = serializers.CharField()

    class Meta:
        model = AstronomyShow
        fields = AstronomyShowSerializer.Meta.fields + ("image",)


class AstronomyShowListSerializer(AstronomyShowDetailSerializer):
    themes = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )


class ShowSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShowSession
        fields = ("id", "show_time", "astronomy_show", "planetarium_dome")


class ShowSessionListSerializer(ShowSessionSerializer):
    astronomy_show_title = serializers.CharField(
        source="astronomy_show.title"
    )
    planetarium_dome_name = serializers.CharField(
        source="planetarium_dome.name"
    )
    planetarium_dome_capacity = serializers.IntegerField(
        source="planetarium_dome.capacity"
    )
    tickets_available = serializers.IntegerField()
    astronomy_show_image = AstronomyShowImageSerializer(
        source="astronomy_show.image"
    )

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "show_time",
            "astronomy_show_title",
            "planetarium_dome_name",
            "planetarium_dome_capacity",
            "tickets_available",
            "astronomy_show_image",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Ticket.validate_row_seat(
            attrs["seat"],
            attrs["row"],
            attrs["show_session"],
            error_to_raise=ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "show_session")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=["show_session", "row", "seat"]
            )
        ]


class TicketListSerializer(TicketSerializer):
    show_session = ShowSessionListSerializer()


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class ShowSessionDetailSerializer(ShowSessionSerializer):
    astronomy_show = AstronomyShowListSerializer()
    planetarium_dome = PlanetariumDomeSerializer()
    taken_places = TicketSeatsSerializer(source="tickets", many=True)

    class Meta:
        model = ShowSession
        fields = (
            "id",
            "show_time",
            "astronomy_show",
            "planetarium_dome",
            "taken_places",
        )


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True)
