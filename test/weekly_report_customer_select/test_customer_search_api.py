from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer


class WeeklyReportCustomerSelectApiTests(APITestCase):
    def test_customer_search_result_contains_fields_needed_for_weekly_report_autofill(self):
        customer = Customer.objects.create(
            client_name='Weekly Report Select Customer',
            business_model='Hunting',
            area='华东',
            city='上海',
            address='上海市测试路1号',
        )

        response = self.client.get('/api/customers/', {'search': 'Weekly Report Select'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        result = response.data['results'][0]
        self.assertEqual(result['id'], customer.id)
        self.assertEqual(result['name'], customer.client_name)
        self.assertEqual(result['region'], customer.area)
        self.assertEqual(result['city'], customer.city)
        self.assertEqual(result['address'], customer.address)
