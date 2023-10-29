from django.shortcuts import render, redirect,HttpResponse
from django.urls import reverse
from django.contrib import messages
import os
from clinic.mixin.forms import ExcelFileform
from clinic.model.account import Account
from clinic.model.patientrecord import Checkupandappointment, ContactInformation,Patientinformation
from django.conf import settings
import openpyxl
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware
from clinic.model.patientrecord import (
    Patientinformation,
    ContactInformation,
    Recentlabhistory,
    MedicalHistory,
    Checkupandappointment
)
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from clinic.model.forecast import Forecast
from mixin import Filter,Recent_Patient
from collections import defaultdict
from django.db.models import Sum
from datetime import date
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Max,Min
from collections import defaultdict
import os
from datetime import datetime, timedelta
from django.db.models import Q
from clinic.model.patientrecord import Checkupandappointment
from clinic.model.forecast import Forecast
from prediction import RNNModel

from django.conf import settings

@login_required(login_url='/account/')

def index(request):
    
    user_model = Account.objects.filter(user=request.user).first()
    recent = Recent_Patient(Checkupandappointment,['DateAdded','Disease'],target='Disease').year_month_day()
    All_Courses = Patientinformation.objects.annotate(date_added=TruncDate('DateAdded')).values('date_added').annotate(patient_count=Count('date_added')).order_by('-date_added')[:5]
    total_count = Patientinformation.objects.all().count()

    All_Disease = Checkupandappointment.objects.all().values('Disease').distinct().order_by('Disease')
    max_date =  Forecast.objects.aggregate(max_date=Max('DateAdded'))['max_date']
    total_percentage = 0
    total_boolean = False
    min_date = None
    top_7_diseases = None
    if max_date:
        past_date = max_date - timedelta(days=30)
        future_data = Forecast.objects.filter(DateAdded__range=(past_date, max_date))\
                        .values('Disease', 'Disease_count')
        min_date = future_data.aggregate(min_date=Min('DateAdded'))['min_date']
        min_date_comparison = min_date - timedelta(days=30)
       
        future_disease_totals = defaultdict(lambda: {'count': 0, 'percentage': 0, 'boolean': False})
        past_prediction_dates = Checkupandappointment.objects.filter(DateAdded__range=(min_date_comparison, min_date)).values().annotate(Disease_count=Count('Disease'))
        future_prediction_date = 0
        past_prediction_date = {}
       
        for entry in future_data:
      
            disease = entry['Disease']
            disease_count = entry['Disease_count']
            
    
            future_disease_totals[disease]['count'] += disease_count
            future_prediction_date += disease_count
            past_prediction_date = {disease:0}

            for data in past_prediction_dates.filter(Disease=disease):
                if disease in past_prediction_date.keys()  :
                    pass
                past_prediction_date[disease] += data['Disease_count']
            
        
            past_data = Checkupandappointment.objects.filter(DateAdded=min_date_comparison, Disease=disease).values('Disease').annotate(Disease_count=Count('Disease')).order_by('Disease_count').first()
            comparison_count = past_data['Disease_count'] if past_data else 0
            
        
            forecast_comparison = Forecast.objects.filter(DateAdded=min_date_comparison, Disease=disease).values().first()
            forecast_count = forecast_comparison['Disease_count'] if forecast_comparison else 0
            
    
            future_disease_totals[disease]['percentage'] = 100 if comparison_count == 0 else int((abs(forecast_count - comparison_count) / comparison_count) * 100)
            
       
            future_disease_totals[disease]['boolean'] = past_prediction_date[disease] < future_prediction_date

            total_percentage = 100 if future_disease_totals['total']['count'] == 0 else int((abs(future_disease_totals['total']['percentage'] - future_disease_totals['total']['count']) / future_disease_totals['total']['count']) * 100)
            total_boolean = past_prediction_date[disease]  > future_prediction_date
            
    
        if 'total' in future_disease_totals:
            future_disease_totals.pop('total')

        # Sort the diseases by their total counts
        sorted_diseases = sorted(future_disease_totals.items(), key=lambda x: x[1]['count'], reverse=True)
    

        # Take the top 7 diseases
        top_7_diseases = sorted_diseases[:7]
        
   



    
    




   
    

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
            data['Patient_count'] = top_patient_courses.get('Patient_count', 0) 
        else:
            data['PatientCOURSE'] = "Unidentified"
            data['Patient_count'] = 0
       
        dataset.append(data)

    context = {
        'total_percentage':total_percentage,
        'total_boolean':total_boolean,
            'max_date': max_date,
           'min_date': min_date,
           'patient_count_week':recent,
            'all_courses':All_Courses,
           'all_disease':All_Disease,
           'top_disease':top_7_diseases,
            'Patient_course':dataset,
            'total_count':total_count,
            'user_model': user_model,
        }
        
    return render(request, 'index/dashboard.html', context)

