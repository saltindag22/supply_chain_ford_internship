import os
import base64
from email.mime.text import MIMEText
import pickle
from pymongo import MongoClient
from datetime import datetime
import google.generativeai as genai


MONGO_URI = ""
DB_NAME = ""
MAILING_LIST_COLLECTION = ""
CONVERSATIONS_COLLECTION = ""
SENDER_EMAIL = ""


try:
    GOOGLE_API_KEY = ""
    if not GOOGLE_API_KEY:
        raise ValueError("The GOOGLE_API_KEY environment variable was not found.")
    genai.configure(api_key=GOOGLE_API_KEY)
except ValueError as e:
    print(f"ERROR: {e}")
    exit()
    
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
token_path = os.path.join(BASE_DIR, 'token.pickle')

def get_gmail_service():
    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    else:
        raise FileNotFoundError(f"Error: token.pickle not found at {token_path}. Please run your token generation script first.")
    
    from googleapiclient.discovery import build
    return build('gmail', 'v1', credentials=creds)




def generate_intro_email_body(company_name, product_name):
    """
    Generates a professional, introductory email in English to a potential supplier,
    using a generic salutation as no specific contact name is available.
    """
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""
    You are a highly professional Strategic Sourcing Specialist in the automotive industry.
    Your task is to write a concise and respectful introductory email to a potential supplier company. The goal is NOT to request a quote but to establish a professional first contact for future collaborations.

    Supplier Company: {company_name}
    Company's Main Product/Field: {product_name}

    Please generate a professional email body in ENGLISH following these rules:
    1.  Start with a professional, generic salutation, as you do not have a specific contact person's name. Use "Dear {company_name} Team," or "To the Sourcing Department at {company_name},".
    2.  Briefly introduce yourself and your role in strategic sourcing for the automotive sector.
    3.  Mention that their company, '{company_name}', has come to your attention for its work in the '{product_name}' field.
    4.  Clearly state your purpose: "While we do not have a specific RFQ at this moment, we are currently enhancing our database of high-potential suppliers for our key clients, such as Ford Otosan. We would be honored to include your company in our list of potential future partners."
    5.  Include a very low-pressure call to action. For example: "We would be pleased to receive a general company presentation or product catalog at your convenience, so we can better understand your capabilities for future projects."
    6.  Conclude professionally with "Sincerely," or "Best regards," followed by your name (Sema) and title (Strategic Sourcing Specialist).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"  - An error occurred while generating text from the LLM: {e}")
        return f"Dear {company_name} Team,\n\nWe are contacting you as part of our supplier development program for the automotive industry. Your company's work in the {product_field} field has caught our attention.\n\nWe would like to add your company to our database for potential future collaborations.\n\nBest regards,\nSema"

def main():
    """Main function to run the email sending process."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    mailing_list = db[MAILING_LIST_COLLECTION].find({"status": "pending"})
    gmail_service = get_gmail_service()
    
    print("Sending introductory emails to potential suppliers...")
    for item in mailing_list:
        
        recipient_email = item.get("email")
        company_name = item.get("company_name")
        product_name = item.get("product_name") 

        if not recipient_email or not company_name:
            print(f"  - WARNING: Skipping record due to missing email or company name: {item.get('_id')}")
            continue

        print(f"- Generating introductory email for '{company_name}'...")
        body = generate_intro_email_body(company_name, product_name)
        
        subject = f"Regarding a Potential Sourcing Partnership with {company_name}"
        
        message = MIMEText(body, 'plain', 'utf-8')
        message['to'] = recipient_email
        message['from'] = SENDER_EMAIL
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            sent_message = gmail_service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            print(f"  -> Email sent successfully to {recipient_email}. Message ID: {sent_message['id']}")
            
            db[MAILING_LIST_COLLECTION].update_one(
                {"_id": item["_id"]},
                {"$set": {"status": "sent", "lastUpdatedAt": datetime.utcnow()}}
            )
            
            db[CONVERSATIONS_COLLECTION].insert_one({
                "threadId": sent_message['threadId'],
                "recipientEmail": recipient_email,
                "companyName": company_name, 
                "status": "initiated",
                "createdAt": datetime.utcnow(),
                "lastUpdatedAt": datetime.utcnow(),
                "messages": [{
                    "role": "assistant",
                    "content": body,
                    "timestamp": datetime.utcnow()
                }]
            })
            
        except Exception as e:
            print(f"  - ERROR: Failed to send email to {recipient_email}: {e}")

    print("\nEmail sending process completed.")

if __name__ == '__main__':
    main()
