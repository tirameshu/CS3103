"""
Run this with
python3 mailer_program.py [maildata.csv]

CSV file should contain header, and columns are to be in the format [email] [name] [department]

Will prompt for login, where sender email and password should be provided.
Will also prompt for absolute file path to email text file.

Email text file format:
-	Start with “Subject: …”
-	Placeholders for variables such as name and department should be enclosed as such: $name$, $department$
"""

import csv
import sys
import time
import smtplib

from getpass import getpass
from socket import gaierror

# save a hash of dept: {email: name}
dept_roster = {}

# smtp server
smtp_server = "smtp.gmail.com"
port = 587

def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of list
    containing rows in the csv file and its entries.
    """
    rows = []

    with open(csvfilename) as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows.append(row)
    return rows

def get_subject(to_send):
    with open(to_send, "r") as content:
        first_line = content.readline()

        # sanity check
        words = first_line.split(" ")
        if "subject" in words[0].lower():
            return " ".join(words[1:])

def get_full_content_formatted(to_send, dept, rec_email):
    with open(to_send, "r") as content:
        body = content.read()

    body = "From: {}\nTo: {}\n" + body

    # format with name of recipient
    receiver_name = dept_roster[dept][rec_email]
    body = body.replace("$name$", receiver_name)
    body = body.replace("$department$", dept)

    return body

"""
Dept provided here is already verified to be valid.

There is only one function to mail to a specific dept because
sending to all is just looping through all the depts
so this is done to prevent duplicate code
"""
def mail_to_dept(dept, to_send, sender_email, server):
    counter = 0

    dept_emails = dept_roster[dept]

    print("Mailing to department: " + dept)

    for rec_email in dept_emails:
        receiver_name = dept_roster[dept][rec_email]

        subject = get_subject(to_send)

        # msg construction
        msg = get_full_content_formatted(to_send, dept, rec_email)

        print("Sending to " + receiver_name + ". Subject: " + subject)

        server.sendmail(sender_email, rec_email, msg.format(sender_email, rec_email, msg).encode("utf-8"))

        counter += 1

    # send summary
    print(str(counter) + " mail(s) sent to department: " + dept + "\n")

def login_and_mail(dept):
    sender_email = input("Sender login: email address ").strip()
    sender_pw = getpass()

    # login attempt
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_pw)

            print('Login successful!\n')

            # only if login is successful do we continue with the mailing
            to_send = input("Please provide the absolute address of your email text file: ").strip()

            start = time.time()

            if dept == "all":
                print("\nMailing to all")

                for dept in dept_roster:
                    mail_to_dept(dept, to_send, sender_email, server)

                print("Total time taken: " + '%.3f' % ((time.time() - start) * 10 ** 3) + "ms\n")
            else:
                mail_to_dept(dept, to_send, sender_email, server)

                print("Total time taken: " + '%.3f' % ((time.time() - start) * 10 ** 3) + "ms\n")

    except (gaierror, ConnectionRefusedError):
        print('Failed to connect to the server. Bad connection settings?')
    except smtplib.SMTPServerDisconnected:
        print('Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
        print('SMTP error occurred: ' + str(e))


def check_dept():
    # keep looping until user gets it right
    valid = False
    dept = ""

    while not valid:
        dept = input("Please enter the department code: ").lower().strip()

        if dept != "all" and dept not in dept_roster: # invalid
            print("Invalid department code!")
            continue
        else:
            valid = True

    login_and_mail(dept)

maildata = sys.argv[1]
# excess args ignored

maildata_rows = read_csv(maildata)

# assumes csv contains header
maildata_entries = maildata_rows[1:]

for entry in maildata_entries:
    email, name, dept = entry
    dept = dept.strip().lower() # case insensitive
    if dept not in dept_roster:
        dept_roster[dept] = {email.strip(): name.strip()}
    else:
        if email not in dept_roster[dept]:
            dept_roster[dept][email] = name
        # ignore duplicate email, saves the earlier entry

# print(dept_roster)

if dept_roster:
    print("Department Roster successfully populated!\n")
else:
    print("Department Roster Unsuccessful :(\n")

# ask for dept code and verify
check_dept()