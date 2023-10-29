from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from clinic.model.patientrecord import Checkupandappointment,Patientinformation

from django.db.models import Count
from clinic.model.account import Account
from django.db.models.functions import TruncDate
from mixin import Filter,Recent_Patient
from django.db.models import Sum
from datetime import date
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from clinic.model.forecast import Forecast
@login_required(login_url='/account/')
def index(request):
    user_model = Account.objects.filter(user=request.user).first()
    recent = Recent_Patient(Checkupandappointment,['DateAdded','Disease'],target='Disease').year_month_day()
    All_Courses = Patientinformation.objects.annotate(date_added=TruncDate('DateAdded')).values('date_added').annotate(patient_count=Count('date_added')).order_by('-date_added')[:5]
    total_count = Patientinformation.objects.all().count()

    All_Disease = Checkupandappointment.objects.all().values('Disease').distinct().order_by('Disease')
    
    top_7_disease =  Forecast.objects.values('Disease').annotate(Disease_count=Sum('Disease_count')).order_by('-Disease_count')[:7]
    


    today = datetime.today()
    end_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    start_of_last_month = end_of_last_month.replace(day=1) - timedelta(days=1)
    end_of_last_month_aware = make_aware(end_of_last_month.replace(hour=0, minute=0, second=0))
    start_of_last_month_aware = make_aware(start_of_last_month.replace(day=1, hour=23, minute=59, second=59))
    start_of_month = today.replace(day=1)
    disease_counts = Checkupandappointment.objects.filter(DateAdded__gte=start_of_month).values('Disease').annotate(Disease_count=Count('Disease'))\
                    .order_by('-Disease_count')[:10]
    
    dataset = []
    for entry in disease_counts:
        data = {}
        data= {}
        top_patient_courses = Patientinformation.objects.filter(CheckupandappointmentID__Disease=entry['Disease']).values('PatientCOURSE')\
                            .annotate(Patient_count=Count('PatientCOURSE')).order_by('-PatientCOURSE').first()
        
        data['Disease']= entry['Disease']
        data['Disease_count']= entry['Disease_count']
        if top_patient_courses is not None:
            data['PatientCOURSE'] = top_patient_courses.get('PatientCOURSE', "No Patient")
            data['Patient_count'] = top_patient_courses.get('Patient_count', "No Patient")
        else:
            data['PatientCOURSE'] = "Unidentified"
            data['Patient_count'] = "Unidentified"
       
        dataset.append(data)


            
    
        
        
                                
        
        
        
     
    


    context = {
           'patient_count_week':recent,
            'all_courses':All_Courses,
            'all_disease':All_Disease,
            'top_disease':top_7_disease,
            'Patient_course':dataset,
            'total_count':total_count,
            'user_model': user_model,
        }
    return render(request,'forecasting_analytic.html',context)
