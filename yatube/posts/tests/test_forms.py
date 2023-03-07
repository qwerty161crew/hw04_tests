from django.test import Client, TestCase
from django.urls import reverse
from django.test import Client, TestCase
from django import forms

from ..models import Post, Group, User


class PostFromTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USERNAME = 'post_author'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.post_author = User.objects.create_user(
            username=cls.USERNAME,
        )
        cls.user = User.objects.create_user(username='authe')
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
        self.URLS = {'post_create': reverse('posts:post_create'),
                     'profile': reverse('posts:profile',
                                        kwargs={'username': self.USERNAME})}
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_count_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            self.URLS.get('post_create'),
            data=form_data,
            form=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.URLS.get('profile'))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_post_edit_form(self):        # post_count = Post.objects.count()
        # self.assertEqual(Post.objects.count(), post_count + 1)
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        post = Post.objects.get(id=post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])
        

    def test_post_create_pages_show_correct_context(self):
        """Шаблон task_detail сформирован с правильным контекстом."""
        response = self.authorized_user.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
