from django.test import Client, TestCase
from django.urls import reverse

from ..settings import NUMBER_POSTS
from ..models import Post, Group, User

SLUG = 'test-slug'
USERNAME = 'post_author'
POST_RANGE = NUMBER_POSTS + 3
INDEX = ('posts:index')
CREATE_POST = reverse('posts:post_create')
PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
URLS = {'post_create': reverse('posts:post_create'),
        'profile': reverse('posts:profile', kwargs={'username': USERNAME})}
GROUP = reverse('posts:group_posts',
                kwargs={'slug': SLUG})


class ViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post_author = User.objects.create_user(
            username=USERNAME,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        Post.objects.bulk_create(
            Post(
                text='Тестовый пост',
                author=cls.user,
                group=cls.group
            ) for i in range(POST_RANGE)
        )
        cls.POST_DETAIL = reverse('posts:post_detail',
                                  kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.authorized_client = Client()
        self.guest_client = Client()
        self.authorized_client.force_login(self.user)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), NUMBER_POSTS - 6)

    def test_group_posts_pages_show_correct_context(self):
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
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_post_in_group(self):
        responses = [
            [INDEX, 'page_obj'],
            [GROUP, 'page_obj'],
            [PROFILE, 'page_obj'],
            [self.POST_DETAIL, 'post'],
        ]
        for url, obj in responses:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                if obj == 'page_obj':
                    posts = response.context[obj]
                    self.assertEqual(len(posts), 1)
                    post = posts[0]
                elif obj == 'post':
                    post = response.context['post']
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.pk, self.post.pk)
