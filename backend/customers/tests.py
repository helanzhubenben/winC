from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact, Customer, WeeklyReport


class CustomerAndContactApiTests(APITestCase):
    def setUp(self):
        self.customer_a = Customer.objects.create(
            client_name='Area A Customer',
            business_model='Hunting',
            area='华东',
            city='上海',
        )
        self.customer_b = Customer.objects.create(
            client_name='Area B Customer',
            business_model='Farming',
            area='华北',
            city='北京',
        )

    def test_customer_list_filters_by_area(self):
        response = self.client.get('/api/customers/', {'area': '华北'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], self.customer_b.client_name)

    def test_contact_list_is_not_paginated(self):
        for index in range(21):
            Contact.objects.create(
                customer=self.customer_a,
                name=f'Contact {index}',
            )

        response = self.client.get('/api/contacts/', {'customer': self.customer_a.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 21)

    def test_create_weekly_report_allows_blank_optional_dates(self):
        payload = {
            'client_name': self.customer_a.client_name,
            'area': self.customer_a.area,
            'address': 'Test address',
            'tasks': 'Task A',
            'definition': 'Definition A',
            'due_date': '2026-04-20',
            'revise_date': '',
            'finish_date': '',
            'revenue': '100',
            'responsibility': 'Tester',
            'remark': 'note',
            'actions': [],
        }

        response = self.client.post('/api/weekly-reports/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = WeeklyReport.objects.get(client_name=self.customer_a.client_name, definition='Definition A')
        self.assertIsNone(report.revise_date)
        self.assertIsNone(report.finish_date)
