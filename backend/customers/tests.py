from rest_framework import status
from rest_framework.test import APITestCase

from .models import Contact, Customer


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
