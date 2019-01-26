import json
from BasicWebParser import Logins
from bs4 import BeautifulSoup


def main():

    with open("BasicWebParser/database.json", "r") as read_file:
        websiteData = json.load(read_file)

    print('Welcome.  Please enter the name of the website you wish to scrape to.')
    print('Options are: ')
    for websiteName in websiteData['websites']:
        print("     ", websiteName)

    userWebsiteSelection = input('Enter the website: ')
    scrapeSession = Logins.WebLoginandParse(websiteData, userWebsiteSelection)
    #if statement: check to see if website login is required
    if websiteData['loginRequired'][userWebsiteSelection] == 'Y':

        print("Login Required for this website.  Beginning Login Process.")
        scrapeSession.performLogin(scrapeSession.urls['loginUrl'], scrapeSession.urls['service'])
        tagsList = scrapeSession.getParseTagsAndAttributes(scrapeSession.urls['homePage'])
        scrapeSession.displayTags(tagsList, scrapeSession.urls['homePage'])

        runAgain = input("Would you like to try other tags? (y/n) ")

        while runAgain == 'y':

            tagsList = scrapeSession.getParseTagsAndAttributes(scrapeSession.urls['homePage'])
            scrapeSession.displayTags(tagsList, scrapeSession.urls['homePage'])
            runAgain = input("Would you like to try other tags? (y/n) ")

        print("Thank you for running the rig. Goodbye.")

    if websiteData['loginRequired'][userWebsiteSelection] == 'N':
        print("Login not required for this website.  Scraping...")

        tagsList = scrapeSession.getParseTagsAndAttributes(scrapeSession.urls['homePage'])
        scrapeSession.displayTags(tagsList, scrapeSession.urls['homePage'])

        runAgain = input("Would you like to try other tags? (y/n) ")

        while runAgain == 'y':

            tagsList = scrapeSession.getParseTagsAndAttributes(scrapeSession.urls['homePage'])
            scrapeSession.displayTags(tagsList, scrapeSession.urls['homePage'])
            runAgain = input("Would you like to try other tags? (y/n) ")

        print("Thank you for running the rig. Goodbye.")




if __name__=="__main__":

    main()
