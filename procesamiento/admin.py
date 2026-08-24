from django.contrib import admin
from .models import (
    MilkBatches,
    PasteurizationRecord,
    Fractionation,
    FractionatedBottle,
    DonorDismissal,
    InternalExtraction,
)

admin.site.register(MilkBatches)
admin.site.register(PasteurizationRecord)
admin.site.register(Fractionation)
admin.site.register(FractionatedBottle)
admin.site.register(DonorDismissal)
admin.site.register(InternalExtraction)
