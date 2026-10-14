import unittest
import json
import os
from app import app
from database import init_db

class GreenCampusBotTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Green Campus", response.data)
        self.assertIn(b"EcoBot", response.data)

    def test_status_endpoint(self):
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'online')
        self.assertIn('ai_provider', data)

    def test_chat_fallback(self):
        # Without OpenAI key configured, knowledge engine should answer cleanly
        response = self.client.post('/api/chat',
                                    data=json.dumps({"message": "How can I save water in college?"}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertTrue(len(data['response']) > 20)
        self.assertIn('suggestions', data)
        self.assertEqual(data['source'], 'knowledge_engine')

    def test_chat_validation(self):
        response = self.client.post('/api/chat',
                                    data=json.dumps({"message": ""}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_tips_endpoint(self):
        response = self.client.get('/api/tips')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tips', data)
        self.assertTrue(len(data['tips']) >= 10)

    def test_challenges_and_completion(self):
        # Fetch challenges
        response = self.client.get('/api/challenges')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('challenges', data)
        self.assertTrue(len(data['challenges']) >= 6)

        # Complete challenge 2
        comp_response = self.client.post('/api/challenges/complete',
                                         data=json.dumps({"challenge_id": 2, "completed": True}),
                                         content_type='application/json')
        self.assertEqual(comp_response.status_code, 200)
        comp_data = json.loads(comp_response.data)
        self.assertTrue(comp_data['success'])

    def test_stats_endpoint(self):
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('tips_count', data)
        self.assertIn('plastic_bottles_saved', data)
        self.assertIn('disclaimer', data)

    def test_feedback_submission(self):
        feedback_data = {
            "user_name": "Test Student",
            "user_role": "Student",
            "rating": 5,
            "category": "Chatbot Experience",
            "comment": "EcoBot is super helpful for hostel water conservation!"
        }
        post_res = self.client.post('/api/feedback',
                                    data=json.dumps(feedback_data),
                                    content_type='application/json')
        self.assertEqual(post_res.status_code, 201)

        get_res = self.client.get('/api/feedback')
        self.assertEqual(get_res.status_code, 200)
        fb_list = json.loads(get_res.data)
        self.assertTrue(len(fb_list['feedbacks']) > 0)

if __name__ == '__main__':
    unittest.main()