@csrf_exempt
def update_chart(request):
    if request.method == 'POST':
        result_list = []
        
        if request.POST.get('all'):
            start_date_str, end_date_str = request.POST.get('all').split(" - ")
            date_str = request.POST.get('all')
            start_date = datetime.strptime(start_date_str, "%m-%d-%Y")
            end_date = datetime.strptime(end_date_str, "%m-%d-%Y")
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")
            forecast_model = Forecast.objects.filter(DateAdded__range=[start_date, end_date])
            if forecast_model:
                forecast_model = Filter(forecast_model,['DateAdded','Disease','Disease_count'],date=date_str,target='Disease',overall=True).clean_data_filter()
                result_list = forecast_model
            return JsonResponse(result_list,safe=False) 
        if request.POST.get('selected_disease') and request.POST.get('selected_disease_date'):
            selected_disease = request.POST.get('selected_disease')
            selected_disease_date_str = request.POST.get('selected_disease_date')   
            selected_disease_start_date_str, selected_disease_end_date_str = selected_disease_date_str.split(" - ")
            selected_disease_start_date = datetime.strptime(selected_disease_start_date_str, "%m-%d-%Y")
            selected_disease_end_date = datetime.strptime(selected_disease_end_date_str, "%m-%d-%Y")

            selected_disease_start_date = selected_disease_start_date.strftime("%Y-%m-%d")
            selected_disease_end_date = selected_disease_end_date.strftime("%Y-%m-%d")

            forecast_model = Forecast.objects.filter(Disease=selected_disease,DateAdded__range=[selected_disease_start_date,selected_disease_end_date])
            checkupandappointment_model =Checkupandappointment.objects.filter(Disease=selected_disease,DateAdded__range=[selected_disease_start_date,selected_disease_end_date])
            if forecast_model or checkupandappointment_model:
        
                forecast_model = Filter(forecast_model,['DateAdded','Disease','Disease_count'],date=selected_disease_date_str,target='Disease',overall=True).clean_data_filter()
                patient_model = Filter(checkupandappointment_model,['DateAdded','Disease'],target='Disease',date=selected_disease_date_str).clean_data_filter() 
    
        
                combined_data = defaultdict(lambda: {'DateAdded': None, 'Actual': 0.0, 'Predict': 0.0})
                    
                for data1 in patient_model:
                    date = data1['DateAdded']
                    combined_data[date]['DateAdded'] = date
                    combined_data[date]['Actual'] = data1['Disease_count']

    
                for data2 in forecast_model:
                    date = data2['DateAdded']
                    if date in combined_data:
                        combined_data[date]['DateAdded'] = date
                        combined_data[date]['Predict'] = data2['Disease_count']
                        
    
                    
                result_list = list(combined_data.values())
             
            

            return JsonResponse(result_list,safe=False)
    return redirect(reverse('dashboard:index'))


def update_forecast(request):   
    if settings.FILE_UPLOAD_IN_PROGRESS:
        def run():
            current_date = datetime.now().date()
            window_start = current_date - timedelta(days=365 * 2)
            all_disease = Checkupandappointment.objects.values('Disease').distinct().order_by('Disease')

            if all_disease:
                for disease in all_disease:
                    disease_name = disease['Disease']
                   
                    disease_data = Checkupandappointment.objects.filter(
                        Q(Disease=disease_name) & Q(DateAdded__range=[window_start, current_date])
                    )
                    rrn = RNNModel(disease_data, ['DateAdded', 'Disease'], target='Disease', name=disease_name,startdate=window_start,enddate=current_date)
                    rrn.train()
                    prediction = rrn.predict()
            else:
                return HttpResponse('Could not train the data because it is empty')
            
        date_today = datetime.today().date()
        forecast_date = Forecast.objects.all().order_by('DateAdded').values('DateAdded').last()
        check_model = Checkupandappointment.objects.all().first()

        if check_model is None:
            return JsonResponse({'message': 'No data to forecast'})
        elif forecast_date is None and check_model:
            print('No data found for forecasting')
            run()
            return HttpResponse('Update complete')
        elif date_today == forecast_date['DateAdded']:
            print('Have forecast data')
            run()
            return HttpResponse('Update complete')
        else:
            print('Waiting for the Schedule...........')
            return JsonResponse({'message': 'Waiting for the Schedule...........'})
    else:
        return HttpResponse('Update complete')

