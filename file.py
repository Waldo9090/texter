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

# Function to process an invite document
def process_invite(doc_snapshot):
    doc_data = doc_snapshot.to_dict()
    if doc_data.get('completed') != True:
        username = doc_data.get('userName')
        invites = doc_data.get('invites', [])

        for invite in invites:
            recipient_name = invite.get('recipientName')
            phone_number = invite.get('recipientPhoneNumber')

            # Personalize the message
            message = f"Hey {recipient_name} - {username} just sent you a friend request on SwoleAI! Join the social fitness app and compete with friends👇\n\n{share_link}"

            # Send the iMessage
            send_imessage(phone_number, message)

        # Mark the document as completed
        doc_snapshot.reference.update({'completed': True})
        print(f"Marked document {doc_snapshot.id} as completed.")
    else:
        print(f"Document {doc_snapshot.id} is already marked as completed.")

# Attach a listener to the 'Invites' collection
def listen_for_invites():
    invites_ref = db.collection('Invites')
    def on_snapshot(col_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED' or change.type.name == 'MODIFIED':
                process_invite(change.document)
    invites_ref.on_snapshot(on_snapshot)

# Start listening for invites
print("Listening for new invites...")
listen_for_invites()

# Keep the script running
import time
while True:
    time.sleep(60)
