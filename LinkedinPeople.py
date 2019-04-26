#!/usr/bin/env python
import urllib, httplib, re, getpass, json, os
from prettytable import PrettyTable
#from termcolor import colored #except ImportError
import argparse

# https connection to url
url = "www.linkedin.com"
port = 443
conn = httplib.HTTPSConnection(url,port)

t = PrettyTable(['NAME', 'SURNAME', 'OCCUPATION'])

# output files
if not os.path.exists("output"):
	os.mkdir("output")
	os.mkdir("output/csv/")
	os.mkdir("output/dict/")
csv_directory = "output/csv/"
dict_directory = "output/dict/"
out_all = open(dict_directory+"all.txt","w")
name_surname = open(dict_directory+"name.surname.txt","w")
surname_name = open(dict_directory+"surname.name.txt","w")
n_surname = open(dict_directory+"n.surname.txt","w")
surname_n = open(dict_directory+"surname.n.txt","w")
nsurname = open(dict_directory+"nsurname.txt","w")
surnamen = open(dict_directory+"surnamen.txt","w")
csv = open(csv_directory+"all.txt","w")


# return csrf token and cookie
def getcsrf():
	conn.request("GET", "/")
	risposta = conn.getresponse()
	set_cookies = risposta.getheader('Set-Cookie')
	lang = re.search(r'lang=(.*?);',set_cookies).group(1)
	JSESSIONID = re.search(r'JSESSIONID=(.*?);',set_cookies).group(1)
	bcookie = re.search(r'bcookie=(.*?);',set_cookies).group(1)
	bscookie = re.search(r'bscookie=(.*?);',set_cookies).group(1)
	cookies = "lang="+lang+"; JSESSIONID="+JSESSIONID+"; bcookie="+bcookie+"; bscookie="+bscookie+";"
 	resp = risposta.read()
	loginCsrfParam = re.search(r'loginCsrfParam-login" type="hidden" value="(.*?)"',resp).group(1)
	return loginCsrfParam, cookies


# return login session cookie
def login(loginCsrfParam, cookies, email, password):
	data = "session_key="+email+"&session_password="+password+"&isJsEnabled=false&loginCsrfParam="+loginCsrfParam
	conn.request("POST","/uas/login-submit", data, headers={"Cookie":"%s"%cookies, "Content-Type":"application/x-www-form-urlencoded"})
	risposta = conn.getresponse()
	resp = risposta.read()
	set_cookies = risposta.getheader('Set-Cookie')
	try:
		li_at = re.search(r'li_at=(.*?);',set_cookies).group(1)
		print "[+] Login ok\n"
	except:
		print "[-] Login error!"
		exit()
	return cookies+" li_at="+li_at+";"


# save into dictionary files
def saveDictionaries(name, surname):
	name_surname.write(name+"."+surname+"\n")
	surname_name.write(surname+"."+name+"\n")
	n_surname.write(name[0]+"."+surname+"\n")
	surname_n.write(surname+"."+name[0]+"\n")
	nsurname.write(name[0]+surname+"\n")
	surnamen.write(surname+name[0]+"\n")
	out_all.write(name+"."+surname+"\n")
	out_all.write(surname+"."+name+"\n")
	out_all.write(name[0]+"."+surname+"\n")
	out_all.write(surname+"."+name[0]+"\n")
	out_all.write(name[0]+surname+"\n")
	out_all.write(surname+name[0]+"\n")


# save into csv file
def saveCSV(name, surname, occupation, email):
	csv.write(name+";"+surname+";"+occupation+";"+email+"\n")
	

# get companies and ids
def getCompanyData(ricercaf):
	conn.request("GET", "/voyager/api/typeahead/hits?q=blended&query="+ricercaf, headers={'Cookie':cookie,'Csrf-Token':Csrf_Token})
	risposta = conn.getresponse()
	resp = risposta.read()
	json_content = json.loads(resp)
	elements = json_content['elements']
	t = PrettyTable(['ID', 'NAME', 'TYPE'])
	for element in elements:
		if element["hitInfo"].get("com.linkedin.voyager.typeahead.TypeaheadCompany") is not None:
			ID = element["hitInfo"]["com.linkedin.voyager.typeahead.TypeaheadCompany"]["id"]
			text = element["text"]["text"]
			subtext = element["subtext"][10:]
			t.add_row([ID,text,subtext])
	print t


