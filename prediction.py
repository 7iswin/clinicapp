import os
import sys
sys.path.append('/path/to/capstoneV2')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()
from clinic.model.forecast import Forecast
from django_pandas.io import read_frame
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from datetime import timedelta
from datetime import datetime
from clinic.model.patientrecord import Checkupandappointment
from django.db.models import Q
from sklearn.preprocessing import MinMaxScaler
class RNNModel:

    def __init__(self,model,*fieldnames,target=None,name='',startdate=None,enddate=None):
        self.name = name
        self.model = model
        self.target = target
        self.fieldnames = fieldnames
        self.startdate = startdate
        self.enddate = enddate
        self.clean_data = self.clean_data_filter()
        self.X = None
        self.train_predictions = None
        self.test_predictions = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
       

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
            if data_clean is None:
                data_clean = [{'DateAdded':self.enddate,'Disease':0}]
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


            date_columns = [column for column in data_clean.columns if column.lower() in dateadded_template]
            data_clean = data_clean.groupby([
                date_columns[0], self.target]).size().reset_index(name=self.target+'_count')
            
            
            date_range = pd.date_range(start=self.startdate, end=self.enddate, freq='D')
            filtered_df = pd.DataFrame(date_range, columns=['DateAdded'])
          
            filtered_df['Disease'] = self.name
            filtered_df['Disease_count'] = 0.0
            filtered_df = filtered_df[~filtered_df['DateAdded'].isin(data_clean['DateAdded'])]
            filtered_df = pd.concat([filtered_df, data_clean], ignore_index=True)
            filtered_df.sort_values('DateAdded', inplace=True)
        
        except ValueError as e:
            print(f'Group and axis must be same length, the {date_columns} is empty')

            
        return filtered_df

    def train(self):
        self.X = self.clean_data[self.target+'_count'].values
        self.X_train = self.X[:-29]
        self.X_test = self.X[-29:]
        self.y_train =  self.X_train[1:]
        self.X_train =  self.X_train[:-1]
        self.y_test = self.X_test[1:]
        self.X_test = self.X_test[:-1]
        self.X_train = np.reshape(self.X_train, (self.X_train.shape[0], 1, 1))
        self.X_test = np.reshape(self.X_test, (self.X_test.shape[0], 1, 1))


        

    def predict(self):
        name =  self.model[0].Disease if self.model else 'No Data'
        scaler = MinMaxScaler()
        scaler.fit_transform(self.X.reshape(-1, 1))
        model = Sequential()
        model.add(LSTM(64, input_shape=(1, self.X_train.shape[2])))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(self.X_train, self.y_train, epochs=10, batch_size=60)
        test_predictions = model.predict(self.X_test)
        predictions = scaler.inverse_transform(test_predictions)
        rounded_predictions = np.round(predictions) 
        train_loss = model.evaluate(self.X_train, self.y_train)
        test_loss = model.evaluate(self.X_test, self.y_test)
        
      
        
        dateadded_template = ['date','dateadded','startdate','timestamp']
        date_columns = [column for column in self.clean_data.columns if column.lower() in dateadded_template]
        forecast_dates = pd.date_range(start=self.clean_data[date_columns[0]].max(), periods=len(rounded_predictions)+1)[1:]
        forecast_df = pd.DataFrame({f'{date_columns[0]}': forecast_dates, f'{self.target}': \
                                  self.name,
                               f'{self.target}_count': rounded_predictions.flatten() })
    
        for forecast in forecast_df.to_dict(orient='records'):
            
            forecast_model = Forecast.objects.create(
                Disease = forecast['Disease'],
                Disease_count = forecast['Disease_count'],
                DateAdded = forecast['DateAdded'],
            )