@login_required(login_url='/account/')
def ExcelFileUpload(request):
    fileupload = os.path.join(settings.MEDIA_ROOT, 'uploads_record')
    if request.method == 'POST':
        settings.FILE_UPLOAD_IN_PROGRESS = False
        form = ExcelFileform(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']
            filename = file.name
            i = 1
            while os.path.isfile(os.path.join(fileupload, filename)):

                basename, type = file.name.split('.')
                filename = basename + f'({i})' + '.' + type
                i = i + 1

            else:

                with open(os.path.join(fileupload, filename), 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                    destination.seek(0, 2)

            with open(os.path.join(fileupload, filename), 'rb+') as destination:
                workbook = openpyxl.load_workbook(destination)
                worksheet = workbook.active

                for row in worksheet.iter_rows(min_row=2, values_only=False):
                    # save the date into the database
                    ContactInformation_model = ContactInformation.objects.create(
                        Address=row[6].value if row[6].value else None,
                        State=row[7].value if row[7].value else None,
                        Country=row[8].value if row[8].value else None,
                        Pincode=int(row[9].value) if row[9].value else None,
                        Phonenumber=row[10].value if row[10].value else None,
                    ).save()

                    MedicalHistory_model = MedicalHistory.objects.create(

                        Allergies=row[15].value if row[15].value else None,
                        Medications=row[16].value if row[16].value else None,
                        Medicalconditions=row[17].value if row[17].value else None,
                        Familyhistory=row[18].value if row[18].value else None,
                    ).save()

                    Recentlabhistory_model = Recentlabhistory.objects.create(
                        Fastingbloodsugar=row[11].value if row[11].value else None,
                        Bloodpressure=row[12].value if row[12].value else None,
                        Hba1c=row[13].value if row[13].value else None,
                        Cholesterol=row[14].value if row[14].value else None,
                    ).save()

                    Checkupandappointment_model = Checkupandappointment.objects.create(
                        Disease=row[19].value if row[19].value else None,
                        DateAdded=row[20].value if row[20].value else None,
                    ).save()
                    ContactInformation_model = ContactInformation.objects.order_by(
                        '-DateAdded').first()
                    MedicalHistory_model = MedicalHistory.objects.order_by(
                        '-DateAdded').first()
                    Recentlabhistory_model = Recentlabhistory.objects.order_by(
                        '-DateAdded').first()
                    Checkupandappointment_model = Checkupandappointment.objects.order_by(
                        '-DateAdded').first()

                    Patientinformation_model = Patientinformation.objects.create(
                        PatientNAME=row[0].value if row[0].value else None,
                        PatientAGE=int(row[1].value) if row[1].value else None,
                        PatientCOURSE=row[2].value if row[2].value else None,
                        PatientBirthday=row[3].value if row[3].value else None,
                        PatientYEARLEVEL=row[4].value if row[4].value else None,
                        PatientGender=row[5].value if row[5].value else None,
                        ContactInformationID=ContactInformation_model,
                        CheckupandappointmentID=Checkupandappointment_model,
                        RecentlabhistoryID=Recentlabhistory_model,
                        MedicalHistoryID=MedicalHistory_model,
                    )
                    Patientinformation_model.save()

                    Patientinformation_model = Patientinformation.objects.filter(
                        PatientNAME=row[0]).first()

                    print('upload successful................')
            settings.FILE_UPLOAD_IN_PROGRESS = True
            messages.success(request, file.name + ' uploaded successfully')
           

            return redirect(reverse('dashboard:index'))

        else:
            messages.error(
                request, 'The uploaded file must be in Excel or CSV format.')

        return redirect(reverse('dashboard:index'))

    else:
        form = ExcelFileform()
        return render(request, 'index/dashboard.html', {'form': form})
