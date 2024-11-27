import unittest
from app import app

class TestJobSearch(unittest.TestCase):
    
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_job_search_route(self):
        response = self.client.post('/student/job_search/result', data={})
        self.assertEqual(response.status_code, 200)

    def test_job_role_required(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': '',
            'minSalary': 50000,
            'maxSalary': 100000,
            'location': 'New York'
        })
        self.assertIn(b'Job Role is required', response.data)

    def test_min_salary_less_than_max_salary(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Software Engineer',
            'minSalary': 60000,
            'maxSalary': 50000,
            'location': 'San Francisco'
        })
        self.assertIn(b'Minimum salary must be less than or equal to maximum salary', response.data)

    def test_valid_job_role_input(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Software Engineer',
            'minSalary': '',
            'maxSalary': '',
            'location': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_job_role_input(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': '12345',
            'minSalary': '',
            'maxSalary': '',
            'location': ''
        })
        self.assertIn(b'Invalid job role input', response.data)

    def test_min_salary_boundary(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Data Scientist',
            'minSalary': 0,
            'maxSalary': 50000,
            'location': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_negative_min_salary(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Data Scientist',
            'minSalary': -5000,
            'maxSalary': 50000,
            'location': ''
        })
        self.assertIn(b'Salary cannot be negative', response.data)

    def test_empty_location_field(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Software Engineer',
            'minSalary': 50000,
            'maxSalary': 100000,
            'location': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_special_characters_in_job_role(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Soft@ware Engineer',
            'minSalary': '',
            'maxSalary': '',
            'location': ''
        })
        self.assertIn(b'Invalid characters in job role', response.data)

    def test_sql_injection_in_job_role(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': "'; DROP TABLE users;",
            'minSalary': '',
            'maxSalary': '',
            'location': ''
        })
        self.assertIn(b'Invalid input detected', response.data)

    def test_large_salary_values(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Data Scientist',
            'minSalary': 999999999,
            'maxSalary': 999999999,
            'location': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_valid_all_fields(self):
        response = self.client.post('/student/job_search/result', data={
            'job_role': 'Data Scientist',
            'minSalary': 60000,
            'maxSalary': 120000,
            'location': 'New York'
        })
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
