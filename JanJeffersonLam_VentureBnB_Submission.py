import email
import imaplib
import pandas as pd
from bs4 import BeautifulSoup
import getpass

# Host for the IMAPLIB
emailHost = "imap.gmail.com"

#What I did here was ask the credentials of the user instead of just hard coding my email credentials
print("Please enter your email credentials.")
emailUsername = input("Email username: ") 
emailPassword = getpass.getpass("Email password: ") 

# 1 - Read in 20 emails from your personal email and pull out any emails that are from "software@venturebnb.io"
# and include "Traveler Housing Request" in the subject line
def ReadInFurnishedFinderHousingRequestsEmails():

    emails = []

    #Connect to the email server 
    mail = imaplib.IMAP4_SSL(emailHost)
    mail.login (emailUsername, emailPassword)
    mail.select ('inbox') 

    # Searches for emails that contains "<from>" and has a subject with "Traveler Housing Request"
    status, searchData = mail.search(None, '(FROM "<from>") (SUBJECT "<subject>")')

    # This prints only if no emails are found
    if status != 'OK':
        print("Failed to search emails.")
        return emails

    # Check if any emails were found
    if not searchData[0]:
        print("No matching emails found.")
    else:
        for num in searchData[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status != 'OK':
                continue
            emails.append(email.message_from_bytes(data[0][1]))

    return emails

# 2 - Loop through the emails and put the following information from EACH email into a new row of a pandas dataframe:
# Tenant, Email Address, Phone Number, Number of Travelers, and Dates
def PullInformationFromEmailsAndPutIntoDataframe(emails):
    # TODO: write the code for this function to return the full dateframe
    data = []

    # Iterates through each email
    for mail in emails: # Loops through each email in the list emails
        if mail.is_multipart(): # checks if the email has multiparts like text and HTML
            for part in mail.walk(): # Iterates through each part of the multipart email
                if part.get_content_type() == "text/html": # Checks if its HTML text 
                    body = part.get_payload(decode=True).decode() # Extracts the content of this HTML part of the email then decodes it into a readable string format. It is assigned to variable body
                    break # exits the loop after finding HTML part. 

        # This only happens when the multipart is just plain text email without HTML
        else: 
            body = mail.get_payload(decode=True).decode() # This extracts the content of the plain text email and decodes it to a readable string format. 

        soup = BeautifulSoup(body, 'html.parser') # To parse the HTML content from variable body
        text = soup.get_text() # Once the HTML is parsed this extract all text from the HTML. Removing all HTML tags or markup

        # Extract information based on the required specifics "Tenant, Email, Phone, Travelers, and Dates"
        tenant = text.split("Tenant:\n\n")[1].split("\n\nEmail:")[0].strip()
        emailAddress = text.split("Email:\n\n")[1].split("\n\nPhone #:")[0].strip()
        phoneNumber = text.split("Phone #:\n\n")[1].split("\n\nTravelers:")[0].strip()
        numberOfTravelers = text.split("Travelers:\n\n")[1].split("\n\nDates:")[0].strip()
        dates = text.split("Dates:\n\n")[1].split("\n\nTraveling To:")[0].strip()

        data.append({
            "Tenant": tenant,
            "Email Address": emailAddress,
            "Phone Number": phoneNumber,
            "Number of Travelers": numberOfTravelers,
            "Dates": dates
        })

    dataframe = pd.DataFrame(data)
    return dataframe

if __name__ == '__main__':
    
    # 1 - Read in 20 emails from your personal email and pull out any emails that are from "<from>"
    # and include "Traveler Housing Request" in the subject line
    emails = ReadInFurnishedFinderHousingRequestsEmails()

    # 2 - Loop through the emails and put the following information from EACH email into a new row of a pandas dataframe:
    # Tenant, Email Address, Phone Number, Number of Travelers, and Dates
    dataframe = PullInformationFromEmailsAndPutIntoDataframe(emails)

    # Print the dataframe. This part is completely optional. I just wanted to make sure everything is working.
    print(dataframe)
    
    # Exports the dataframe to a CSV File. Though this will still create a csv file even though the dataframe is empty
    outputFile = 'jj.csv' #This will be the name of the CSV File
    dataframe.to_csv(outputFile, index=False)
    print (f"Has been exported to a csv file")
