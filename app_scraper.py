import streamlit as st
import requests
import xlwt
from xlwt import Workbook
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

BASE_URL = 'https://remoteok.com/api/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36'
REQUEST_HEADER = {'User-Agent': USER_AGENT, 'Accept-Language': 'en-US, en;q=0.5'}

st.title("MY Job Scraper & Email Sender")

def get_job_postings():
    res = requests.get(url=BASE_URL, headers=REQUEST_HEADER)
    return res.json()[1:]  # Skip the first entry (metadata)

def output_jobs_to_xls(data, filename="remote_jobs.xls"):
    wb = Workbook()
    job_sheet = wb.add_sheet('Jobs')
    headers = list(data[0].keys())
    for i in range(len(headers)):
        job_sheet.write(0, i, headers[i])
    for i, job in enumerate(data):
        values = list(job.values())
        for x in range(len(values)):
            job_sheet.write(i+1, x, values[x])
    wb.save(filename)
    return filename

def send_email(send_from, send_to, subject, text, files):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to) if isinstance(send_to, list) else send_to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))
    
    for f in files or []:
        with open(f, "rb") as file:
            part = MIMEApplication(file.read(), Name=basename(f))
        part['Content-Disposition'] = f'attachment; filename="{basename(f)}"'
        msg.attach(part)

    smtp = smtplib.SMTP("smtp.gmail.com:587")
    smtp.starttls()
    smtp.login(send_from, st.secrets["email_password"])  # Use email password from secrets
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
    return "Email sent successfully!"

if st.button("Fetch Jobs"):
    jobs = get_job_postings()
    st.session_state['jobs'] = jobs
    st.success("Job postings fetched successfully!")

if 'jobs' in st.session_state:
    if st.button("Generate Excel File"):
        filename = output_jobs_to_xls(st.session_state['jobs'])
        st.session_state['filename'] = filename
        st.success(f"Excel file '{filename}' created!")

st.header("Send Email")
sender_email = st.text_input("Your Email")
receiver_email = st.text_input("Recipient Email")
subject = st.text_input("Email Subject")
message = st.text_area("Email Message")

if 'filename' in st.session_state:
    if st.button("Send Email"):
        response = send_email(sender_email, receiver_email, subject, message, [st.session_state['filename']])
        st.success(response)
