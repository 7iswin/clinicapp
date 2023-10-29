from django import forms
from django.core.exceptions import ValidationError
import pandas as pd


class ExcelFileform(forms.Form):
    
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file.name.endswith('.xls') or file.name.endswith('.xlsx'):
            return file
        elif file.name.endswith('.csv'):
            try:
                pd.read_csv(file)
            except pd.errors.ParserError:
                raise ValidationError('The uploaded CSV file is not valid.')
            return file
        else:
            raise ValidationError('The uploaded file must be in Excel or CSV format.')
        
