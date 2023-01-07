import requests
from bs4 import BeautifulSoup as bs
from os import path

url = 'https://www.kijiji.ca/b-london/terrarium'
baseurl = 'https://www.kijiji.ca'
page = '/page-'
locationLondon = '/k0l1700214'
adurls = []
goodAds = []

verbose = False  # should it print out details of every ad while looking at them

# sizes in gallons and prices i am willing to pay
specs = [["20", 10], ['25', 10], ['30', 15], ['40', 2000]]


def saveAll(urls):  # saves all urls, since connection with server is cut after around 25 requests
    with open('links.txt', 'w') as file:
        for url in urls:
            file.write("%s\n" % url)


def saveGood(urls):  # formats and saves ads that fit desired criteria
    with open('goodAds.txt','w') as file:
        for url in urls:
            file.write("%s\n%s:  $%.2f\nat: %s\nposted: %s\n%s\n\n" % (url[0], url[1], url[2], url[3], url[4], url[5]))


def verify(urls):  # verify that the item fits a criteria I want

    i = 0
    try:
        for url in urls:
            print("Scraping listing "+str(i)+" : "+url)
            i += 1
            url = url.rstrip('\n')
            response = requests.get(url)
            soup = bs(response.text, "html.parser")
            try:
                title = soup.select_one("h1[class*=title-2323565163]").text
                price = soup.select_one("span[class*=currentPrice-2842943473]").text.strip('$')
                if price == "Free":
                    price = 0.0
                elif price == "Please Contact":
                    price = -1.0  # invalid value to represent the Please Contact status
                else:
                    price = float(price)
                description = soup.find('div', attrs={'itemprop': 'description'}).text
                if verbose:
                    print(title + ":    " + str(price))
                    print(description)
                # check if it is an item that I want and at a price I am willing
                valid = False
                for spec in specs:
                    if price == 0 or (price <= spec[1] and (spec[0] in str(title) or spec[0] in str(description))):
                        valid = True
                        break
                if valid:
                    if verbose: print("valid")
                    location = soup.find('span', attrs={'class': 'address-3617944557'}).text
                    date = soup.find('time').text
                    goodAds.append([url, title, price, location, date, description])

                else:
                    if verbose: print("invalid")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)
        pass


def getUrls(numPages):
    # if file with links exists, use it
    if path.exists('links.txt'):
        if verbose:
            print("getting links from file")
        with open('links.txt', 'r') as file:
            links = file.readlines()
        verify(links)

    # else get links from website, writing them to file and getting details
    else:
        if verbose:
            print("Getting links from website")
        for pageNum in range(numPages):
            url_final = url+page+str(pageNum)+locationLondon
            response = requests.get(url_final)
            soup = bs(response.text, "html.parser")
            adTitles = soup.findAll('div', attrs={'class' : 'title'})
            try:
                for link in adTitles:
                    adlink = baseurl+link.find('a')['href']
                    adurls.append(adlink)
            except Exception as e:
                print(e)

        saveAll(adurls)
        verify(adurls)


numPages = 3  # number of pages to scrape
getUrls(numPages)
saveGood(goodAds)


