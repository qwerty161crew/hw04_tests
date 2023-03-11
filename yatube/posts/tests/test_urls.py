from django.test import TestCase, Client
from django.urls import reverse

from http import HTTPStatus

from ..models import Post, Group, User

GROUP_TITLE = 'Тестовая группа'
USERNAME = 'post_author'
SLUG = 'test-slug'
INDEX = reverse('posts:index')
PROFILE = reverse('posts:profile',
                  kwargs={'username': USERNAME})
GROUP = reverse('posts:group_posts',
                kwargs={'slug': SLUG})
LOGIN = reverse('users:login')
CREATE = reverse('posts:post_create')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='post_author')
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )
        cls.POST_EDIT = reverse('posts:post_edit',
                                kwargs={'post_id': cls.post.id})
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        TEMPLATE_NAME = [
            ['posts/index.html', INDEX, self.guest_client],
            ['posts/group_list.html', GROUP,
             self.guest_client],
            ['posts/profile.html', PROFILE,
             self.guest_client],
            ['posts/post_detail.html', self.POST_DETAIL,
             self.guest_client],
            ['posts/create_post.html', CREATE,
             self.authorized_client],
            ['posts/create_post.html',
                self.POST_EDIT,
                self.authorized_client],
        ]
        for template, address, user in TEMPLATE_NAME:
            with self.subTest(address=address):
                response = user.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirects(self):
        REDIRECT_URLS = [[LOGIN + '?next=/create/',
                          CREATE],
                         [LOGIN
                          + f'?next=/posts/{self.post.id}/edit/',
                          self.POST_EDIT]
                         ]
        for destination, address in REDIRECT_URLS:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, destination)

    def test_urs_exists_at_desired_location_guest(self):
        """Проверка доступа на станицы, авторизированного пользователя и
        гостя"""
        templates_url_names = [
            [INDEX, self.guest_client, HTTPStatus.OK],
            [GROUP,
             self.guest_client, HTTPStatus.OK],
            [PROFILE, self.authorized_client, HTTPStatus.OK],
            [PROFILE,
             self.guest_client, HTTPStatus.OK],
            [CREATE,
             self.guest_client, HTTPStatus.FOUND],
            [CREATE,
             self.authorized_client, HTTPStatus.OK],
            [self.POST_EDIT,
             self.authorized_client, HTTPStatus.OK],
            [self.POST_EDIT,
             self.guest_client, HTTPStatus.FOUND],
        ]
        for url, user_status, answer in templates_url_names:
            with self.subTest(url=url):
                self.assertEqual(user_status.get(url).status_code, answer)
