import json
import urllib, urllib2
from rango.keys import BING_API_KEY

def run_query(search_terms):
    # Specify the base
    root_url = 'https://api.datamarket.azure.com/Bing/Search/'
    source = 'Web'

    # Specify results_per_page and offset
    results_per_page = 10
    offset = 0 #offest = 11 would start the returned results from page 2

    # wrap quotes around our query terms as required by bing_api
    # The query we will use is then stored in a variable query
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # construct the latter part of our request url
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
                    root_url,
                    source,
                    results_per_page,
                    offset,
                    query)
    print search_url
    # set authentication with bing servers
    # username must be a blank string
    username = ''

    # create a password manager which handles authentication for us
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)

    # create our results list which we will populate
    results = []

    try:
    # Prepare for connecting with bing servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    # Connect to the server and read the response generated
        response = urllib2.urlopen(search_url).read()

    # Convert the string response to a python dictionary object
        json_response = json.loads(response)

    # Loop through each page returned, populating our results
        for result in json_response['d']['results']:
            results.append({
                           'title': result['Title'],
                           'link':result['Url'],
                           'summary':result['Description']})


    # Catch the URLException - something went wrong during connecting!
    except urllib2.URLError, e:
        print "Error while connecting to bing search.", e

    # Return the list of results to the calling function
    return results

    if __name__ == '__main__':
        print "Please enter your search terms"
        search_terms = sys.argv[1:]
        rank = 0
        results = run_query(search_terms)[:10]
        for result in results:
            rank += 1
            print rank
            print results['title']
            print results['link']


