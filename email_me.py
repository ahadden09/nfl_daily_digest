import smtplib
import pandas as pd

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(data, email_to, email_from):
	host = 'smtp.gmail.com'
	port = 587
	login_email = raw_input('login_email address:')
	password = raw_input('password:')
	try:
		smtp_obj = smtplib.SMTP(host, port) #Create SMTP object
		smtp_obj.ehlo() #Send SMTP "Hello" message		***Will probably need to add a error handling here in case connection fails***
		smtp_obj.starttls() #Start TLS encryption
	except:
		print 'smtp_connection_error: ehlo() or starttls()'
	try:
		smtp_obj.login(login_email, password) #Login to email
	except:
		print 'stmp_login_error: smtp_login_issue'
		raise
	try: #created using code stolen (but not all copy pasta) from https://stackoverflow.com/questions/882712/sending-html-email-using-python	
		#Create message container - the correct MIME type is multipart/alternative
		msg = MIMEMultipart('alternative')
		msg['Subject'] = 'NFLdb Daily Digest'
		msg['From'] = email_from
		msg['To'] = email_to
		
		#create the body of the message (a plain-test and an HTML version).
		text = 'This is a plain-text test!/nThis is only a test!'
		html = '''\
				<html>
				  <head></head>
				  <body>
					<table>
						{}
					</table>
				  </body>
				</html>
				'''.format(data.to_html())
				
		#Records the MIME types of both parts - text/plain and text/html
		part1 = MIMEText(text, 'plain')
		part2 = MIMEText(html, 'html')
		
		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)
		msg.attach(part2)
	except:
		raise
	try: #Send message via SMTP server
		body = data
		smtp_obj.sendmail(email_from, email_to, msg.as_string())
		print 'email sent'
		smtp_obj.quit()
	except:
		print 'send_email_error: email could not be sent'
		
