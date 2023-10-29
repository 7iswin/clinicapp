from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q,Count,DateTimeField,When,Case
from django.db.models.functions import Cast

class Filters:
    def __init__(self, model, date_field=None, filters=None):
        self.model = model.objects
        self.date_field = date_field
        self.filters = filters or {}

    def get_data(self, exclude_filters=None, annotate_fields=None, order_by_fields=None,rows_number=None):
       
        # set default values for exclude_filters, annotate_fields and order_by_fields
        exclude_filters = exclude_filters or {}
        annotate_fields = annotate_fields or {}
        

        # get queryset from the model with filters applied
        if exclude_filters:
            queryset = self.model.filter(**self.filters).exclude(**exclude_filters)

        # annotate queryset with additional fields
        if annotate_fields:
            queryset = self.model.annotate(**annotate_fields)

        # order queryset by specified fields
        if order_by_fields:
            order_by_fields = ['-{}'.format(order_by_fields)] or ['-{}'.format(self.date_field)]
            queryset = self.model.order_by(*order_by_fields)
        if rows_number:
            queryset = self.model[:rows_number]
            return queryset
        # return list of queryset results
        queryset = self.model
        return queryset
        

    def this_month(self):
        today = datetime.today()
        start_of_month = today.replace(day=1)
        filters={
            '{}__gte'.format(self.date_field): start_of_month
        }
        model = self.model.filter(**filters)
        return model

        
    def last_month(self):
        today = datetime.today()
        end_of_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        start_of_last_month = end_of_last_month.replace(day=1) - timedelta(days=1)
        end_of_last_month_aware = make_aware(end_of_last_month.replace(hour=0, minute=0, second=0))
        start_of_last_month_aware = make_aware(start_of_last_month.replace(day=1, hour=23, minute=59, second=59))
        filters = Q(**{
            '{}__range'.format(self.date_field): (start_of_last_month_aware.date(), end_of_last_month_aware.date()),
        })
       
        model = self.model.filter(filters)
        return model
    def this_week(self):
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week - timedelta(days=6)
        start_of_week_aware = make_aware(start_of_week.replace(hour=0, minute=0, second=0))
        end_of_week_aware = make_aware(end_of_week.replace(hour=23, minute=59, second=59))
        filters = Q(**{
            '{}__range'.format(self.date_field): (end_of_week_aware.date(),start_of_week_aware.date()),
        })
        model = self.model.filter(filters)
        
        return model

    def last_day(self):
        start_of_day = datetime.today()
        end_of_day = start_of_day - timedelta(days=1) - timedelta(seconds=1)
        start_of_day_aware = make_aware(start_of_day)
        end_of_day_aware = make_aware(end_of_day)
       
        

        filters = Q(**{
            '{}__range'.format(self.date_field): (end_of_day_aware,start_of_day_aware)
        })
        model = self.model.filter(filters)
        return model
    
    
    def last_year(self):
        today = datetime.today()
        start_of_last_year = today.replace(year=today.year-1, month=1, day=1)
        end_of_last_year = start_of_last_year.replace(year=start_of_last_year.year+1, month=1, day=1) - timedelta(days=1)
        return self.get_data(filters={
            '{}__gte'.format(self.date_field): start_of_last_year,
            '{}__lte'.format(self.date_field): end_of_last_year,
        }, order_by_fields=[self.date_field])

    def this_year(self):
        today = datetime.today()
        start_of_year = today.replace(month=1, day=1)
        filters=Q(**{
            '{}__gte'.format(self.date_field): start_of_year
        })
        model = self.model.filter(filters)
        return model


    def custom_annotations(self, case=None, cast=None, count=None):
        if case:
            self.model.annotate(
                survive_disease=Case(
                    When(
                        **{f"{case[0]}__in": case[1]},
                        then=case[2],
                    ),
                    default=case[3],
                    output_field=case[4],
                )
            )
        if count:
            variable_name = count[0]
            field_name = count[1]
            annotations = {variable_name: Count(field_name)}
            self.model = self.model.annotate(**annotations)
            
            
        if cast:
            self.model.annotate(
                DateAdded_datetime=Cast(cast[0], output_field=cast[1])
            )
           
    

    def values(self, *args):
        self.model = self.model.values(*args)
        


    def custom_filter(self, **filters):
       self.model = self.model.filter(**filters)
       

         
