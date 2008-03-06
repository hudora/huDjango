from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Always provide the auth system login and logout views
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    
    # test urlconf for middleware tests
    (r'^middleware/', include('regressiontests.middleware.urls')),
)
