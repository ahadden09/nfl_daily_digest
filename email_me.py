import smtplib

host = 'smtp.gmail.com'
port = 587
email = raw_input('email address:')
password = raw_input('password:')

smtp_obj = smtplib.SMTP(host, port) #Create SMTP object

print smtp_obj.ehlo() #Send SMTP "Hello" message		***Will probably need to add a error handling here in case connection fails***

print smtp_obj.starttls() #Start TLS encryption

smtp_obj.login(email, password)

body = 'Subject: NFLdb Daily Digest\nTesting 123'

smtp_obj.sendmail(email, email, body)

smtp_obj.quit()
