import os
import sys

# Add the root directory of your project to the sys.path
sys.path.append('/path/to/capstoneV2')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django_pandas.io import read_frame
import pandas as pd
from datetime import timedelta
from django.db.models import Count

from clinic.model.forecast import Forecast
from clinic.model.patientrecord import Checkupandappointment
from filter import Filters

from datetime import date,timedelta
from django.db.models import Max
from datetime import datetime
class Filter:
    
    def __init__(self,model,*fieldnames,target=None,date='',overall=False):
        self.model = model
        self.date = date
        self.fieldnames = fieldnames
        self.target = target
        self.overall = overall

    def clean_data_filter(self):
        
        if isinstance(self.model, str):
            if self.model.endswith('.csv'):
                data_clean = pd.read_csv(self.model)
            elif self.model.endswith('.xlsx'):
                data_clean = pd.read_excel(self.model)
            else:
                raise ValueError("Unsupported file type.")
        elif isinstance(self.model, object):
            if not self.fieldnames:
                raise ValueError("fieldnames are not provided or are empty")
          
            data_clean = read_frame(self.model, fieldnames=self.fieldnames[0])

            
            
            
        else:
            raise ValueError("Unsupported data source.")
        
        date_template = ['date','dateadded','enddate','startdate','timestamp']
        dateadded_template = ['date','dateadded','startdate','timestamp']

        for column in data_clean.columns:
            if any(template in column.lower() for template in date_template):
                try:
                    data_clean[column] = pd.to_datetime(data_clean[column])
                except ValueError as e:
                    print(f"Error converting date column '{column}': {e}")
        
        try:
            start_date_str,max_date_str = self.date.split(" - ")
            start_date = datetime.strptime(start_date_str, "%m-%d-%Y")
            max_date = datetime.strptime(max_date_str, "%m-%d-%Y")
            start_date = start_date.strftime("%Y-%m-%d")
            max_date = max_date.strftime("%Y-%m-%d")
            if self.model:
                date_columns = [column for column in data_clean.columns if column.lower() in dateadded_template]
                if self.overall:
                    data_clean = data_clean.groupby('DateAdded')['Disease_count'].sum().reset_index(name='Disease_count')
                    date_range = pd.date_range(start=start_date, end=max_date, freq='D')
                    filtered_df = pd.DataFrame(date_range, columns=['DateAdded'])
                    filtered_df['Disease_count'] = 0.0
                    filtered_df = filtered_df[~filtered_df['DateAdded'].isin(data_clean['DateAdded'])]
                    filtered_df = pd.concat([filtered_df, data_clean], ignore_index=True)
                    filtered_df.sort_values('DateAdded', inplace=True) 
                    return filtered_df.to_dict(orient='records')
                
                else:
                    data_clean = data_clean.groupby([
                    date_columns[0], self.target]).size().reset_index(name=self.target+'_count')
                    name_disease=self.model.values('Disease').first()
                    new_date_range = pd.date_range(start=start_date, end=max_date, freq='D')
                    filtered_df = pd.DataFrame(new_date_range, columns=['DateAdded'])
                    filtered_df['Disease'] = name_disease['Disease']
                    filtered_df['Disease_count'] = 0.0
                    filtered_df = filtered_df[~filtered_df['DateAdded'].isin(data_clean['DateAdded'])]
                    filtered_df = pd.concat([filtered_df, data_clean], ignore_index=True)
                    filtered_df.sort_values('DateAdded', inplace=True)
                    return filtered_df.to_dict(orient='records')
            else:
                new_date_range = pd.date_range(start=start_date, end=max_date, freq='D')
                filtered_df = pd.DataFrame(new_date_range, columns=['DateAdded'])
                filtered_df['Disease'] = None
                filtered_df['Disease_count'] = 0.0
                return filtered_df.to_dict(orient='records')


          
        except ValueError as e:
            print(f'Group and axis must be same length, the {date_columns} is empty')
        
            
        
    



class Recent_Patient:
    def __init__(self,model,*fieldnames,target=None):
        self.model = model
        self.target = target
        self.fieldnames = fieldnames[0]
        self.get_data = self.year_month_day() 
        

    def year_month_day(self):
        
        model  =Filters(self.model,date_field=self.fieldnames[0])
        model_year = model.this_year()
        model_month = model.this_month()
        model_week = model.this_week()
        model_day = model.last_day()
        filter = {
            f'{self.target}_count':Count(self.target)
        }
        model_count_year = model_year.values(self.target).annotate(**filter)
        model_count_month = model_month.values(self.target).annotate(**filter)
        model_count_day = model_day.values(self.target).annotate(**filter)
        model_count_week = model_week.values(self.target).annotate(**filter)
        dataset = []
      

        for data in model_count_week:
            
            data_target = data[self.target]
            data_target_count = data[f'{self.target}_count']
            year_data = sum([x[f'{self.target}_count'] for x in model_count_year if x[self.target] == data_target])
            month_data = sum([x[f'{self.target}_count'] for x in model_count_month if x[self.target] == data_target])
            day_data = sum([x[f'{self.target}_count'] for x in model_count_day if x[self.target] == data_target])
            week_data = sum([x[f'{self.target}_count'] for x in model_count_week if x[self.target] == data_target])
            
            
            
            filter_data = {f'{self.target}':data_target}
   
            today = date.today()
            start_advance= today + timedelta(days=7)
            start_date= today + timedelta(days=7)
            forecast_count_week = Forecast.objects.filter(DateAdded__range=(today,start_advance),Disease=data_target).values('Disease_count')

            actual_count_week = Checkupandappointment.objects.filter(DateAdded__range=(start_date,today),Disease=data_target).annotate(Disease_count=Count('Disease')).values('Disease_count')
            forecast_count_week = sum([entry['Disease_count'] for entry in forecast_count_week]) if forecast_count_week.order_by().first() else 0
            actual_count_week = sum([entry['Disease_count'] for entry in actual_count_week]) if actual_count_week.order_by().first() else 0
            is_increasing = False if actual_count_week < forecast_count_week and forecast_count_week != 0   else True
            percent_increase = 0 if forecast_count_week==0 else int(abs(actual_count_week-forecast_count_week) / forecast_count_week * 100)
                
            
            data['year_data'] = year_data
            data['month_data'] = month_data
            data['day_data'] = day_data
            data['week_data'] = week_data
            data['forcasted_count']=forecast_count_week
            data['percentage'] = percent_increase
            data['is_increasing'] = is_increasing
          


            dataset.append(data)
        return dataset