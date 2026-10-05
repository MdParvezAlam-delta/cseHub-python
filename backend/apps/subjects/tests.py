from django.test import TestCase
from django.db import connection
from rest_framework.test import APIClient

from .models import Subject


class SubjectApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.subject_data = {
            'name': 'Computer Networks',
            'author': 'Test Admin',
            'publish_date': '2026-10-05',
            'description': 'Networking fundamentals.',
            'icon': 'router',
            'domain': 'DSA',
            'content_markdown': '# Introduction',
            'code_snippets': [{'language': 'JavaScript', 'code': 'console.log("hello");'}],
            'is_active': True,
        }

    def test_public_list_returns_subject_cards(self):
        subject = Subject.objects.create(**self.subject_data)

        response = self.client.get('/api/subjects/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['id'], subject.pk)
        self.assertEqual(response.data['results'][0]['name'], subject.name)
        self.assertEqual(response.data['results'][0]['content_markdown'], subject.content_markdown)
        self.assertEqual(response.data['results'][0]['code_snippets'], subject.code_snippets)
        self.assertEqual(response.data['results'][0]['author'], 'Test Admin')
        self.assertEqual(str(response.data['results'][0]['publish_date']), '2026-10-05')
        self.assertNotIn('module_heading', response.data['results'][0])

    def test_public_list_hides_inactive_subjects(self):
        Subject.objects.create(**{**self.subject_data, 'is_active': False})

        response = self.client.get('/api/subjects/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], [])

    def test_legacy_article_and_chatbot_tables_are_removed_by_migrations(self):
        tables = set(connection.introspection.table_names())

        self.assertFalse(any(table.startswith('articles_') for table in tables))
        self.assertFalse(any(table.startswith('chatbot_') for table in tables))

    def test_removed_content_endpoints_are_not_routed(self):
        self.assertEqual(self.client.get('/api/articles/').status_code, 404)
        self.assertEqual(self.client.get('/api/categories/').status_code, 404)
        self.assertEqual(
            self.client.post('/api/admin-auth/signin/', {}, format='json').status_code,
            404,
        )

    def test_admin_accounts_table_was_removed(self):
        tables = set(connection.introspection.table_names())
        self.assertNotIn('users_adminaccount', tables)

    def test_anyone_can_create_update_and_delete_subjects(self):
        created = self.client.post('/api/subjects/', self.subject_data, format='json')
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.data['code_snippets'], self.subject_data['code_snippets'])
        self.assertEqual(created.data['author'], 'Test Admin')
        self.assertEqual(str(created.data['publish_date']), '2026-10-05')
        self.assertNotIn('module_heading', created.data)
        subject_id = created.data['id']

        updated = self.client.patch(
            f'/api/subjects/{subject_id}/',
            {
                'description': 'Updated description.',
                'content_markdown': '# Updated content',
                'is_active': False,
            },
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['description'], 'Updated description.')
        self.assertEqual(updated.data['content_markdown'], '# Updated content')
        self.assertFalse(updated.data['is_active'])

        deleted = self.client.delete(f'/api/subjects/{subject_id}/')
        self.assertEqual(deleted.status_code, 204)
        self.assertFalse(Subject.objects.filter(pk=subject_id).exists())
