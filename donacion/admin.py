from django.contrib import admin
from .models import CollectionCenter, Zone, Donacion, SerologyStudy, Consent, Visit

admin.site.register(CollectionCenter)
admin.site.register(Zone)
admin.site.register(Donacion)
admin.site.register(SerologyStudy)
admin.site.register(Consent)
admin.site.register(Visit)
