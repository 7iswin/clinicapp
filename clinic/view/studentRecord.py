from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from clinic.model.patientrecord import (
    Patientinformation,
    ContactInformation,
    Recentlabhistory,
    MedicalHistory,
    Checkupandappointment
)
from django.contrib.auth.decorators import login_required
import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from django.db.models import Q
from clinic.model.account import Account
def generate_excel(request):
    patient_model = Patientinformation.objects.get(id=request.GET['id'])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="student_detail.xlsx"'
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['Name', patient_model.PatientNAME])
    worksheet.append(['Age', patient_model.PatientAGE])
    worksheet.append(['Gender', patient_model.PatientGender])
    worksheet.append(['Course', patient_model.PatientCOURSE])
    worksheet.append(['Birthday', patient_model.PatientBirthday])
    worksheet.append(['Disease', patient_model.CheckupandappointmentID.Disease])
    worksheet.append(['Allergies', patient_model.MedicalHistoryID.Allergies])
    worksheet.append(['Medications', patient_model.MedicalHistoryID.Medications])
    worksheet.append(['Medicalconditions', patient_model.MedicalHistoryID.Medicalconditions])
    worksheet.append(['Familyhistory', patient_model.MedicalHistoryID.Familyhistory])
    worksheet.append(['Fastingbloodsugar', patient_model.RecentlabhistoryID.Fastingbloodsugar])
    worksheet.append(['Bloodpressure', patient_model.RecentlabhistoryID.Bloodpressure])
    worksheet.append(['Hba1c', patient_model.RecentlabhistoryID.Hba1c])
    worksheet.append(['Cholesterol', patient_model.RecentlabhistoryID.Cholesterol])
 



    workbook.save(response)
    return response

def generate_pdf(request):

    patient_model = Patientinformation.objects.get(id=request.GET['id'])
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_detail.pdf"'
    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    p.drawString(50, 750, f"Name: {patient_model.PatientNAME}")
    p.drawString(50, 730, f"Age:  {patient_model.PatientAGE}")
    p.drawString(50, 710, f"Gender: {patient_model.PatientGender}")
    p.drawString(50, 690, f"Course: {patient_model.PatientCOURSE}")
    p.drawString(50, 670, f"Birthday: {patient_model.PatientBirthday}")
    p.drawString(50, 650, f"Year Level: {patient_model.PatientYEARLEVEL}")
    p.drawString(50, 610, f"Disease Name: {patient_model.CheckupandappointmentID.Disease}")
    p.drawString(50, 590, f"Date Added: {patient_model.CheckupandappointmentID.DateUpdated}")
    p.drawString(50, 550, f"Allergies: {patient_model.MedicalHistoryID.Allergies}")
    p.drawString(50, 530, f"Medications: {patient_model.MedicalHistoryID.Medications}")
    p.drawString(50, 510, f"Medical Conditions: {patient_model.MedicalHistoryID.Medicalconditions}")
    p.drawString(50, 490, f"Family History: {patient_model.MedicalHistoryID.Familyhistory}")
    p.drawString(50, 470, f"Date Added: {patient_model.MedicalHistoryID.DateAdded}")
    p.drawString(50, 450, f"Date Updated: {patient_model.MedicalHistoryID.DateUpdated}")
    p.drawString(50, 410, f"Fasting Blood Sugar: {patient_model.RecentlabhistoryID.Fastingbloodsugar}")
    p.drawString(50, 390, f"Blood Pressure: {patient_model.RecentlabhistoryID.Bloodpressure}")
    p.drawString(50, 370, f"HbA1c: {patient_model.RecentlabhistoryID.Hba1c}")
    p.drawString(50, 350, f"Cholesterol: {patient_model.RecentlabhistoryID.Cholesterol}")
    p.drawString(50, 330, f"Date Added: {patient_model.RecentlabhistoryID.DateAdded}")
    p.drawString(50, 310, f"Date Updated: {patient_model.RecentlabhistoryID.DateUpdated}")
    p.showPage()
    p.save()
    return response
def record_delete(request):
    Patientinformation.objects.get(id=request.GET['id']).delete()
    messages.success(request, "The patient record has been deleted successfully.")
    return redirect(reverse('studentrecord:list'))
