from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

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

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        self.TEMPLATE_NAME = [
            ['posts/index.html', reverse('posts:index'), self.guest_client],
            ['posts/group_list.html', reverse('posts:group_posts',
                                              kwargs={'slug':
                                                      self.GROUP_SLUG}),
             self.guest_client],
            ['posts/profile.html', reverse('posts:profile',
                                           kwargs={'username': self.USERNAME}),
             self.guest_client],
            ['posts/post_detail.html',
             reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
             self.guest_client],
            ['posts/create_post.html', reverse('posts:post_create'),
             self.authorized_client],
            ['posts/create_post.html',
                reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
                self.authorized_client],
        ]
        for template, address, user in self.TEMPLATE_NAME:
            with self.subTest(address=address):
                response = user.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirects(self):
        self.REDIRECT_URLS = [[reverse('users:login') + '?next=/create/',
                              reverse('posts:post_create')],
                              [reverse('users:login')
                              + f'?next=/posts/{self.post.id}/edit/',
                              reverse('posts:post_edit',
                                      kwargs={'post_id': self.post.id})]
                              ]
        for destination, address in self.REDIRECT_URLS:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, destination)

    def test_urs_exists_at_desired_location_guest(self):
        """Проверка доступа на станицы, авторизированного пользователя и
        гостя"""
        templates_url_names = [
            [reverse('posts:index'), self.guest_client, HTTPStatus.OK],
            [reverse('posts:group_posts', kwargs={'slug': self.GROUP_SLUG}),
             self.guest_client, HTTPStatus.OK],
            [reverse('posts:profile', kwargs={
                     'username': self.USERNAME}),
             self.guest_client, HTTPStatus.OK],
            [reverse('posts:profile', kwargs={
                     'username': self.USERNAME}),
             self.guest_client, HTTPStatus.OK],
            [reverse('posts:post_create'),
             self.guest_client, HTTPStatus.FOUND],
            [reverse('posts:post_create'),
             self.authorized_client, HTTPStatus.OK],
            [reverse('posts:post_edit', kwargs={
                     'post_id': self.post.id}),
             self.authorized_client, HTTPStatus.OK],
            [reverse('posts:post_edit', kwargs={
                     'post_id': self.post.id}),
             self.guest_client, HTTPStatus.FOUND],
        ]
        for url, user, answer in templates_url_names:
            with self.subTest(url=url):
                self.assertEqual(user.get(url).status_code, answer)
