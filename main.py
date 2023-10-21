import requests
import datetime
import time
import logging
import html
from settings import *
from bs4 import BeautifulSoup

logging.basicConfig(level=getattr(logging, LOGGING_LEVEL),
                    format='%(asctime)s - %(levelname)s - %(message)s')

MS_GRAPH_TOKEN_ENDPOINT = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
MS_GRAPH_MAIL_ENDPOINT = 'https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false'
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

def refresh_access_token():
    logging.debug("Refreshing access token...")
    payload = {
        'client_id': CLIENT_ID,
        'scope': ' '.join(SCOPE),
        'refresh_token': REFRESH_TOKEN,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'refresh_token',
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(MS_GRAPH_TOKEN_ENDPOINT, data=payload)
    if response.status_code == 200:
        logging.debug("Access token refreshed successfully.")
        return response.json().get('access_token')
    else:
        logging.error(f"Failed to refresh access token. Status code: {response.status_code}, Response: {response.text}")
        return None

def load_processed_email_ids():
    try:
        with open('processed_emails.txt', 'r') as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        return set()

def save_processed_email_ids(email_ids):
    with open('processed_emails.txt', 'w') as file:
        for email_id in email_ids:
            file.write(email_id + '\n')


def get_unread_emails(access_token):
    logging.debug("Fetching unread emails...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(MS_GRAPH_MAIL_ENDPOINT, headers=headers)
    if response.status_code == 200:
        emails = response.json().get('value', [])
        logging.debug(f"Fetched {len(emails)} unread emails.")
        return emails
    else:
        logging.error(f"Failed to fetch unread emails. Status code: {response.status_code}, Response: {response.text}")
        return []

def send_telegram_message(email):
    subject = email['subject']
    sender = email['from']['emailAddress']['address']
    recipient = email['toRecipients'][0]['emailAddress']['address']
    received_time = email['receivedDateTime']  # Format this as per your requirements
    html_content = email['body']['content']

    # Convert HTML to plain text
    soup = BeautifulSoup(html_content, "html.parser")
    plain_text_content = soup.get_text()

    # Format the message
    message = f"""
🕞 {received_time}
❱❱ to: #{recipient}
❰❰ by: #{sender}
💬 {subject}

{plain_text_content}
"""

    # Send the message to Telegram
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': html.escape(message)
    }
    response = requests.post(TELEGRAM_API_URL, data=payload)
    if response.status_code == 200:
        logging.debug("Message sent to Telegram successfully.")
    else:
        logging.error(f"Failed to send message to Telegram. Status code: {response.status_code}, Response: {response.text}")

def main():
    processed_emails = load_processed_email_ids()
    last_saved_time = datetime.datetime.now()
    
    while True:
        access_token = refresh_access_token()
        if access_token:
            unread_emails = get_unread_emails(access_token)
            for email in unread_emails:
                # Если это новое письмо
                if email['id'] not in processed_emails:
                    send_telegram_message(email)
                    processed_emails.add(email['id'])
        
        # Проверяем, прошел ли час с момента последнего сохранения
        current_time = datetime.datetime.now()
        if (current_time - last_saved_time).total_seconds() >= 3600:
            save_processed_email_ids(processed_emails)
            last_saved_time = current_time

        time.sleep(30)  # Проверка каждые 30 секунд

    # Сохраняем обработанные ID писем при завершении работы
    save_processed_email_ids(processed_emails)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Если бот остановлен пользователем, сохраняем обработанные ID писем
        save_processed_email_ids(processed_emails)