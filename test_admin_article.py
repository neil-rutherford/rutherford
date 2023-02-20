import unittest
from config import Config
import json
from app import create_app, db
from app.models import Article
from time import sleep

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    PUBLISHER_KEY = 'example_publisher_key'

class ArticleAdminRoutesCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_article(self):

        # Test success
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['author_name'], 'Albert Einstein')
        self.assertEqual(data['author_twitter'], '@alberteinstein')
        self.assertEqual(data['author_fbid'], '1234567890123456')
        self.assertEqual(data['title'], 'My Interesting Title')
        self.assertEqual(data['slug'], 'my-interesting-title')
        self.assertEqual(data['description'], 'My interesting description')
        self.assertEqual(data['section'], 'SECTION NAME')
        self.assertEqual(len(data['tags']), 4)
        self.assertEqual(data['tags'][-1], 'tags')
        self.assertEqual(data['body'], '<h1>This is my header</h1>\n<p>This is my paragraph</p>...')
        self.assertEqual(data['image'], 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg')
        self.assertEqual(data['created_at'], data['modified_at'])

        # Wrong publisher key
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'wrong_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 403)

        # Author name too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'A'*101,
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_name` error: Length cannot exceed 100 characters.", response.data)

        # Author name in wrong format
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'me',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_name` error: Input is in the wrong format.", response.data)

        # Author Twitter too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@'*21,
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_twitter` error: Length cannot exceed 20 characters.", response.data)

        # Author FBID too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1'*21,
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_fbid` error: Length cannot exceed 20 characters.", response.data)        

        # Title too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'A'*76,
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`title` error: Length cannot exceed 75 characters.", response.data)

        # Description too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'A'*161,
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`description` error: Length cannot exceed 160 characters.", response.data)

        # Image too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'A'*256,
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`image` error: Length cannot exceed 255 characters.", response.data)

        # Image not loading
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://www.example.com/image.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`image` error: Cannot load image.", response.data)

        # Section too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'A'*51,
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`section` error: Length cannot exceed 50 characters.", response.data)

        # Tags too long
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a'*256,
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`tags` error: Length cannot exceed 255 characters.", response.data)

        # Tags not parsing
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a. list. of. tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`tags` error: Error parsing tags. Make sure they are in a comma-separated list.", response.data)

        # Nothing in body
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': ''
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`body` error: There is nothing in the article body.", response.data)

        # Title not unique
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`title` error: The title is not unique.", response.data)

        # Test no FBID
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'J Robert Oppenheimer',
                'author_twitter': '@oppenheimer',
                'author_fbid': None,
                'title': 'Going Nuclear',
                'description': 'Hear me out...what if we split an atom?',
                'image': 'https://www.nps.gov/common/uploads/cropped_image/primary/851F8DC3-E107-F862-976C335A500A35FF.jpg?width=1600&quality=90&mode=crop',
                'section': 'Bomb-ass Shit',
                'tags': 'nukes, world war 2, usa',
                'body': '<h1>This is Oppenheimer header</h1>\n<p>This is Oppenheimer paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['author_fbid'], None)

    def test_read_article(self):
        # Test success
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 201)
        response = self.app.test_client().get(
            '/_admin/read/article/my-interesting-title'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['author_name'], 'Albert Einstein')
        self.assertEqual(data['author_twitter'], '@alberteinstein')
        self.assertEqual(data['author_fbid'], '1234567890123456')
        self.assertEqual(data['title'], 'My Interesting Title')
        self.assertEqual(data['slug'], 'my-interesting-title')
        self.assertEqual(data['description'], 'My interesting description')
        self.assertEqual(data['section'], 'SECTION NAME')
        self.assertEqual(len(data['tags']), 4)
        self.assertEqual(data['tags'][-1], 'tags')
        self.assertEqual(data['body'], '<h1>This is my header</h1>\n<p>This is my paragraph</p>')
        self.assertEqual(data['image'], 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg')
        self.assertEqual(data['created_at'], data['modified_at'])
        
        # Not found
        response = self.app.test_client().get(
            '/_admin/read/article/my-uninteresting-title'
        )
        self.assertEqual(response.status_code, 404)

    def test_update_article(self):

        # Test success
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 201)
        sleep(1)

        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Nikola Tesla',
                'author_twitter': '@nikolatesla',
                'author_fbid': '0987654321098765',
                'title': 'My Interesting Title',
                'description': 'All about electricity!',
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current',
                'body': "<h1>This is Tesla's header</h1>\n<p>This is Tesla's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['author_name'], 'Nikola Tesla')
        self.assertEqual(data['author_twitter'], '@nikolatesla')
        self.assertEqual(data['author_fbid'], '0987654321098765')
        self.assertEqual(data['description'], 'All about electricity!')
        self.assertEqual(data['image'], 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg')
        self.assertEqual(data['section'], 'SCIENCE')
        self.assertEqual(data['tags'][2], 'direct current')
        self.assertEqual(data['body'], "<h1>This is Tesla's header</h1>\n<p>This is Tesla's paragraph</p>...")
        self.assertNotEqual(data['created_at'], data['modified_at'])

        # Wrong publisher key
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'wrong_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Incorrect publisher_key.", response.data)

        # Author name too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'A'*101,
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_name` error: Length cannot exceed 100 characters.", response.data)

        # Test 404
        response = self.app.test_client().post(
            '/_admin/update/article/my-uninteresting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Article not found.", response.data)
        
        # Author name in wrong format
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'me',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_name` error: Input is in the wrong format.", response.data)

        # Author Twitter too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison...godamongmortals',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_twitter` error: Length cannot exceed 20 characters.", response.data)

        # Author FBID too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': 'a'*21,
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`author_fbid` error: Length cannot exceed 20 characters.", response.data)

        # Title too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'A'*76,
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`title` error: Length cannot exceed 75 characters.", response.data)

        # Title not unique
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My interesting title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`title` error: The title is not unique.", response.data)

        # Description too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "A"*161,
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`description` error: Length cannot exceed 160 characters.", response.data)

        # Tags too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'A'*256,
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`tags` error: Length cannot exceed 255 characters.", response.data)

        # Tags not parsing
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity. science. direct current. alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`tags` error: Error parsing tags. Make sure they are in a comma-separated list.", response.data)

        # Nothing in body
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': ""
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`body` error: There is nothing in the article body.", response.data)

        # Image doesn't load
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://www.example.com/image.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`image` error: Cannot load image.", response.data)

        # Section too long
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': '123456789098765',
                'title': 'My Interesting Title',
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'a'*51,
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"`section` error: Length cannot exceed 50 characters.", response.data)

        # Test successful reslugging and no FBID
        response = self.app.test_client().post(
            '/_admin/update/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Thomas Edison',
                'author_twitter': '@thomasedison',
                'author_fbid': None,
                'title': "Why Tesla is a villain",
                'description': "Tesla's electricity is dangerous!",
                'image': 'https://cdn.sparkfun.com/assets/9/8/d/5/4/519f9719ce395faa3c000000.jpg',
                'section': 'Science',
                'tags': 'electricity, science, direct current, alternating current',
                'body': "<h1>This is Edison's header</h1>\n<p>This is Edison's paragraph</p>"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['slug'], 'why-tesla-is-a-villain')
        self.assertEqual(data['title'], 'Why Tesla is a villain')
        self.assertEqual(data['author_fbid'], None)

    def test_delete_article(self):

        # Wrong publisher_key
        response = self.app.test_client().post(
            '/_admin/create/article',
            data={
                'publisher_key': 'example_publisher_key',
                'author_name': 'Albert Einstein',
                'author_twitter': '@alberteinstein',
                'author_fbid': '1234567890123456',
                'title': 'My Interesting Title',
                'description': 'My interesting description',
                'image': 'https://i.natgeofe.com/n/7fef9761-077c-45d0-9cca-78a984b9d614/burmese-python_thumb_3x2.jpg',
                'section': 'Section name',
                'tags': 'a, list, of, tags',
                'body': '<h1>This is my header</h1>\n<p>This is my paragraph</p>'
            }
        )
        self.assertEqual(response.status_code, 201)

        response = self.app.test_client().post(
            '/_admin/delete/article/my-interesting-article',
            data={
                'publisher_key': 'wrong_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Incorrect publisher_key.", response.data)

        # Test 404
        response = self.app.test_client().post(
            '/_admin/delete/article/my-uninteresting-article',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Article not found.", response.data)

        # Test success
        response = self.app.test_client().post(
            '/_admin/delete/article/my-interesting-title',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 204)