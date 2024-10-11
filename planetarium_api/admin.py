from django.contrib import admin

from planetarium_api.models import (
    PlanetariumDome,
    ShowTheme,
    AstronomyShow,
    ShowSession,
    Reservation,
    Ticket,
)

admin.site.register(PlanetariumDome)
admin.site.register(ShowTheme)
admin.site.register(AstronomyShow)
admin.site.register(ShowSession)
admin.site.register(Ticket)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInLine,)
