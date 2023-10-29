from django.db import models
from django.utils.timezone import now



class ContactInformation(models.Model):
    Address = models.TextField(blank=True,null=True)
    State = models.CharField(max_length=100,null=True,blank=True)
    Country = models.CharField(max_length=100,null=True,blank=True)
    Pincode = models.IntegerField(null=True,blank=True)
    Phonenumber= models.CharField(max_length=100,null=True,blank=True)
    DateAdded = models.DateTimeField(auto_now_add=now)
    DateUpdated = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.DateAdded)
    



class Recentlabhistory(models.Model):
   
    Fastingbloodsugar = models.CharField(max_length=100,null=True,blank=True)
    Bloodpressure = models.CharField(max_length=100,null=True,blank=True)
    Hba1c = models.FloatField(null=True,blank=True)
    Cholesterol = models.FloatField(null=True,blank=True)
    DateAdded = models.DateTimeField(auto_now_add=now)
    DateUpdated = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.DateAdded)

class MedicalHistory(models.Model):
    Allergies = models.CharField(max_length=100,blank=True,null=True)
    Medications = models.CharField(max_length=100,blank=True,null=True)
    Medicalconditions = models.CharField(max_length=100,blank=True,null=True)
    Familyhistory = models.TextField(blank=True,null=True)
    DateAdded = models.DateTimeField(auto_now_add=now)
    DateUpdated = models.DateTimeField(auto_now_add=now)

    def __str__(self):
        return str(self.DateAdded)

class Checkupandappointment(models.Model):
    Disease = models.CharField(max_length=100)
    DateAdded = models.DateField(blank=True)
    DateUpdated = models.DateField(auto_now_add=True)


    def __str__(self):
        return self.Disease

class Patientinformation(models.Model):
    PatientNAME= models.CharField(max_length=100,null=True,blank=True)
    PatientAGE = models.IntegerField(null=True,blank=True)
    PatientCOURSE = models.CharField(max_length=100,null=True,blank=True)
    PatientYEARLEVEL = models.CharField(max_length=100,blank=True,null=True)
    PatientGender = models.CharField(max_length=100,null=True,blank=True)
    PatientBirthday = models.CharField(max_length=100,null=True,blank=True)
    DateAdded = models.DateTimeField(auto_now_add=now)
    DateUpdated = models.DateTimeField(auto_now_add=now)
    ContactInformationID = models.ForeignKey(ContactInformation,on_delete=models.CASCADE)
    CheckupandappointmentID = models.ForeignKey(Checkupandappointment,on_delete=models.CASCADE)
    RecentlabhistoryID = models.ForeignKey(Recentlabhistory, on_delete=models.CASCADE)
    MedicalHistoryID = models.ForeignKey(MedicalHistory, on_delete=models.CASCADE)


    def __str__(self):
        return self.PatientCOURSE






    












