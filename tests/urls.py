# coding: utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Always provide the auth system login and logout views
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    
    # test urlconf for middleware tests
    (r'^middleware/', include('regressiontests.middleware.urls')),
)

urlpatterns = patterns('tests.regressiontests.auth_decorators.views',
    (r'^auth_decorators/require_login/$', 'require_login_view'))
