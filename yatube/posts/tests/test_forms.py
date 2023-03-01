from django.test import Client, TestCase
from django.urls import reverse
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PostFromTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='authe')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_count_post(self):
        tasks_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), tasks_count)
        # Проверяем, что создалась запись с нашим слагом
        # self.assertTrue(
        #     Group.objects.filter(
        #         slug='testovyij-zagolovok',
        #         ).exists()
        # )
        # Подготавливаем данные для передачи в форму

        form_data = {
            'text': 'Тестовый пост',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            form=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'authe'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
