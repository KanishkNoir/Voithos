import os
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from together import Together
from dotenv import load_dotenv

load_dotenv()
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Together.ai API configuration
api_key = os.getenv('TOGETHER_API_KEY')
client = Together(api_key=api_key)

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def get_events(service, time_min, max_results=10):
    events_result = service.events().list(
        calendarId="primary",
        timeMin=time_min,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    return events

def process_query(query, events=None):
    today_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')  # Format today's date
    if events:
        events_info = "\n".join([f"**Event**: {event['summary']}\n- **Start Time**: {event['start']['dateTime']} (UTC)\n- **End Time**: {event['end']['dateTime']} (UTC)\n- **Details**: [View Event]({event['htmlLink']})" for event in events])
    else:
        events_info = "No upcoming events."

    prompt = f"""
    You are an AI assistant designed to help students manage their schedules effectively. Below is a list of upcoming events in the user's Google Calendar:

    {events_info}

    Today's date is: {today_date}

    The user has asked the following question:
    {query}

    Your task is to provide a clear, friendly, and helpful response based on the events in the user's calendar and today's date. Make sure your answer is easy to understand and addresses the user's query comprehensively. If the query is about specific events, deadlines, scheduling conflicts, or general information like today's date, provide the necessary information or suggestions to help the user.

    Response:
    """

    try:
        output = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.2,
            stop=None,
            stream=False
        )
        response_content = output.choices[0].message.content
    except Exception as e:
        response_content = f"Error processing the query: {str(e)}"
    
    return response_content

def main():
    print("AI-Powered Calendar Assistant")

    # Google Calendar Authentication
    try:
        service = get_calendar_service()
    except Exception as e:
        print(f"Failed to authenticate with Google Calendar: {str(e)}")
        return

    # User Input
    query = input("Enter your request: ")
    
    if query:
        print("Processing your request...")
        now = datetime.now(timezone.utc).isoformat()
        events = get_events(service, now)
        response = process_query(query, events)
        print("\nAI Response")
        print(response)

if __name__ == "__main__":
    main()
