import json
import requests
from bs4 import BeautifulSoup
from BasicWebParser import DataPrinter
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

    def __init__(self, webData, website):

        self.webData = webData
        self.website = website
        self.credentials = {}
        self.formInputs = {}
        self.urls = {}
        self.headers = {}
        self.vault = {}
        self.currentUrl = ""

        #split json tree into websites dictionary and headers dictionary
        self.vault = self.webData['websites'].copy()
        self.headers = self.webData['headers'].copy()

        #parseing the json into somewhat useful stuff
        for k, v in self.vault[self.website].items():

            if k == 'usernameField':
                self.credentials.update({v: self.vault[self.website]['username']})

            if k == 'passwordField':
                self.credentials.update({v: self.vault[self.website]['password']})

            if k != 'passwordField' and k != 'usernameField' and k != 'username' and k != 'password':
                self.urls.update({k:v})


        print("Here are the details for " + self.website)
        DataPrinter.PrintDictionaryKeysAndValues(self.credentials)
        DataPrinter.PrintDictionaryKeysAndValues(self.urls)

        #initialize a session for this class.. to be used for all requests
        self.s = requests.session()

    #func: get the tags off of websites
    #input: web session that keeps the cookies from a login, url name from user selection or JSON dictionary
    def getParseTagsAndAttributes(self, urlIdentifier):
        tagList = []
        pageResponse = self.s.get(urlIdentifier)
        page = BeautifulSoup(pageResponse.text, 'html.parser')

        print("Here are the tags on this website..", pageResponse.url, pageResponse)

        for tag in page.find_all(True):
            if tag.name not in tagList:
                print("  -  ", tag.name)
            #tagList needs not in the condition so all tags are Grabbed
            #the print is in the if for pretty printing only.
            tagList.append(tag.name)

        userSelection = input('Enter which tags would you like to see.. separated by a comma: ')
        listOfTags = userSelection.replace(' ', '').split(',')

        try:
            for tag in listOfTags:
                assert(tag in tagList), "tag selected not in list.. try again"

        except AssertionError as error:
            print(error)
            self.getParseTagsAndAttributes(session)

        return listOfTags


    def displayTags(self, tags, pageUrl):
        allTags = []
        pageResponse = self.s.get(pageUrl)
        pageContent = BeautifulSoup(pageResponse.text, 'html.parser')
        print("You wanted to view these tags: ")
        DataPrinter.PrintList(tags)

        for tag in tags:
            #find_all returns list of tags
            allTags.append(pageContent.find_all(tag))

        for listOfTags in allTags:
            i = 0
            print("Heres what I found for: ", tags[0])
            DataPrinter.PrintList(listOfTags)

            ++i
            #print(page)

    # By default, have user input on for this function.  In automated scripts turn it off, and pass in payload
    def getFormInputs(self, formUrl, userInputOn=True, payload={}):
        # initialize formInputs to be empty each request
        self.formInputs = {}

        formResponse = self.s.get(formUrl, headers=self.headers)
        print("Grabbed form page: ", formResponse.url, formResponse)
        # incase you want to parse through the login page.. see below comment
        formPageText = BeautifulSoup(formResponse.text, 'html.parser')

        # <input> are the needed fields in the login form.. csrf token updates per each request
        inputs = formPageText.find_all('input')
        # adds the csrf middleware tokens to login details.. usually stored
        # in <name> and <value> html tags
        for inputfield in inputs:
            key = inputfield.get('name')
            value = inputfield.get('value')
            self.formInputs.update({key : value})

        # remove None type attributes
        try:
            self.formInputs.pop(None)
        except KeyError:
            print("No nonetype attributes to be removed.")

        print("Here are the values for inputs I found")
        DataPrinter.PrintDictionaryKeysAndValues(self.formInputs)

        if userInputOn == True:
            userInput = input("Do you wish to update any of these inputs further? (y/n): ")
            if userInput == "y":
                forminputSelection = str(input("Enter the input and its value like (input:value): "))

                forminputSelection = forminputSelection.split(':')
                self.formInputs.update({forminputSelection[0]:forminputSelection[1]})
                print("Value updated.")
                DataPrinter.PrintDictionaryKeysAndValues(self.formInputs)

        # this statement is for the programmer who wants to skip user input but modify
        # a name attribute
        else:
            print("Updated to your liking sir: ")
            self.formInputs.update(payload)
            DataPrinter.PrintDictionaryKeysAndValues(self.formInputs)
    # func: perform a post onto a website form (serviceUrl)
    #      by inputting data to the (formUrl)
    # formType sets the type of form post.. default is post
    # formType search performs a get request in a search bar on a site

    def performLogin(self, formUrl, serviceUrl):

        self.getFormInputs(formUrl)
        ## DEBUG: get this exception to work without wifi -- expand these exceptions
        try:
            # updates the formInputs to contain the credentials of the user
            self.formInputs.update(self.credentials)
            print("Here are the inputs with your credentials... ")
            DataPrinter.PrintDictionaryKeysAndValues(self.formInputs)
            print("Entering " + serviceUrl + "... ")
            response = self.s.post(serviceUrl, data=self.formInputs, headers=self.headers)

            # # DEBUG: for uploading files
            # if formType == 'FileUpload':
            #     files = {'file': open('ResumeNTmech.pdf', 'rb')}
            #     response = self.s.post(serviceUrl, data=self.formInputs, headers=self.headers, files=files)

            print("Connection established @: ", response.url, response)

            return

        except AssertionError as e:
            print("Form entry failed.. ", e)
            return

    def performPost(self, formUrl, serviceUrl, payload, userInputOn=False):

        self.getFormInputs(formUrl, userInputOn, payload)
        print("Entering " + serviceUrl + "... ")
        response = self.s.post(serviceUrl, data=self.formInputs, headers=self.headers)

        return response

    # Enter into a search form for a website, passing in formInputs gathered by formUrl
    def enterSearchForm(self, formUrl, searchUrl, payload, userInputOn=False):

        self.getFormInputs(formUrl, userInputOn, payload)

        response = self.s.get(searchUrl, params=self.formInputs, headers=self.headers)
        print("Opened: " + response.url)

        return response

    def getUrls(self, pageResponse):

        pageText = BeautifulSoup(pageResponse.text, 'html.parser')

        for link in pageText.find_all('a'):
            print(link)

        print("Got all links from: ", pageResponse.url)





#TODO: make a perform request page.. look into more accurate parseing of the html into useful data
