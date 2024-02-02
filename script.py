# Import libraries
import requests
import json
import schedule
import time
import smtplib

# Define the stock news source and API key
source = "https://financialmodelingprep.com/api/v3/stock_news?tickers=NSE:RELIANCE,NSE:TCS,NSE:INFY&limit=50&apikey=YOUR_API_KEY"
# Replace YOUR_API_KEY with your own API key from financialmodelingprep.com

# Define the keywords to look for
keywords = ["bonus", "split"]

# Define the email and whatsapp details
sender_email = "YOUR_EMAIL" # Replace with your own email
sender_password = "YOUR_PASSWORD" # Replace with your own password
receiver_email = "YOUR_RECEIVER_EMAIL" # Replace with the receiver's email
whatsapp_url = "https://api.callmebot.com/whatsapp.php?phone=+91XXXXXXXXXX&text={}&apikey=YOUR_API_KEY"
# Replace +91XXXXXXXXXX with the receiver's phone number
# Replace YOUR_API_KEY with your own API key from callmebot.com

# Define a function to send email
def send_email(subject, message):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the message body
    msg.attach(MIMEText(message, 'plain'))

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to send the email
    try:
        # Connect to the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls(context=context)
        # Login to the email account
        server.login(sender_email, sender_password)
        # Send the email
        server.sendmail(sender_email, receiver_email, msg.as_string())
        # Quit the server
        server.quit()
        # Print a confirmation
        print("Email sent successfully")
    except Exception as e:
        # Print an error message
        print("Error sending email:", e)

# Define a function to send whatsapp message
def send_whatsapp(message):
    # Encode the message
    message = urllib.parse.quote(message)
    # Format the url with the message
    url = whatsapp_url.format(message)
    # Try to send the whatsapp message
    try:
        # Make a request to the url
        response = requests.get(url)
        # Check the status code
        if response.status_code == 200:
            # Print a confirmation
            print("Whatsapp message sent successfully")
        else:
            # Print an error message
            print("Error sending whatsapp message:", response.text)
    except Exception as e:
        # Print an error message
        print("Error sending whatsapp message:", e)

# Define a function to check the stock news
def check_stock_news():
    # Make a request to the source
    response = requests.get(source)
    # Check the status code
    if response.status_code == 200:
        # Parse the response as json
        data = response.json()
        # Loop through the news articles
        for article in data:
            # Get the title and url of the article
            title = article['title']
            url = article['url']
            # Check if any of the keywords are in the title
            for keyword in keywords:
                if keyword.lower() in title.lower():
                    # Format the subject and message
                    subject = f"Stock news alert: {keyword}"
                    message = f"{title}\n{url}"
                    # Send email and whatsapp message
                    send_email(subject, message)
                    send_whatsapp(message)
                    # Break the loop
                    break
    else:
        # Print an error message
        print("Error getting stock news:", response.text)

# Schedule the function to run twice a day
schedule.every().day.at("09:00").do(check_stock_news) # At 9:00 am
schedule.every().day.at("21:00").do(check_stock_news) # At 9:00 pm

# Run the script
while True:
    # Run the pending tasks
    schedule.run_pending()
    # Sleep for one minute
    time.sleep(60)

