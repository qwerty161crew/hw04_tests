from django.test import TestCase, Client

from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост который состоит из 15 сиволов',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_routes(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get('/profile/auth/')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, 200)
