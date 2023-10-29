from django.urls import path
from clinic.view import studentRecord
app_name='studentrecord'
urlpatterns = [
    path('student/detail',studentRecord.record_detail,name='record'),
    path('student/list',studentRecord.record_list,name='list'),
    path('student/add',studentRecord.record_add,name='add'),
    path('student/edit',studentRecord.record_edit,name='edit'),
    path('student/delete',studentRecord.record_delete,name='delete'),
    path('generate_pdf',studentRecord.generate_pdf,name='generate_pdf'),
    path('generate_excel',studentRecord.generate_excel,name='generate_excel'),

]