# get result pages number
def getPages():
	url = "/voyager/api/search/cluster?count=10&guides=List(v-%3EPEOPLE,facetCurrentCompany-%3E"+str(ID)+")&origin=OTHER&q=guided&start=0"
	#"/voyager/api/search/cluster?count=10&guides=List()&keywords="+queryf+"&origin=OTHER&q=guided&start=0"
	conn.request("GET", url, headers={'Cookie':cookie,'Csrf-Token':Csrf_Token,'X-RestLi-Protocol-Version':'2.0.0'})
	risposta = conn.getresponse()
	resp = risposta.read()
	json_content = json.loads(resp)
	total = json_content["elements"][0]["total"]
	if total > 1000: # limit to 1000 results
		pages = 100
	elif int(total)%10==0:
		pages = int(round(int(total)/10.0))			
	else:
		pages = int(round((int(total)/10.0)+0.5))			
	print "[*] Found " + str(total) + " total results in " + str(pages) + " pages...\n"
	return pages


# use name, surname and hunter.io pattern to get the email
def makeEmail(name,surname):
	if pattern is None:
		return "not found"
	email = '{}@{}'.format(pattern,domain)
	email = email.replace("{f}",name[0])
	email = email.replace("{l}",surname[0])
	email = email.replace("{first}",name)
	email = email.replace("{last}",surname)
	return email.lower()


# process and filter found results
def processResults(resp,t):
	json_content = json.loads(resp)
	elements = json_content['elements'][0]['elements']
	for element in elements:
		if 'com.linkedin.voyager.search.SearchProfile' in element['hitInfo']and element['hitInfo']['com.linkedin.voyager.search.SearchProfile']['headless'] == False:
			data = element['hitInfo']['com.linkedin.voyager.search.SearchProfile']
			try:
				industry = data["industry"].encode("utf8") # currently not used
			except:
				industry = ""
			try:
				location = data["location"].encode("utf8") # currently not used
			except:
				location = ""
			try:
				name = data["miniProfile"]["firstName"].encode("utf8")
			except:
				name = ""
			try:
				surname = data["miniProfile"]["lastName"].encode("utf8")
				if re.search('(.*?)[\-,]',surname):
					surname = re.search('(.*?)[ \-,]',surname).group(1)
			except:
				surname = ""
			try:		
				occupation = data["miniProfile"]["occupation"].encode("utf8").replace("\n", "")
				if len(occupation)>65:
					occupation = occupation[:65]+"..."
			except:
				occupation = ""
			try:		
				identifier = data["miniProfile"]["publicIdentifier"].encode("utf8") # currently not used
			except:
				identifier = ""	
			email = makeEmail(name, surname)
			t.add_row([unicode(name,errors='ignore'), unicode(surname,errors='ignore'), unicode(occupation,errors='ignore'), unicode(email,errors='ignore')])
			if args.dict:
				saveDictionaries(name.lower(), surname.lower())
			if args.csv:
				saveCSV(name, surname, occupation, email)	
		else:
			print "[-] Out of network result found" 
		

# search request (10 result each page)
def getResults():
	try:
		t = PrettyTable(['NAME', 'SURNAME', 'OCCUPATION', 'EMAIL'])
		for i in range(pages):
			url = "/voyager/api/search/cluster?count=10&guides=List(v-%3EPEOPLE,facetCurrentCompany-%3E"+str(ID)+")&origin=OTHER&q=guided&start="+str(i*10)
			#"/voyager/api/search/cluster?count=40&guides=List()&keywords="+queryf+"&origin=OTHER&q=guided&start="+str(i*10)
			conn.request("GET", url, headers={'Cookie':cookie,'Csrf-Token':Csrf_Token,'X-RestLi-Protocol-Version':'2.0.0'})
			risposta = conn.getresponse()
			resp = risposta.read()
			processResults(resp,t)
		print t
		print ""
	except IndexError as e:
		print e
		# index exception: no results
		print "[-] No Results\n"
	except Exception as e:
		print e


