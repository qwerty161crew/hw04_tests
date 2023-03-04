from django.test import Client, TestCase
from django.urls import reverse
from django.test import Client, TestCase
from django import forms

from ..models import Post, Group, User


class PostFromTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author',
        )
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
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)

    def test_count_post(self):
        tasks_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), tasks_count)

        form_data = {
            'text': 'Тестовый пост',
            'group_id': '1',
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            form=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'post_author'}))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_create_post_form(self):
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
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == self.post_author)
        self.assertTrue(post.group_id == form_data['group'])

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
