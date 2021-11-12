import json
import requests
from bs4 import BeautifulSoup
from webparse import printer
#websites are stored in JSON file.
#'loginURL' is the key to access URLs
class WebLoginandParse:

    # webData is entire JSON tree
    # website is user specified website to login to
    # credentials are the credentials of the user
    # formInputs are the credentials of a site and possible he login credentials
    # urls are the urls assosiated with a site
    # headers are the headers used for requests
    # vault are the websites along with all the data for each

    def __init__(self, web_data, website):

        self.web_data = web_data
        self.website = website
        self.credentials = {}
        self.form_inputs = {}
        self.urls = {}
        self.headers = {}
        self.vault = {}
        self.current_url = ""

        #split json tree into websites dictionary and headers dictionary
        self.vault = self.web_data['websites'].copy()
        self.headers = self.web_data['headers'].copy()

        #parseing the json into somewhat useful stuff
        for k, v in self.vault[self.website].items():

            if k == 'usernameField':
                self.credentials.update({v: self.vault[self.website]['username']})

            if k == 'passwordField':
                self.credentials.update({v: self.vault[self.website]['password']})

            if k != 'passwordField' and k != 'usernameField' and k != 'username' and k != 'password':
                self.urls.update({k:v})


        print("Here are the details for " + self.website)
        printer.print_dict_key_vals(self.credentials)
        printer.print_dict_key_vals(self.urls)

        #initialize a session for this class.. to be used for all requests
        self.s = requests.session()

    #func: get the tags off of websites
    #input: web session that keeps the cookies from a login, url name from user selection or JSON dictionary
    def get_parse_tags_and_attributes(self, url_identifer):
        tag_list = []
        page_response = self.s.get(url_identifer)
        page = BeautifulSoup(page_response.text, 'html.parser')

        print("Here are the tags on this website..", page_response.url, page_response)

        for tag in page.find_all(True):
            if tag.name not in tag_list:
                print("  -  ", tag.name)
            #tagList needs not in the condition so all tags are Grabbed
            #the print is in the if for pretty printing only.
            tag_list.append(tag.name)

        user_selection = input('Enter which tags would you like to see.. separated by a comma: ')
        list_of_tags = user_selection.replace(' ', '').split(',')

        try:
            for tag in list_of_tags:
                assert(tag in tag_list), "tag selected not in list.. try again"

        except AssertionError as error:
            print(error)
            self.get_parse_tags_and_attributes(session)

        return list_of_tags


    def display_tags(self, tags, pageUrl):
        all_tags = []
        page_response = self.s.get(pageUrl)
        page_content = BeautifulSoup(page_response.text, 'html.parser')
        print("You wanted to view these tags: ")
        printer.print_list(tags)

        for tag in tags:
            #find_all returns list of tags
            all_tags.append(page_content.find_all(tag))

        for listOfTags in all_tags:
            i = 0
            print("Heres what I found for: ", tags[0])
            printer.print_list(listOfTags)

            i +=1
            #print(page)

    # By default, have user input on for this function.  In automated scripts turn it off, and pass in payload
    def get_form_inputs(self, form_url, user_input_on=True, payload={}):
        # initialize formInputs to be empty each request
        self.form_inputs = {}

        form_response = self.s.get(form_url, headers=self.headers)
        print("Grabbed form page: ", form_response.url, form_response)
        # incase you want to parse through the login page.. see below comment
        form_page_text = BeautifulSoup(form_response.text, 'html.parser')

        # <input> are the needed fields in the login form.. csrf token updates per each request
        inputs = form_page_text.find_all('input')
        # adds the csrf middleware tokens to login details.. usually stored
        # in <name> and <value> html tags
        for inputfield in inputs:
            key = inputfield.get('name')
            value = inputfield.get('value')
            self.form_inputs.update({key : value})

        # remove None type attributes
        try:
            self.form_inputs.pop(None)
        except KeyError:
            print("No nonetype attributes to be removed.")

        print("Here are the values for inputs I found")
        printer.print_dict_key_vals(self.form_inputs)

        if user_input_on == True:
            userInput = input("Do you wish to update any of these inputs further? (y/n): ")
            if userInput == "y":
                forminputSelection = str(input("Enter the input and its value like (input:value): "))

                forminputSelection = forminputSelection.split(':')
                self.form_inputs.update({forminputSelection[0]:forminputSelection[1]})
                print("Value updated.")
                printer.print_dict_key_vals(self.form_inputs)

        # this statement is for the programmer who wants to skip user input but modify
        # a name attribute
        else:
            print("Updated to your liking sir: ")
            self.form_inputs.update(payload)
            printer.print_dict_key_vals(self.form_inputs)
    # func: perform a post onto a website form (serviceUrl)
    #      by inputting data to the (formUrl)
    # formType sets the type of form post.. default is post
    # formType search performs a get request in a search bar on a site

    def perform_login(self, formUrl, serviceUrl):

        self.get_form_inputs(formUrl)
        ## DEBUG: get this exception to work without wifi -- expand these exceptions
        try:
            # updates the formInputs to contain the credentials of the user
            self.form_inputs.update(self.credentials)
            print("Here are the inputs with your credentials... ")
            printer.print_dict_key_vals(self.form_inputs)
            print("Entering " + serviceUrl + "... ")
            response = self.s.post(serviceUrl, data=self.form_inputs, headers=self.headers)

            # # DEBUG: for uploading files
            # if formType == 'FileUpload':
            #     files = {'file': open('ResumeNTmech.pdf', 'rb')}
            #     response = self.s.post(serviceUrl, data=self.formInputs, headers=self.headers, files=files)

            print("Connection established @: ", response.url, response)

            return

        except AssertionError as e:
            print("Form entry failed.. ", e)
            return

    def perform_post(self, form_url, service_url, payload, user_input_on=False):

        self.get_form_inputs(form_url, user_input_on, payload)
        print("Entering " + service_url + "... ")
        response = self.s.post(service_url, data=self.form_inputs, headers=self.headers)

        return response

    # Enter into a search form for a website, passing in formInputs gathered by formUrl
    def enter_search_form(self, form_url, search_url, payload, user_input_on=False):

        self.get_form_inputs(form_url, user_input_on, payload)

        response = self.s.get(search_url, params=self.form_inputs, headers=self.headers)
        print("Opened: " + response.url)

        return response

    def get_urls(self, page_response):

        page_text = BeautifulSoup(page_response.text, 'html.parser')

        for link in page_text.find_all('a'):
            print(link)

        print("Got all links from: ", page_response.url)





#TODO: make a perform request page.. look into more accurate parseing of the html into useful data
