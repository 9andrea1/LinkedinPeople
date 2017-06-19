#!/usr/bin/env python
import urllib, httplib, re, sys, getpass, json, os
#from termcolor import colored #except ImportError
import argparse


# https connection to url
url = "www.linkedin.com"
port = 443
conn = httplib.HTTPSConnection(url,port)

# output files
if not os.path.exists("output"):
	os.mkdir("output")
	os.mkdir("output/pdf/")
	os.mkdir("output/dict/")
pdf_directory = "output/pdf/"
dict_directory = "output/dict/"
out_all = open(dict_directory+"all.txt","w")
nome_cognome = open(dict_directory+"nome.cognome.txt","w")
cognome_nome = open(dict_directory+"cognome.nome.txt","w")
n_cognome = open(dict_directory+"n.cognome.txt","w")
cognome_n = open(dict_directory+"cognome.n.txt","w")
ncognome = open(dict_directory+"ncognome.txt","w")
cognomen = open(dict_directory+"cognomen.txt","w")


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
		sys.exit()	
	return cookies+" li_at="+li_at+";"


# save into dictionary files
def printToFile(name, surname):
	nome_cognome.write(name+"."+surname+"\n")
	cognome_nome.write(surname+"."+name+"\n")
	n_cognome.write(name[0]+"."+surname+"\n")
	cognome_n.write(surname+"."+name[0]+"\n")
	ncognome.write(name[0]+surname+"\n")
	cognomen.write(surname+name[0]+"\n")
	out_all.write(name+"."+surname+"\n")
	out_all.write(surname+"."+name+"\n")
	out_all.write(name[0]+"."+surname+"\n")
	out_all.write(surname+"."+name[0]+"\n")
	out_all.write(name[0]+surname+"\n")
	out_all.write(surname+name[0]+"\n")


# process and filter found results
def processResults(resp,cookie):
	json_content = json.loads(resp)
	elements = json_content['elements'][0]['elements']
	for element in elements:
		data = element['hitInfo']['com.linkedin.voyager.search.SearchProfile']['miniProfile']
		action_list = element['hitInfo']['com.linkedin.voyager.search.SearchProfile']['profileActions']['overflowActions']
		for action in action_list:
			try:
				pdf_url = action['action']['com.linkedin.voyager.identity.profile.actions.SaveToPdf']['requestUrl'].encode('utf8')
				break
			except:
				None	
		try:
			name = data['firstName'].encode('utf8')
		except:
			name = ""
		try:
			surname = data['lastName'].encode('utf8')
		except:
			surname = ""
		try:		
			occupation = data['occupation'].encode('utf8')
		except:
			occupation = ""	
		if len(name)>0 and len(surname)>0:
			print name + " " + surname + "\t\t" + occupation #TODO log to file
			if args.dict: 
				printToFile(name, surname)
		else:
			print "## debug -> " + pdf_url
		if args.pdf:
			getPDF(pdf_url, cookie)


# search requests (10 link each)
def getResults(ricercaf, cookie, Csrf_Token):
	try:
		conn.request("GET", "/voyager/api/search/cluster?count=10&guides=List()&keywords="+ricercaf+"&origin=SWITCH_SEARCH_VERTICAL&q=guided&start=0", headers={'Cookie':cookie,'Csrf-Token':Csrf_Token,'X-LI-Track':'{"clientVersion":"1.0.*","osName":"web","timezoneOffset":2,"deviceFormFactor":"DESKTOP"}'})
		risposta = conn.getresponse()
		resp = risposta.read()
		json_content = json.loads(resp)
		max_num = json_content['paging']['total']
		pagine = int(round((int(max_num)/10.0)+0.5))			
		print "[*] Found " + str(max_num) + " total results in " + str(pagine) + " pages...\n"
		processResults(resp,cookie)
		if pagine > 1 :
			if pagine > 1000 :	
				pagine = 1000 # max 999 pagine
			for n in range(1,pagine):
				conn.request("GET", "/voyager/api/search/cluster?count=10&guides=List()&keywords="+ricercaf+"&origin=SWITCH_SEARCH_VERTICAL&q=guided&start="+str(n*10), headers={'Cookie':cookie,'Csrf-Token':Csrf_Token,'X-LI-Track':'{"clientVersion":"1.0.*","osName":"web","timezoneOffset":2,"deviceFormFactor":"DESKTOP"}'})
				risposta = conn.getresponse()
				resp = risposta.read()
				processResults(resp,cookie)
		print "\n[+] Done\n"	
	except IndexError:
		# index exception: no results
		print "[*] No Results\n"
	except Exception as e:
		print e


# Format search text
def formatSearch(query):
	queryf = query.replace(" ", "+")
	return urllib.quote_plus("\""+queryf+"\"")


# save pdf profile
def savePDF(fname, resp):
	f = open(pdf_directory+fname,"wb")
	f.write(resp)
	f.close()

# download pdf profile
def getPDF(url, cookie):
	url = url[24:].replace(" ", "+") # remove https://www.linkedin.com and space
	conn.request("GET", url, headers={"Cookie":"%s"%cookie})
	risposta = conn.getresponse()
	resp = risposta.read()
	d = risposta.getheader('Content-disposition')
	fname = re.search('filename="(.+)"', d).group(1)
	savePDF(fname, resp)	


##########################################
#		MAIN                     #
##########################################

parser = argparse.ArgumentParser(description='Linkedin Company People Harvester')
parser.add_argument('-e', '--email', type=str, dest="email", metavar="EMAIL", help='Linkedin email')
parser.add_argument('-p', '--password', type=str, dest="password", metavar="PASSWORD", help='Linkedin password')
parser.add_argument('-s', '--search', type=str, dest="search", metavar="SEARCH", help='Linkedin search string')
parser.add_argument('-w', '--pdf', action='store_true', dest="pdf", help='Write harvested profile to pdf')
parser.add_argument('-d', '--dict', action='store_true', dest="dict", help='Write dictionaries')

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
	else:
		query = raw_input("Company name $> ")
	print "[*] Requested query: " + query + "\n"
	
	queryf = formatSearch(query)
	
	# get request results
	getResults(queryf, cookie, Csrf_Token)

except KeyboardInterrupt: # if ctrl-c
	print "\n[-] Aborting...\n"
	sys.exit()
except Exception as e:
	print e
