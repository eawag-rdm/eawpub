# _*_ coding: utf-8 _*_

import json
import ldap
from pprint import pprint
import math
import requests

class EawagPublications(object):
    "Handles publication updates for Eawag via Scopus"
    def __init__(self):
        with open("../config.json") as con_file:
            self.apikey = json.load(con_file)['apikey']
        self.afi = '60002612' # Eawags affiliation ID
        self.baseuri = 'http://api.elsevier.com/content/search/scopus'
        self.headers = {'X-ELS-APIKey': self.apikey}
        self.maxentries = 200

    def get_since(self, since):
        """ Returns all publications since year 'since'"""
        query = ('AF-ID({afi}) '
                 'AND PUBYEAR > {since} '
                 'OR PUBYEAR = {since}'.format(afi=self.afi, since=since))
        
        # get number of records    
        res = requests.get(self.baseuri, headers=self.headers,
                   params={'query': query, 'start': 0, 'count': 1})
        nfound = int(res.json()['search-results']['opensearch:totalResults'])
        print("Found {} publications since {}.".format(nfound, since))

        # iterate
        iterations = int(math.ceil(float(nfound) / self.maxentries))
        publications = []
        for i in range(0, iterations):
            print("Requesting batch no {}/{}".format(i+1, iterations))
            res = requests.get(self.baseuri, headers=self.headers,
                               params={'query': query,
                                       'start': i*self.maxentries,
                                       'count': self.maxentries})
            publications.extend(res.json()['search-results']['entry'])
        print("Retrieved {} publications.".format(len(publications)))
        return(publications)
    
    def filter_doi(self, publist):
        return [p['prism:doi'] for p in publist]

    def query_xref(self, doilist):
        doclist = []
        for i, doi in enumerate(doilist):
            print("Crossref query {} of {}".format(i+1, len(doilist)))
            doclist.append(requests.get('http://api.crossref.org/works/{}'
                                        .format(doi)))
        return [d.json()['message'] for d in doclist]

    def filter_doclist(self, doclist):
        def mk_authors(auth):
            return 'X'
        
        docs = [{'url': rj.get('URL'), 'authors': mk_authors(rj.get('author')),
                 'created': rj.get('created').get('date-parts'),
                 'title': rj.get('title'),
                 'container': rj.get('short-container-title'),
                 'volume': rj.get('volume'),
                 'page': rj.get('page')} for rj in doclist]

        return(docs)

class EawagLdap(object):
    def __init__(self, conffile):
        with open(conffile, 'r') as f:
            config = json.load(f)
        self.ldap_uri = config['ldap_uri']
        self.ldap_base_dn = config['ldap_base_dn']
        self.ldap_auth_dn = config['ldap_auth_dn']
        self.ldap_auth_password = config['ldap_auth_password']
        self.l = ldap.initialize(self.ldap_uri)
        self.l.bind_s(self.ldap_auth_dn, self.ldap_auth_password)


    def box_author(self, authord):
        first = authord.get('given')
        last = authord.get('family')
        # search for last name
        res = l.search_s(ldap_base_dn, ldap.SCOPE_SUBTREE,
                         '(sn={})'.format(last))
        print(res)


ldap = EawagLdap('../ldap_config.json')
epub = EawagPublications()
doilist = epub.filter_doi(epub.get_since(2017))
docs = epub.query_xref(doilist)
docs1 = epub.filter_doclist(docs)









# ldap_search_filter='sAMAccountName={login}'

# def get_departments():
#     res = l.search_s(ldap_base_dn, ldap.SCOPE_SUBTREE,
#                      '(dn=*)',
#                      ['company', 'department', 'departmentNumber'])
#     return res

# res = get_departments()


# res = l.search_s(ldap_base_dn, ldap.SCOPE_SUBTREE, '(sAMAccountName=vonwalha)')


# def ldap_get_dept(author):
    
        



