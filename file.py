import firebase_admin
from firebase_admin import credentials, firestore
import subprocess

# Initialize Firebase
cred = credentials.Certificate("/Users/ayushmahna/Downloads/bodymax-2b6c1-firebase-adminsdk-rzab1-6f37400166.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Share link to include in message
share_link = "https://apps.apple.com/us/app/swoleai-fitness-max/id6581480231"

# Function to send iMessage using AppleScript
def send_imessage(phone_number, message_text):
    script = f'''
    on run {{phone_number, message_text}}
        tell application "Messages"
            set targetService to 1st service whose service type = iMessage
            set targetBuddy to buddy phone_number of targetService
            send message_text to targetBuddy
        end tell
    end run
    '''
    try:
        subprocess.run(['osascript', '-e', script, phone_number, message_text], check=True)
        print(f"Message sent to {phone_number}")
    except Exception as e:
        print(f"Failed to send message to {phone_number}: {e}")

# Function to process invites in all documents in the 'Invites' collection
def process_all_invites():
    invites_ref = db.collection('Invites')
    docs = invites_ref.stream()

    for doc in docs:
        doc_data = doc.to_dict()
        
        # Check if 'completed' field exists and is set to True
        if doc_data.get('completed') != True:
            username = doc_data.get('userName')
            invites = doc_data.get('invites', [])

            for invite in invites:
                recipient_name = invite.get('recipientName')
                phone_number = invite.get('recipientPhoneNumber')
                
                # Use full name for personalization
                message = f"Hey {recipient_name} - {username} just sent you a friend request on SwoleAI! Join the social fitness app and compete with friends👇\n\n{share_link}"
                
                # Send the iMessage
                send_imessage(phone_number, message)
            
            # Update document to set 'completed' to True
            doc.reference.update({'completed': True})
            print(f"Marked document {doc.id} as completed.")
        else:
            print(f"Document {doc.id} is already marked as completed.")

# Process all invites in the 'Invites' collection
process_all_invites()
