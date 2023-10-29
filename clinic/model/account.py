from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=100,blank=True)
    lastname = models.CharField(max_length=100,blank=True)
    userid = models.CharField(max_length=100,blank=True)
    bio = models.TextField(blank=True)
    position = models.CharField(max_length=100,blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=100, blank=True)
    age = models.CharField(max_length=100, blank=True)
    residence = models.CharField(max_length=100, blank=True)
    bday=models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=100, blank=True)
    companyname = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    periodfrom = models.DateField(null=True, blank=True)
    periodto = models.DateField(null=True, blank=True)
    phonenumber = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.user.username