import unittest
from app import app

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_register(self):
        response = self.app.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'contactInfo': 'test@example.com'
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', response.get_data(as_text=True))

    def test_login(self):
        self.app.post('/auth/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'contactInfo': 'test@example.com'
        })
        response = self.app.post('/auth/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

if __name__ == '__main__':
    unittest.main()
