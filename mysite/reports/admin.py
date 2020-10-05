

from django.contrib import admin
from .models import ContentReport,UserReport
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.utils.html import format_html


from django.contrib.admin import SimpleListFilter

class ContentFilter(SimpleListFilter):
    title = 'Content Type' # or use _('country') for translated title
    parameter_name = 'content'

    def lookups(self, request, model_admin):
        data = []
        qs = ContentType.objects.filter(app_label='netizen')   
      
        for c in qs:
            data.append([c.model, c.model.title()]) 
        qs1 = ContentType.objects.filter(app_label='comments')
        for c in qs1:
            data.append([c.model, c.model.title()])     #.title() is used for captilizinf first letter

        # print(qs)
        return data

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type__model=self.value())
        

class ContentReportsAdmin(admin.ModelAdmin):
    
    def content(self):
        content_type = ContentType.objects.get(id=self.content_type_id)
        obj = self.content_type.get_object_for_this_type(id=self.object_id)

        if content_type.app_label == 'comments':
            return obj.body

        url= obj.get_absolute_url()
        return format_html( "<a href={url}>{id}</a>", url=url,id=obj.id)

    def content_type(self):
        return self.content_type.model.title()



    list_display = ('description',content,content_type,'created',)
    list_display_links = ('description', )
    list_filter = (  'created',ContentFilter)
    search_fields = ('description','object_id')
    readonly_fields = ['description','content_type','object_id','created','user',content]

class UserReportsAdmin(admin.ModelAdmin):
    
    def profile(self):
   
        url=self.user.get_profile_url()
        return format_html( "<a href={url}>{url}</a>", url=url)

    exclude = ('reporter',)
    list_display = ('user', 'subject','description',profile)
    # list_display_links = ('description', )
    list_filter = ( 'subject',  'created',)
    search_fields = ('description','object_id')
    readonly_fields = ['user','subject','description','created',]

    

  





admin.site.register(ContentReport,ContentReportsAdmin)
admin.site.register(UserReport,UserReportsAdmin)
