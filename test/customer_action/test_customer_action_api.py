from rest_framework import status
from rest_framework.test import APITestCase

from customers.models import Customer, WeeklyReport


class CustomerActionApiTests(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            client_name='Action Target Customer',
            business_model='Hunting',
            area='华东',
            city='上海',
            address='上海市测试路1号',
        )

    def test_create_action_from_customer_creates_associated_weekly_report(self):
        response = self.client.post(
            f'/api/customers/{self.customer.id}/create-action/',
            {
                'client_name': 'Wrong Customer',
                'area': 'Wrong Area',
                'address': 'Wrong Address',
                'tasks': '供应商质量跟进',
                'definition': '新项目启动',
                'due_date': '2026-06-30',
                'responsibility': 'Sales A',
                'revenue': '100 KEUR',
                'remark': '需要继续跟进',
                'action_date': '2026-05-21',
                'action': '与客户确认下一步计划',
                'result': '客户同意推进',
                'next_step': '安排技术会议',
                'user': 'Tester',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WeeklyReport.objects.count(), 1)

        report = WeeklyReport.objects.get()
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.client_name, self.customer.client_name)
        self.assertEqual(report.area, self.customer.area)
        self.assertEqual(report.address, self.customer.address)
        self.assertEqual(report.tasks, '供应商质量跟进')
        self.assertEqual(report.definition, '新项目启动')
        self.assertEqual(str(report.due_date), '2026-06-30')
        self.assertEqual(report.responsibility, 'Sales A')
        self.assertEqual(report.revenue, '100 KEUR')
        self.assertEqual(report.remark, '需要继续跟进')
        self.assertEqual(report.status, 'in_progress')
        self.assertEqual(len(report.actions), 1)
        self.assertEqual(report.actions[0]['action_date'], '2026-05-21')
        self.assertEqual(report.actions[0]['action'], '与客户确认下一步计划')
        self.assertEqual(report.actions[0]['result'], '客户同意推进')
        self.assertEqual(report.actions[0]['next_step'], '安排技术会议')
        self.assertEqual(report.actions[0]['user'], 'Tester')
        self.assertIn('timestamp', report.actions[0])

        self.assertEqual(response.data['id'], report.id)
        self.assertEqual(response.data['client_name'], self.customer.client_name)
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertEqual(response.data['actions_count'], 1)

    def test_create_action_from_customer_requires_definition(self):
        response = self.client.post(
            f'/api/customers/{self.customer.id}/create-action/',
            {
                'action_date': '2026-05-21',
                'action': '与客户确认下一步计划',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], '项目定义不能为空')
        self.assertEqual(WeeklyReport.objects.count(), 0)

    def test_create_action_from_customer_requires_action_content(self):
        response = self.client.post(
            f'/api/customers/{self.customer.id}/create-action/',
            {
                'definition': '新项目启动',
                'action_date': '2026-05-21',
                'action': '   ',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], '行动内容不能为空')
        self.assertEqual(WeeklyReport.objects.count(), 0)
