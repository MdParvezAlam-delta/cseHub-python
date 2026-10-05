from django.test import TestCase
from rest_framework.test import APIClient

from apps.users.models import User
from .models import Note, Todo


class PersonalWorkspaceApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='workspace-user',
            email='workspace@example.invalid',
            password='TestPassword123!',
        )
        self.other_user = User.objects.create_user(
            username='other-workspace-user',
            email='other-workspace@example.invalid',
            password='TestPassword123!',
        )

    def test_note_crud_is_persisted_and_user_scoped(self):
        denied = self.client.get('/api/notes/')
        self.assertEqual(denied.status_code, 401)

        self.client.force_authenticate(user=self.user)
        created = self.client.post(
            '/api/notes/',
            {'title': 'Study notes', 'date': '2026-10-05', 'content': 'Graphs'},
            format='json',
        )
        self.assertEqual(created.status_code, 201)
        self.assertTrue(Note.objects.filter(pk=created.data['id'], user=self.user).exists())

        Note.objects.create(user=self.other_user, title='Private note', content='Hidden')
        listed = self.client.get('/api/notes/')
        self.assertEqual([row['title'] for row in listed.data['results']], ['Study notes'])

        updated = self.client.patch(
            f"/api/notes/{created.data['id']}/",
            {'content': 'Updated graph notes'},
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['content'], 'Updated graph notes')

    def test_todo_crud_persists_in_separate_table_and_is_user_scoped(self):
        self.client.force_authenticate(user=self.user)
        created = self.client.post(
            '/api/todos/',
            {'title': 'Review trees', 'tag': 'Study', 'completed': False},
            format='json',
        )
        self.assertEqual(created.status_code, 201)
        self.assertTrue(Todo.objects.filter(pk=created.data['id'], user=self.user).exists())
        self.assertNotEqual(Note._meta.db_table, Todo._meta.db_table)

        updated = self.client.patch(
            f"/api/todos/{created.data['id']}/",
            {'completed': True},
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        self.assertTrue(updated.data['completed'])
