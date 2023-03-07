from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POST_ID = 1
        cls.USERNAME = 'post_author'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.TEMPLATE_NAME = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_posts', kwargs={'slug': cls.GROUP_SLUG}),
            'posts/profile.html': reverse('posts:profile', kwargs={'username': cls.USERNAME}),
            'posts/post_detail.html': reverse('posts:post_detail', kwargs={'post_id': cls.POST_ID}),
        }
        cls.TEMPLATE_NAME_AUTH = {
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html'
        }
        cls.user = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам

        for template, address in self.TEMPLATE_NAME.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_auth(self):
        for address, template in self.TEMPLATE_NAME_AUTH.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
