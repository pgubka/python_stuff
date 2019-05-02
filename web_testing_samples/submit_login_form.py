import ssl
import time
import datetime
import mechanize

# maximum 10 requests in 60 seconds
req_limit = 10        # 10 requests
window_duration = 60  # 60 seconds

uwm_url = "https://[2001:420:27c1:b02:250:56ff:feb9:faeb]"
uwm_login_uri = "/login/"

usr = "guest"
pwd = "moremoremoremore1"

    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_handle_refresh(False)
    br.addheaders = [(
		'User-agent',
		'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1'
	)]

    ssl._create_default_https_context = ssl._create_unverified_context


    br.open(url)
    br.select_form(nr=form_no)

    br.form["username"] = username
    br.form["password"] = password
    br.form["remember"] = remember

    response = br.submit()
