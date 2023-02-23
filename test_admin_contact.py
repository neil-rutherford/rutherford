import unittest
from config import Config
import json
from app import create_app, db
from app.models import Contact
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

    def test_create_article(self):
        # Test no contacts
        response = self.app.test_client().post(
            '/_admin/read/contacts',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)

        # Add contacts to database
        c1 = Contact(
            first_name='Joe',
            last_name='Biden',
            company='DNC',
            email='joe@wh.gov',
            opt_out=False,
            created_at=datetime.datetime(2020,1,1,0,0)
        )
        c2 = Contact(
            first_name='Barack',
            last_name='Obama',
            company='DNC',
            email='barry@wh.gov',
            opt_out=False,
            created_at=datetime.datetime(2008,1,1,0,0)
        )
        c3 = Contact(
            first_name='Donald',
            last_name='Trump',
            company='GOP',
            email='djt@wh.gov',
            opt_out=False,
            created_at=datetime.datetime(2016,1,1,0,0)
        )

        db.session.add(c1)
        db.session.add(c2)
        db.session.add(c3)
        db.session.commit()
        
        # Test success
        response = self.app.test_client().post(
            '/_admin/read/contacts',
            data={
                'publisher_key': 'example_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)
        
        self.assertEqual(data[0]['first_name'], 'Joe')
        self.assertEqual(data[0]['last_name'], 'Biden')
        self.assertEqual(data[0]['company'], 'DNC')
        self.assertEqual(data[0]['email'], 'joe@wh.gov')
        self.assertEqual(data[0]['created_at'], '2020-01-01 00:00:00')

        self.assertEqual(data[1]['first_name'], 'Donald')
        self.assertEqual(data[1]['last_name'], 'Trump')
        self.assertEqual(data[1]['company'], 'GOP')
        self.assertEqual(data[1]['email'], 'djt@wh.gov')
        self.assertEqual(data[1]['created_at'], '2016-01-01 00:00:00')

        self.assertEqual(data[2]['first_name'], 'Barack')
        self.assertEqual(data[2]['last_name'], 'Obama')
        self.assertEqual(data[2]['company'], 'DNC')
        self.assertEqual(data[2]['email'], 'barry@wh.gov')
        self.assertEqual(data[2]['created_at'], '2008-01-01 00:00:00')

        # Test wrong publisher_key
        response = self.app.test_client().post(
            '/_admin/read/contacts',
            data={
                'publisher_key': 'wrong_publisher_key'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Incorrect publisher_key.", response.data)