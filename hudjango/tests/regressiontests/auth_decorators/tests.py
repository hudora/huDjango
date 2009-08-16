"""Test hudjango.auth.decorator functionality."""

from django.test import TestCase
from django.http import HttpResponse
from hudjango.auth.decorators import require_login
from django.test.client import Client
from django.contrib.auth.models import User


def fully_decorated(request):
    """Expected __doc__"""
    return HttpResponse('<html><body>dummy</body></html>')
fully_decorated.anything = "Expected __dict__"

fully_decorated = require_login(fully_decorated)


class DecoratorsTest(TestCase):

    def test_attributes(self):
        """
        Tests that django decorators set certain attributes of the wrapped
        function.
        """
        self.assertEquals(fully_decorated.__name__, 'fully_decorated')
        self.assertEquals(fully_decorated.__doc__, 'Expected __doc__')
        self.assertEquals(fully_decorated.__dict__['anything'], 'Expected __dict__')

    def test_require_login(self):
        """
        Verifies that an unauthenticated user attempting to access a
        login_required view gets redirected to the login page and that
        an authenticated user is let through.
        """
        
        view_url = '/auth_decorators/require_login/'
        client = Client()
        user = User.objects.create_user('testuser', 'nobody@hudora.de', 'testpassword')
        user.save()
        
        # unauthenticated
        response = client.get(view_url)
        self.assertEqual(response.status_code, 401)
        
        # HTTP-authenticated
        auth = 'basic %s' % 'testuser:testpassword'.encode('base64')
        response = client.get(view_url, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'access!')
        
        # Django/Session-authenticated
        client = Client()
        client.login(username='testuser', password='testpassword')
        response = client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'access!')
        
        # mismatch between session and HTTP-authentication, invalid http auth
        client = Client()
        client.login(username='testuser', password='testpassword')
        auth = 'basic %s' % 'nouser:nopassword'.encode('base64')
        response = client.get(view_url, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 401)
        self.assertNotContains(response, 'access!', status_code=401)
        
        # invalid HTTP-authentication
        client = Client()
        client.login(username='testuser', password='testpassword')
        auth = 'basic %s' % 'nouser:nopassword'.encode('base64')
        response = client.get(view_url, HTTP_AUTHORIZATION=auth)
        self.assertEqual(response.status_code, 401)
        self.assertNotContains(response, 'access!', status_code=401)
