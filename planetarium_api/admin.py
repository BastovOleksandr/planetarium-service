from django.contrib import admin
from django.contrib.auth.models import Group

from planetarium_api.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    ShowSession,
    Ticket,
    Reservation,
)

admin.site.unregister(Group)

admin.site.register(ShowTheme)
admin.site.register(PlanetariumDome)
admin.site.register(AstronomyShow)
admin.site.register(ShowSession)
admin.site.register(Ticket)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)
