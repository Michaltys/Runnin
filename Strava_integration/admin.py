from django.contrib import admin
from .models import Activity, Athlete, Comment, Kudoers

admin.site.register(Athlete)
admin.site.register(Activity)
admin.site.register(Comment)
admin.site.register(Kudoers)