# hunter.io search to get domain email pattern
def getEmailPattern(domain):
	hunter_url = "hunter.io"
	hunter_port = 443
	hunter_conn = httplib.HTTPSConnection(hunter_url,hunter_port)
	hunter_conn.request("GET", "/trial/v2/domain-search?offset=0&domain="+domain+"&format=json")
	risposta = hunter_conn.getresponse()
	resp = risposta.read()
	if "pattern" in resp:
		json_content = json.loads(resp)
		pattern = json_content['data']['pattern']
		hunter_conn.close()
		return pattern
	elif "Please use an API key" in resp and args.api_key:
		hunter_conn.request("GET", "/v2/domain-search?domain="+domain+"&api_key="+args.api_key)
		risposta = hunter_conn.getresponse()
		resp = risposta.read()
		json_content = json.loads(resp)
		pattern = json_content['data']['pattern']
		hunter_conn.close()
		return pattern
	else:
		print "[-] Hunter.io api_key required!\n"
		exit()
	

# Format search text
def formatSearch(query):
	queryf = query.replace(" ", "+")
	return urllib.quote_plus("\""+queryf+"\"")



##########################################
#		MAIN                     #
##########################################

parser = argparse.ArgumentParser(description='Linkedin Company People Harvester')
parser.add_argument('-e', '--email', type=str, dest="email", metavar="EMAIL", help='Linkedin email')
parser.add_argument('-p', '--password', type=str, dest="password", metavar="PASSWORD", help='Linkedin password')
parser.add_argument('-s', '--search', type=str, dest="search", metavar="SEARCH", help='Linkedin search string')
parser.add_argument('-d', '--domain', type=str, dest="domain", metavar="DOMAIN", help='Email domain')
parser.add_argument('--dict', action='store_true', dest="dict", help='Write usernames dictionaries')
parser.add_argument('--csv', action='store_true', dest="csv", help='Write search output to csv file')
parser.add_argument('--company-id', type=str, dest="company_id", metavar="COMPANYID", help='Company ID number')
parser.add_argument('--api-key', type=str, dest="api_key", metavar="API_KEY", help='Hunter api key')

args = parser.parse_args()

try:
	# check email and password
	if args.email is not None:
		email = args.email	
	else:
		email = urllib.quote_plus( raw_input("Email: ") ) # url encode special chars
	if args.password is not None:
		password = args.password
	else:		
		password = urllib.quote_plus( getpass.getpass() ) # url encode special chars

	# get login cookie
	loginCsrfParam, tmp_cookies = getcsrf()
	login_cookies = login(loginCsrfParam, tmp_cookies, email, password)
	cookie = login_cookies
	Csrf_Token = re.search(r'JSESSIONID=(.*?);',cookie).group(1)
	
	# check search input
	if args.search is not None:
		query = args.search
		queryf = formatSearch(query)
	elif args.company_id is None:
		query = raw_input("Company Name $> ")
		print "[*] Requested query: " + query + "\n"
		queryf = formatSearch(query)
	
	if args.domain is not None:
		domain = args.domain
	else:
		domain = raw_input("Company Domain $> ")

	# get email pattern 
	pattern = getEmailPattern(domain)
	if pattern is None:
		print "[-] Possible email pattern: not found\n"
	else:
		print "[+] Possible email pattern: " + pattern + "\n"

	# search for company id
	if args.company_id is not None:
		ID = args.company_id
	else:
		getCompanyData(queryf)
		ID = raw_input("Company ID $> ")
	
	# get results max page number
	pages = getPages()
	
	# get people from company id
	getResults()

except KeyboardInterrupt: # if ctrl-c
	print "\n[-] Aborting...\n"
	exit()
except Exception as e:
	print e
