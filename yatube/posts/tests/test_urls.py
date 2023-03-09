from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USERNAME = 'post_author'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'

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
        cls.TEMPLATE_NAME = [
            ['posts/index.html', reverse('posts:index'), 'all'],
            ['posts/group_list.html', reverse('posts:group_posts',
                                              kwargs={'slug': cls.GROUP_SLUG}),
             'all'],
            ['posts/profile.html', reverse('posts:profile',
                                           kwargs={'username': cls.USERNAME}),
             'all'],
            ['posts/post_detail.html',
             reverse('posts:post_detail', kwargs={'post_id': cls.post.id}),
             'all'],
            ['posts/create_post.html', reverse('posts:post_create'), 'auth'],
            ['posts/create_post.html',
                reverse('posts:post_edit', kwargs={'post_id': cls.post.id}),
                'auth'],
        ]
        cls.REDIRECT_URLS = [[reverse('users:login') + '?next=/create/',
                              reverse('posts:post_create')],
                             [reverse('users:login')
                              + f'?next=/posts/{cls.post.id}/edit/',
                              reverse('posts:post_edit',
                                      kwargs={'post_id': cls.post.id})]
                             ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам

        for template, address, user in self.TEMPLATE_NAME:
            with self.subTest(address=address):
                if user == 'auth':
                    response = self.authorized_client.get(address)
                else:
                    response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirects(self):
        for destination, address in self.REDIRECT_URLS:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, destination)
