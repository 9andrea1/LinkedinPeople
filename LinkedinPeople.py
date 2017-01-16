#!/usr/bin/env python
import urllib, httplib, re, sys, getpass
from termcolor import colored #except ImportError
import argparse


# https connection to url
url = "www.linkedin.com"
port = 443
conn = httplib.HTTPSConnection(url,port)

# output files
out_all = open("all.txt","w")
nome_cognome = open("nome.cognome.txt","w")
cognome_nome = open("cognome.nome.txt","w")
n_cognome = open("n.cognome.txt","w")
cognome_n = open("cognome.n.txt","w")
ncognome = open("ncognome.txt","w")
cognomen = open("cognomen.txt","w")

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
	sourceAlias = re.search(r'sourceAlias-login" type="hidden" value="(.*?)"',resp).group(1)
	return loginCsrfParam, sourceAlias, cookies


# return session cookie
def login(loginCsrfParam, sourceAlias, cookies, email, password):
	data = "session_key="+email+"&session_password="+password+"&isJsEnabled=false&loginCsrfParam="+loginCsrfParam+"&sourceAlias="+sourceAlias+"\""
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


# print found results
def printResults(resp):
	page_name_list = re.findall('"fmt_name":"(.*?)"',resp)
	for tmp in page_name_list:
		name_surname = tmp.replace("&#39;","'")
		print name_surname
		lista = name_surname.strip().split(" ")
		name = lista[0].lower()
		surname = lista[1].lower()
		# save into dictionary file
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


# search requests (10 link each)
def getResults(ricercaf, cookie):
	try:
		conn.request("GET", "/vsearch/f?keywords="+ricercaf+"&pt=people&page_num=1", headers={'Cookie':cookie})
		risposta = conn.getresponse()
		resp = risposta.read()
		max_num_tmp = re.findall('"\\\\u003cstrong\\\\u003e(.{1,10})\\\\u003c/strong\\\\u003e risultati in Persone',resp)[1]
		max_num = max_num_tmp.replace(".","")
		pagine = int(round((int(max_num)/10.0)+0.5))			
		print "[*] Found " + max_num + " total results in " + str(pagine) + " pages...\n"
		printResults(resp)
		if pagine > 1 :
			if pagine > 100 :	
				pagine = 100
			for n in range(2,pagine):
				conn.request("GET", "/vsearch/f?keywords="+ricercaf+"&pt=people&page_num="+str(n), headers={'Cookie':cookie})
				risposta = conn.getresponse()
				resp = risposta.read()
				printResults(resp)
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



##########################################
#		MAIN                     #
##########################################

parser = argparse.ArgumentParser(description='Linkedin Company People Harvester')
parser.add_argument('-e', '--email', type=str, dest="email", metavar="EMAIL", help='Linkedin email')
parser.add_argument('-p', '--password', type=str, dest="password", metavar="PASSWORD", help='Linkedin password')
parser.add_argument('-s', '--search', type=str, dest="search", metavar="SEARCH", help='Linkedin search string')

args = parser.parse_args()

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
loginCsrfParam, sourceAlias, tmp_cookies = getcsrf()
login_cookies = login(loginCsrfParam, sourceAlias, tmp_cookies, email, password)
cookie = login_cookies

# check search input
if args.search is not None:
	query = args.search
else:
	query = raw_input("Company name $> ")
print "[*] Requested query: " + query + "\n"
try: 
	queryf = formatSearch(query)
	getResults(queryf, cookie)
except KeyboardInterrupt: # if ctrl-c
	print "\n[-] Aborting...\n"
	sys.exit()


