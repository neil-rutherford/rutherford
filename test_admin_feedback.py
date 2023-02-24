import unittest
from config import Config
import json
from app import create_app, db
from app.models import Article, Feedback
import datetime

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    PUBLISHER_KEY = 'example_publisher_key'

class ContactAdminRoutesCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_read_feedback(self):
        a1 = Article(
            author_name='Albert Einstein',
            author_twitter='@alberteinstein',
            author_fbid='1234567890',
            title='Why the US should develop atomic weapons',
            slug='why-the-us-should-develop-atomic-weapons',
            description='Germany is working on a dangerous bomb...we should beat them to the punch.',
            image='https://en.wikipedia.org/wiki/Manhattan_Project#/media/File:Trinity_shot_color.jpg',
            section='SCIENCE',
            tags='atomic science, ww2, physics',
            body="""
            <p>In the course of the last four months it has been made probable – through the work of Joliot in France as well as Fermi and Szilard in America – that it may become possible to set up a nuclear chain reaction in a large mass of uranium, by which vast amounts of power and large quantities of new radium-like elements would be generated. Now it appears almost certain that this could be achieved in the immediate future.</p>

            <p>This new phenomenon would also lead to the construction of bombs, and it is conceivable – though much less certain – that extremely powerful bombs of a new type may thus be constructed. A single bomb of this type, carried by boat and exploded in a port, might very well destroy the whole port together with some of the surrounding territory. However, such bombs might very well prove to be too heavy for transportation by air.</p>
            """,
            created_at=datetime.datetime(1939,7,12,0,0),
            modified_at=datetime.datetime(1939,7,12,0,0)
        )
        db.session.add(a1)
        db.session.commit()
        f2 = Feedback(
            article_id=1,
            email='roosevelt@wh.gov',
            rating=5,
            comments="I found this data of such import that I have convened a Board consisting of the head of the Bureau of Standards and a chosen representative of the Army and Navy to thoroughly investigate the possibilities of your suggestion regarding the element of uranium.",
            created_at=datetime.datetime(1939,8,15,0,0)
        )
        f1 = Feedback(
            article_id=1,
            email='adolphin@germany.com',
            rating=1,
            comments="Stupid article! Also, when are you coming back to the Fatherland?",
            created_at=datetime.datetime(1940,1,1,0,0)
        )
        f3 = Feedback(
            article_id=2,
            email='stallin@ussr.com',
            rating=5,
            comments="I love cats too!",
            created_at=datetime.datetime(1945,1,1,0,0)
        )
        db.session.add(f1)
        db.session.add(f2)
        db.session.add(f3)
        db.session.commit()
        
        # Test wrong credentials
        response = self.app.test_client().post(
            '/_admin/read/feedbacks/all',
            data={
                'publisher_key': 'wrong_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Incorrect publisher_key.", response.data)

        # Test 404
        response = self.app.test_client().post(
            '/_admin/read/feedbacks/this-slug-doesn-t-exist',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Article with slug this-slug-doesn-t-exist not found.", response.data)

        # Test success on Einstein article
        response = self.app.test_client().post(
            '/_admin/read/feedbacks/why-the-us-should-develop-atomic-weapons',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['email'], 'adolphin@germany.com')
        self.assertEqual(data[1]['email'], 'roosevelt@wh.gov')

        # Test success on all
        response = self.app.test_client().post(
            '/_admin/read/feedbacks/all',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['email'], 'stallin@ussr.com')
        self.assertEqual(data[1]['email'], 'adolphin@germany.com')
        self.assertEqual(data[2]['email'], 'roosevelt@wh.gov')