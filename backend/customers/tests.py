from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from .models import Contact, Customer, CustomerRevenue, WeeklyReport, get_last_quarter_range


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

    def test_create_customer_revenue_requires_exact_customer_name_match(self):
        response = self.client.post('/api/customer-revenues/', {
            'customer_name': self.customer_a.client_name.lower(),
            'month': '2026-01-01',
            'revenue': '1000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CustomerRevenue.objects.count(), 0)

        response = self.client.post('/api/customer-revenues/', {
            'customer_name': self.customer_a.client_name,
            'month': '2026-01-01',
            'revenue': '1000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomerRevenue.objects.count(), 1)
        self.assertEqual(CustomerRevenue.objects.get().customer, self.customer_a)

    def test_import_customer_revenue_skips_unmatched_customers(self):
        csv_content = (
            'month,customer name,revenue\n'
            f'2026-01,{self.customer_a.client_name},1000\n'
            '2026-01,Unknown Customer,2000\n'
        ).encode('utf-8')
        upload = SimpleUploadedFile('revenues.csv', csv_content, content_type='text/csv')

        response = self.client.post('/api/customer-revenues/import/', {
            'file': upload,
        }, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['imported'], 1)
        self.assertEqual(response.data['skipped'], 1)
        self.assertEqual(CustomerRevenue.objects.count(), 1)
        self.assertEqual(CustomerRevenue.objects.get().customer, self.customer_a)

    def test_customer_payload_includes_last_year_and_last_quarter_revenue(self):
        today = timezone.localdate()
        last_year_month = today.replace(year=today.year - 1, month=5, day=1)
        last_quarter_start, _ = get_last_quarter_range(today)

        CustomerRevenue.objects.create(
            customer=self.customer_a,
            month=last_year_month,
            revenue='1200.00',
        )
        CustomerRevenue.objects.create(
            customer=self.customer_a,
            month=last_quarter_start,
            revenue='300.00',
        )

        response = self.client.get(f'/api/customers/{self.customer_a.id}/')

        expected_last_year = '1500.00' if last_quarter_start.year == today.year - 1 else '1200.00'
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_year_revenue'], expected_last_year)
        self.assertEqual(response.data['last_quarter_revenue'], '300.00')
