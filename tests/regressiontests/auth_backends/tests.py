__test__ = {'API_TESTS': """
# >>> from auth.backends import EmailBackend
# >>> backend = EmailBackend()
# >>> repr(backend.authenticate(username='foo', password='testpw'))
# 'None'

# >>> from django.contrib.auth.models import User, AnonymousUser
# >>> u = User.objects.create_user('authtestuser', 'authtest@example.com', 'testpw')
# >>> u.save()
# 
# >>> repr(backend.authenticate(username='foo', password='testpw'))
# 'None'
# >>> repr(backend.authenticate(username='authtest@example.com', password='wrong'))
# 'None'
# >>> repr(backend.authenticate(username='authtestuser', password='wrong'))
# 'None'
# 
# 
# We can login with username
# >>> backend.authenticate(username='authtestuser', password='testpw').username
# u'authtestuser'
# 
# And we can log in with email adress
# >>> backend.authenticate(username='authtest@example.com', password='testpw').username
# u'authtestuser'
# 
# If a E-Mail adress appears twice in the database login by that E-Mail address is disabled.
# >>> u2 = User.objects.create_user('authtestuser2', 'authtest@example.com', 'testpw')
# >>> u2.save()
# >>> repr(backend.authenticate(username='authtest@example.com', password='testpw'))
# 'None'
# 
# But we still can log in with the username.
# >>> backend.authenticate(username='authtestuser', password='testpw').username
# u'authtestuser'
# >>> backend.authenticate(username='authtestuser2', password='testpw').username
# u'authtestuser2'
# 
# 
# 
# This LDAP tests actually need an LDAP-Server to run.
# >>> from auth.backends import ZimbraBackend
# >>> backend = ZimbraBackend()
# >>> repr(backend.authenticate(username='foo', password='testpw'))
# 'None'
# >>> len(User.objects.filter(email='md@hudora.de'))
# 0
# >>> repr(backend.authenticate(username='md@hudora.de', password='testpw'))
# 'None'
# >>> backend.authenticate(username='md@hudora.de', password='GEHEIM').username
# 'm.dornseif'
# 
# Does it work twice? (second time we get back an unicode object ...)
# >>> backend.authenticate(username='md@hudora.de', password='GEHEIM').username
# u'm.dornseif'
# 

"""}
