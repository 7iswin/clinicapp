from django.contrib import admin
from clinic.model.patientrecord import (
    Patientinformation,
    ContactInformation,
    Recentlabhistory,
    MedicalHistory,
    Checkupandappointment
)
admin.site.register(Patientinformation)
admin.site.register(ContactInformation)
admin.site.register(Recentlabhistory)
admin.site.register(MedicalHistory)
admin.site.register(Checkupandappointment)

