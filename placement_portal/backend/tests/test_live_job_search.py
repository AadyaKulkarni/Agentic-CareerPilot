import unittest
from app.services.job_search import _normalise_remotive

class LiveJobSearchNormalisationTests(unittest.TestCase):
    def test_remotive_keeps_attribution_and_link(self):
        job = _normalise_remotive({"id": 9, "title": "Backend Engineer", "company_name": "Remote Co",
            "candidate_required_location": "Worldwide", "url": "https://remotive.com/job/9",
            "description": "<p>Python API</p>", "salary": "$70k"})
        self.assertEqual(job["source"], "Remotive")
        self.assertTrue(job["remote"])
        self.assertEqual(job["url"], "https://remotive.com/job/9")
        self.assertIn("Python API", job["description"])

if __name__ == "__main__": unittest.main()
