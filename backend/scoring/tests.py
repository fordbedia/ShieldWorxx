# scoring/tests.py
from django.test import SimpleTestCase
from .checks import check_recruiter_email
from .posting import Post


class RecruiterEmailTests(SimpleTestCase):

    def run_check(self, text):
        return check_recruiter_email(Post(url="https://ford.com", text=text))

    def test_no_email(self):
        finding = self.run_check("Apply via our portal")
        self.assertEqual(finding["penalty"], 0)

    def test_free_email_at_end_of_sentence(self):
        finding = self.run_check("Send your resume to brightpath.hr@gmail.com.")
        self.assertEqual(finding["penalty"], -15)
        self.assertIn("brightpath.hr@gmail.com", finding["reason"])

    # Your turn: test_company_email and test_mixed_emails