from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from tastypie.api import Api
import code_register

from opencollea.resources import \
    LoginResource, CourseResource, UserProfileResource, QuestionResource, \
    RegistrationDetailsResource, EtherpadNoteResource, AnswerResource, \
    CourseActivityResource
from opencollea import settings

import code_register.resources
import find_courses.resources

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(LoginResource())
v1_api.register(CourseResource())
v1_api.register(UserProfileResource())
v1_api.register(RegistrationDetailsResource())
v1_api.register(QuestionResource())
v1_api.register(AnswerResource())
v1_api.register(EtherpadNoteResource())
v1_api.register(CourseActivityResource())

# code_register's API resources
v1_api.register(code_register.resources.GenderResource())
v1_api.register(code_register.resources.LanguageResource())
v1_api.register(code_register.resources.AgeRangeResource())
v1_api.register(code_register.resources.OccupationResource())
v1_api.register(code_register.resources.AreaOfStudyResource())

# find_courses's API resources
v1_api.register(find_courses.resources.MoocCourseResource())

urlpatterns = \
    patterns('',
             #  API
             url(r'^api/', include(v1_api.urls)),
             #  Login / logout.
             url(r'^login/$', 'opencollea.views.login', name='login'),
             url(r'^logout/$', 'django.contrib.auth.views.logout',
                 name='logout'),

             url(r'^$', "opencollea.views.home", name='home'),
             url(r'^courses', "opencollea.views.courses", name='courses'),
             url(r'^users', "opencollea.views.users", name='users'),
             url(r'^forums', "opencollea.views.forums", name='forums'),

             # Examples:
             # url(r'^$', 'opencollea.views.home', name='home'),
             # url(r'^opencollea/', include('opencollea.foo.urls')),

             # Uncomment the admin/doc line below to enable admin document.:
             # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

             # Uncomment the next line to enable the admin:
             url(r'^admin/', include(admin.site.urls)),

             # List of Mooc Courses
             url(r'^find_courses/', include('find_courses.urls',
                                            namespace='find_courses')),

             url("", include("django_socketio.urls")),
             url(r'^chat/', include("chat.urls")),) \
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
