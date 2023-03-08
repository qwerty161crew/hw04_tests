from django.test import Client, TestCase
from django.urls import reverse

from ..settings import PAGE_POST
from ..models import Post, Group, User

POST_RANGE = PAGE_POST + 3


class ViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USERNAME = 'post_author'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.user = User.objects.create_user(username='auth')
        cls.post_author = User.objects.create_user(
            username=cls.USERNAME,
        )
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.posts = []
        Post.objects.bulk_create([
            Post(
                text='Тестовый пост',
                author=cls.user,
            ) for i in range(POST_RANGE)
        ])

    def setUp(self):
        self.URLS = {'post_create': reverse('posts:post_create'),
                     'profile': reverse('posts:profile',
                                        kwargs={'username': self.USERNAME})}
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_users_correct_template(self):
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'auth'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), PAGE_POST)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), PAGE_POST - 7)

    def test_index_page_show_correct_context(self):
        """Шаблон task_list сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_autrhor = first_object.author
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_autrhor, self.user)

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(
            response.context['group'].description, 'Тестовое описание')
        self.assertEqual(response.context['group'].slug, 'test-slug')

    def test_profile_pages_show_correct_context(self):
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(
            response.context['page_obj'][0].author.username, 'auth')
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:profile', kwargs={
                                   'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
