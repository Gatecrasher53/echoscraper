"""Provides login functionality to echo360 for scraper and download modules."""

import getpass                  # gets password from user silently
from lxml import html           # parses html

import requests                 # Maintains session and makes requests

class Echo360login(object):
    def __init__(self):
        self.sesh = requests.Session()

    def login(self):
        """Logs into Echo360 and authenticates for all future downloads."""

        print("Logging in to Echo360...")

        # Should get redirected to login page
        loginpage_url = 'https://echo360.org.au'

        # Load Institution login page
        
        response = self.sesh.get(loginpage_url)
        while True:
            usr = input('    Username: ')

            postData = {
                'email': usr + '@adelaide.edu.au',
                'appId': 'c08c41ee-50e3-45e8-a6e6-e9579b28f620',
            }
            response = self.sesh.post('https://login.echo360.org.au/login/institutions', data=postData)

            if "No institutions were found" not in response.text:
                break
            else:
                print("    Wrong username.")

        # Now on actual login page, re-use usr and get password, then POST to login
        attempts = 3
        while attempts > 0:
            # Get login credentials
            postData = {
                'UserName': "uofa\\" + usr,
                'Password': getpass.getpass('    Password: '),
                'AuthMethod': 'FormsAuthentication',
            }
            response = self.sesh.post(response.url, data=postData)

            if "Incorrect user ID or password." and "Enter your password." not in response.text:
                # Login Successful
                break

            print("    Incorrect password.")
            attempts = attempts - 1

            if attempts == 0:
                print("All attempts used. Exiting.")
                return False
            else:
                print("    {} attempts remaining.".format(attempts))
        
        # We get redirected to ping identity and must post SAMLRequest and RelayState response info
        response = self.autoPOST(response)

        # We get redirected again. Ping Identity gave us agentid and tokenid 
        # and now we post one last time to get to echo360
        response = self.autoPOST(response)

        print("Login Successful.")
        return True

    def autoPOST(self, response):
        """Used when post form needs to submit default values."""

        # Build html tree from response
        tree = html.fromstring(response.text)
        form = tree.xpath(".//form")[0]

        url = form.xpath("./@action")[0]
        data = {}

        for inpt in form.xpath("./input"):
            # Scrape input name and value
            name = inpt.xpath("./@name")[0]
            value = inpt.xpath("./@value")[0]

            data[name] = value
        
        # POST data
        return self.sesh.post(url, data)