def record_edit(request):
    user_model = Account.objects.filter(user=request.user).first()
    patient_model = Patientinformation.objects.get(id=request.GET["id"])
    patient_course = Patientinformation.objects.all().values('PatientCOURSE').distinct()
    patient_year_level = Patientinformation.objects.all().values('PatientYEARLEVEL').distinct()
    patient_gender = Patientinformation.objects.all().values('PatientGender').distinct()
    
    if request.method == 'POST':
        patient_model.PatientNAME = request.POST.get('fullname')
        patient_model.PatientAGE = request.POST.get('age')
        patient_model.PatientCOURSE = request.POST.get('course')
        birthdate = request.POST.get('birthdate')
        if birthdate:
            patient_model.PatientBirthday = datetime.datetime.strptime(birthdate, '%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            patient_model.PatientBirthday = None

        patient_model.PatientYEARLEVEL = request.POST.get('yearlevel')
        patient_model.PatientGender = request.POST.get('gender')
        patient_model.ContactInformationID.Address = request.POST.get('address')
        patient_model.ContactInformationID.State = request.POST.get('state')
        patient_model.ContactInformationID.Country = request.POST.get('country')
        patient_model.ContactInformationID.Pincode = request.POST.get('pincode')
        patient_model.ContactInformationID.Phonenumber = request.POST.get('phonenumber')
        patient_model.MedicalHistoryID.Allergies = request.POST.get('allergies')
        patient_model.MedicalHistoryID.Medications = request.POST.get('medications')
        patient_model.MedicalHistoryID.Medicalconditions = request.POST.get('medicalconditions')
        patient_model.MedicalHistoryID.Familyhistory = request.POST.get('familyhistory')
        patient_model.RecentlabhistoryID.Fastingbloodsugar = request.POST.get('fastingbloodsugar')
        patient_model.RecentlabhistoryID.Hba1c = request.POST.get('hba1c')
        patient_model.RecentlabhistoryID.Bloodpressure = request.POST.get('bloodpressure')
        patient_model.RecentlabhistoryID.Cholesterol = request.POST.get('cholesterol')
        patient_model.CheckupandappointmentID.Disease = request.POST.get('disease')
        checkupdate = request.POST.get('checkupdate')
        if checkupdate:
            patient_model.CheckupandappointmentID.DateAdded = datetime.datetime.strptime(checkupdate, '%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            patient_model.CheckupandappointmentID.DateAdded = None

        patient_model.save()
        messages.success(request,"The patient information has been saved successfully")
        return redirect(reverse('studentrecord:list'))

    context = {
        'patient_model':patient_model,
        'patient_course':patient_course,
        'patient_year_level':patient_year_level,
        'patient_gender':patient_gender,
        'user_model':user_model
    }
    return render(request,'studentlist/studentedit.html',context)


@login_required(login_url='/account/')
def record_list(request):
    user_model = Account.objects.filter(user=request.user).first()
    patient_course = Patientinformation.objects.all().values('PatientCOURSE').distinct()
    patient_model =  Patientinformation.objects.all().order_by('-DateAdded').reverse()
    if request.method == "POST":
        id = request.POST['ID']
        name = request.POST['name']
        course = request.POST['course']
        filter_conditions = Q()
        if id:
            filter_conditions |= Q(id__icontains=id)
        if name:
            filter_conditions |= Q(PatientNAME__icontains=name)
        if course:
            filter_conditions |= Q(PatientCOURSE__icontains=course)

        patient_model = Patientinformation.objects.filter(filter_conditions).order_by('-DateAdded').reverse()
    
    
    context = {
        'patient_model':patient_model,
        'patient_course':patient_course,
        'user_model':user_model
    }
    return render(request,'studentlist/studentlist.html',context)

@login_required(login_url='/account/')
def record_detail(request):
    user_model = Account.objects.filter(user=request.user).first()
    patient_model = Patientinformation.objects.filter(id=request.GET['id']).first()
    context = {
        'patient_model':patient_model,
        'user_model':user_model
    }
    return render(request,'studentlist/studentdetail.html',context)

@login_required(login_url='/account/')
def record_add(request):
    
    
    if request.method == 'POST':
        #patient information
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        age = request.POST.get('age')
        course = request.POST.get('course')
        birthdate = datetime.datetime.strptime(request.POST['birthdate'], '%d-%m-%Y').strftime('%Y-%m-%d')
        yearlevel = request.POST.get('yearlevel')
        gender = request.POST.get('gender')
        #contact  information
        address = request.POST.get('address')
        state = request.POST.get('state')
        country = request.POST.get('country')
        pincode = request.POST.get('pincode')
        phonenumber = request.POST.get('phonenumber')
        #medical history
        allergies = request.POST.get('allergies')
        medications = request.POST.get('medications')
        medicalconditions = request.POST.get('medicalconditions')
        familyhistory = request.POST.get('familyhistory')
        #Recent Lab Results
        fastingbloodsugar = request.POST.get('fastingbloodsugar')
        hba1c = request.POST.get('hba1c')
        bloodpressure = request.POST.get('bloodpressure')
        cholesterol = request.POST.get('cholesterol')
        #Check-Up and Appointments
        disease = request.POST.get('disease')
        checkupdate = datetime.datetime.strptime(request.POST['checkupdate'], '%d-%m-%Y').strftime('%Y-%m-%d')
    


        ContactInformation_model = ContactInformation.objects.create(
            Address=address,
            State=state,
            Country=country,
            Pincode=pincode,
            Phonenumber=phonenumber,
        )
        ContactInformation_model.save()
        MedicalHistory_model = MedicalHistory.objects.create(
            Allergies=allergies,
            Medications=medications,
            Medicalconditions=medicalconditions,
            Familyhistory=familyhistory,
           

        )
        MedicalHistory_model.save()
        Recentlabhistory_model = Recentlabhistory.objects.create(
            Fastingbloodsugar=fastingbloodsugar,
            Bloodpressure=bloodpressure,
            Hba1c=hba1c,
            Cholesterol=cholesterol,
        )
        Recentlabhistory_model.save()
        Checkupandappointment_model = Checkupandappointment.objects.create(
            Disease=disease,
            DateAdded=checkupdate,
        )
        Checkupandappointment_model.save()
        Patientinformation_model = Patientinformation.objects.create(
            PatientNAME=str(firstname) + ' ' + str(lastname),
            PatientAGE=age,
            PatientCOURSE=course,
            PatientBirthday=birthdate,
            PatientYEARLEVEL=yearlevel,
            PatientGender=gender,
            ContactInformationID =ContactInformation_model,
            CheckupandappointmentID =Checkupandappointment_model,
            RecentlabhistoryID =Recentlabhistory_model,
            MedicalHistoryID =MedicalHistory_model
        )
        Patientinformation_model.save()
        
        messages.success(request,"The patient information has been saved successfully")
        return redirect(reverse('studentrecord:add'))
    else:
        user_model = Account.objects.filter(user=request.user).first()
        patient_course = Patientinformation.objects.all().values('PatientCOURSE').distinct()
        return render(request,'studentlist/studentadd.html',{'patient_course':patient_course,'user_model':user_model})