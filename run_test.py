from scoring.checks import check_recruiter_email
from scoring.posting import Post
from scoring.engine import run_all_checks

# for text in [
#     "Apply via our portal",
#     "Contact jobs@ford.com",
#     "Send your resume to brightpath.hr@gmail.com.",
#     "Questions: careers@ford.com. Apply: fordhiring.team@gmail.com",
# ]:
#     print(check_recruiter_email(Post(url="https://ford.com", text=text)))

print(run_all_checks(Post(url="https://freedomforever.com/about/contact-us/")))

