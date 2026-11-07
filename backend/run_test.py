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

# print(run_all_checks(Post(url="https://freedomforever.com/about/contact-us/")))
text = """"
Contact us - Freedom Forever (contact: jane@ihop.top, hr@team.xyz.com and tina@portfolio.xyz) 
Get a quote Portal login Menu Close Get a quote Portal login Get a quote Portal login Why go solar Services Learning center About Home Solar 
Disruption Theory States we serve Contact us Why go solar Services Learning center About Home Solar Disruption Theory States we serve Contact us 
Facebook Instagram Linkedin YouTube Spotify Get in touch Want to get in touch? We’d love to hear from you. Here’s how you can reach us… 
Customer Support Existing Freedom Forever customer? Find quick answers and get in touch with our Customer Support team via chat or by emailing 
us at customersupport@freedomforever.com Or, you can call us at 800-685-1850 Monday – Friday, 5am – 5pm PT Closed Saturday & Sunday Email Customer Support 
Get a Quote to Go Solar Thinking about going solar? Submit your info via the link below to get started with a free personalized quote based 
on your energy use. Our company is https://zenvoy.com, you can check our careers page at: https://zenvoy.com/careers Get a Quote Media Outreach Reaching out about press coverage or a media opportunity? Email us at 
freedomforever@interdependence.com Get a Quote Get 25 years of clean, reliable solar power with Freedom Forever’s Production Guarantee! 
Your energy freedom starts here. Terms and conditions apply* " * " indicates required fields Instagram This field is for validation purposes 
and should be left unchanged. Name * First Last Email * Phone Number * Address * Street Address Address Line 2 City ZIP / Postal Code State 
* Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Guam Hawaii Idaho Illinois Indiana Iowa Kansas 
Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New Hampshire New Jersey 
New Mexico New York North Carolina North Dakota Ohio Oklahoma Oregon Pennsylvania Puerto Rico Rhode Island South Carolina South Dakota 
Tennessee Texas Utah U.S. Virgin Islands Vermont Virginia Washington West Virginia Wisconsin Wyoming Consent * I agree to the privacy policy. 
By checking the box and clicking submit, I authorize Freedom Forever LLC, it’s partners and/or affiliates to contact me via telephone calls 
and/or text messages (SMS), using auto dialing technology or otherwise, for advertising/marketing purposes, whether or not my phone 
number is on a national and/or state “Do Not Call” list. By using and interacting with this website, I agree to electronically contract and 
be bound by this website’s Terms of Use and Freedom Forever Website Privacy Policy. No purchase is required. Message and data rates may apply.
 Text STOP to opt-out. contact these persons: john@expired.badssl.com, tina@self-signed.badssl.com, manuel@untrusted-root.badssl.com and fermin@wrong.host.badssl.com Facebook Instagram Linkedin YouTube Spotify Helpful Links Why go solar About Us Services Volt Mobile 
 App Learning center Verification of Employment Podcast Dealer program Careers States we service Customer portal Contact us 
 Why go solar About Us Services Volt Mobile App Learning center Verification of Employment Podcast Dealer program Careers States we service 
 Customer portal Contact us Why go solar About Us Services Volt Mobile App Learning center Verification of Employment Podcast Dealer program 
 Careers States we service Customer portal Contact us Solar is changing fast. Stay informed. Accolades Every solar energy system is customized 
 based on many different factors, including your electricity needs, home structure, utility company rules, state and federal incentive programs,
  geography and topography. System production may be decreased by several factors that would affect the production guarantee. Refer to 
  your specific installation agreement for exclusions and/or other factors. The statements made by Freedom Forever are based on the data 
  available as of the last update to this website. Salary range: $80,000 - $110000 USD There is no express or implied dollar savings guarantee. Statements regarding tax rebates 
  and/or incentives are not guarantees you should seek advice from a tax professional regarding any rebate terms and/or qualifications.
   Warranty and repair of the system are subject strictly to the specific terms and conditions stated in your installation agreement. 
   We also have 140,000 USD for senior. For more information about the Illinois Shines Adjustable Block Program by the Illinois Power Agency, please read the Illinois Shines 
   Brochure . Legal | Website Privacy Policy | Terms of Use | Licenses 43445 Business Park Drive Suite 104, Temecula 92590 © 2021 Freedom Forever LLC 
   customersupport@freedomforever.com'
"""
print(run_all_checks(Post(url="https://www.frogtummy.com/intermediate-full-stack-laravel-developer")))