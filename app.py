from flask import Flask, request, jsonify, session
from flask_cors import CORS
import google.generativeai as genai
import uuid
import logging
import json
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "journey_app_secret_key"
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Gemini
genai.configure(api_key="AIzaSyD2ArK74wBtL1ufYmpyrV2LqaOBrSi3mlU")
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    safety_settings=[
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    ],
    generation_config={"temperature": 0.7, "top_p": 0.95, "top_k": 40}
)

# Session storage
sessions = {}

# Mock data for screen components
MOCK_SCREEN_COMPONENTS = [
    {"screen_component_id": 1, "screen_component_name": "CustomerDetails"},
    {"screen_component_id": 2, "screen_component_name": "pan"},
    {"screen_component_id": 3, "screen_component_name": "aadhar"},
    {"screen_component_id": 4, "screen_component_name": "otp"},
    {"screen_component_id": 5, "screen_component_name": "status"}
]

# Mock data for field components
MOCK_FIELD_COMPONENTS = {
    "CustomerDetails": [
        {
            "fieldComponentId": 1,
            "fieldType": "largetext",
            "fieldName": "customerDetailsHeading",
            "fieldLabel": "Enter Customer Details",
            "validations": {},
            "dataSource": None,
            "dependencies": None,
            "isTriggerComponent": False,
            "createdAt": "2025-02-23T12:06:37.958916",
            "updatedAt": "2025-02-23T12:06:37.904855",
            "style": "defaultFieldStyle"
        },
        {
            "fieldComponentId": 28,
            "fieldType": "text_field",
            "fieldName": "firstname",
            "fieldLabel": "First Name",
            "validations": {
                "required": True,
                "requiredMessage": "First Name is required",
                "minLength": 3,
                "minLengthMessage": "Firstname must be at least 3 characters",
                "helperText": "Enter a Firstname between 3-20 characters"
            },
            "dataSource": None,
            "dependencies": None,
            "isTriggerComponent": False,
            "createdAt": "2025-02-24T09:55:40.602092",
            "updatedAt": "2025-02-24T09:55:40.568178",
            "style": "defaultFieldStyle"
        }
    ],
    "pan": [
        {
            "fieldComponentId": 11,
            "fieldType": "largetext",
            "fieldName": "panDetailsHeading",
            "fieldLabel": "Enter PAN Details",
            "validations": {},
            "dataSource": None,
            "dependencies": None,
            "isTriggerComponent": False,
            "createdAt": "2025-02-23T12:16:29.365502",
            "updatedAt": "2025-02-23T12:16:29.352896",
            "style": "defaultFieldStyle"
        }
    ],
    "aadhar": [
        {
            "fieldComponentId": 14,
            "fieldType": "largetext",
            "fieldName": "aadharHeadingDetails",
            "fieldLabel": "Enter Aadhar Details",
            "validations": {},
            "dataSource": None,
            "dependencies": None,
            "isTriggerComponent": False,
            "createdAt": "2025-02-23T12:27:20.931269",
            "updatedAt": "2025-02-23T12:27:20.906399",
            "style": "defaultFieldStyle"
        }
    ],
    "otp": [
        {
            "fieldComponentId": 17,
            "fieldType": "largetext",
            "fieldName": "otpHeading",
            "fieldLabel": "Enter OTP",
            "validations": {},
            "dataSource": None,
            "dependencies": None,
            "isTriggerComponent": False,
            "createdAt": "2025-02-23T12:29:14.083147",
            "updatedAt": "2025-02-23T12:29:14.071053",
            "style": "defaultFieldStyle"
        }
    ],
    "status": [
        {
            "fieldComponentId": 19,
            "fieldType": "statustext",
            "fieldName": "status",
            "fieldLabel": "status",
            "validations": {},
            "dataSource": None,
            "dependencies": None,
            "isTriggerComponent": False,
            "createdAt": "2025-02-23T23:24:15.569678",
            "updatedAt": "2025-02-23T23:24:15.548801",
            "style": "defaultFieldStyle"
        }
    ]
}

# Function to fetch screen components (mocked)
def fetch_screen_components():
    """
    Mock function to fetch screen components from secondary backend
    
    # Actual API call would be:
    # import requests
    # response = requests.get("https://backend.example.com/api/screen-components")
    # return response.json()
    """
    return MOCK_SCREEN_COMPONENTS

# Function to fetch field components for a screen component (mocked)
def fetch_field_components(screen_component_name):
    """
    Mock function to fetch field components for a screen component
    
    # Actual API call would be:
    # import requests
    # response = requests.get(f"https://backend.example.com/api/field-components/{screen_component_name}")
    # return response.json()
    """
    return MOCK_FIELD_COMPONENTS.get(screen_component_name, [])

# Initial prompt for Gemini
SYSTEM_PROMPT = """
You are an AI assistant that helps users create journey JSON configurations for a banking application. 
Your task is to generate JSON based on user requirements, following these rules:

1. You must ONLY return valid JSON in your response - no explanations, no comments, no additional text.
2. The journey structure follows this format:
   - journey_name: Name of the journey (e.g., "SavingAccountJourney")
   - journey_type: "single" 
   - screens: Array of screen objects
   - navigation: Array of navigation rules between screens

3. Each screen has:
   - screen_id: Unique numeric ID
   - screen_name: Descriptive name
   - template: Use "defaultTemplate"
   - style: Use "defaultScreenStyle"
   - screen_components: Array of components in this screen

4. You CANNOT create new screen_components or field_components. You must use existing ones from the provided lists.

5. When the user wants to add a new screen, you must:
   - Select an appropriate screen_component from the available list
   - Include the corresponding field_components for that screen_component

6. Be polite when asking for missing information. If the user doesn't specify something important, ask for it specifically.

7. Keep track of the current state of the journey as the conversation progresses.

Available screen components: 
{screen_components}

Remember: Return ONLY the JSON object with no additional text or explanations.
"""

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/start', methods=['POST'])
def start_session():
    """Start a new session and initialize the journey creation process"""
    # Generate a new session ID
    session_id = str(uuid.uuid4())
    
    # Fetch available screen components
    screen_components = fetch_screen_components()
    
    # Initialize session with screen components info
    sessions[session_id] = {
        "journey": {
            "journey_name": "",
            "journey_type": "single",
            "no_screens": 0,
            "screens": [],
            "navigation": []
        },
        "messages": [],
        "screen_components": screen_components
    }
    
    # Format screen components for prompt
    screen_components_info = "\n".join([
        f"- ID: {sc['screen_component_id']}, Name: {sc['screen_component_name']}" 
        for sc in screen_components
    ])
    
    # Add system prompt to messages
    system_prompt = SYSTEM_PROMPT.format(screen_components=screen_components_info)
    sessions[session_id]["messages"].append({"role": "system", "content": system_prompt})
    
    # Create welcome message
    next_prompt = ("Hi! I'll help you create a journey for your banking application. "
                  "What would you like to name this journey? "
                  "Please tell me what type of journey you want to create (e.g., Savings Account Opening, Loan Application).")
    
    logger.info(f"Session started: {session_id}")
    return jsonify({
        "message": "session started",
        "next_prompt": next_prompt,
        "final": False,
        "session_id": session_id
    })

@app.route('/api/process', methods=['POST'])
def process_message():
    """Process user message and progress the journey creation"""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')
    
    if not session_id or not user_message or session_id not in sessions:
        logger.error(f"Invalid request: session_id={session_id}")
        return jsonify({"error": "Invalid session ID or message"}), 400
    
    session_data = sessions[session_id]
    
    # Add user message to conversation history
    session_data["messages"].append({"role": "user", "content": user_message})
    
    # Check for confirmation or cancellation commands
    is_final = False
    if user_message.lower() == 'confirm':
        is_final = True
        next_prompt = "Your journey has been confirmed and saved. Thank you!"
    elif user_message.lower() == 'cancel':
        # Reset journey
        session_data["journey"] = {
            "journey_name": "",
            "journey_type": "single",
            "no_screens": 0,
            "screens": [],
            "navigation": []
        }
        next_prompt = "Journey creation has been cancelled. Let's start again. What would you like to name this journey?"
    else:
        # Process with Gemini
        try:
            # Create a message for Gemini that includes the current journey state
            gemini_prompt = f"""
Current journey state:
{json.dumps(session_data['journey'], indent=2)}

User message: {user_message}

Create or update the journey JSON based on the user's message. 
Return ONLY the JSON with no explanations or additional text.
"""
            session_data["messages"].append({"role": "user", "content": gemini_prompt})
            
            # Get Gemini's response
            gemini_messages = [msg for msg in session_data["messages"]]
            response = model.generate_content(gemini_messages)
            
            # Extract JSON from response
            try:
                response_text = response.text
                # Clean the response if it contains markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                journey_json = json.loads(response_text)
                
                # Update the session's journey data
                session_data["journey"] = journey_json
                
                # Generate next prompt for user
                next_prompt_prompt = f"""
Based on the current journey JSON and the user's last message, generate a friendly, non-technical prompt 
to guide the user to the next step in creating their journey. 

Do not expose any JSON or technical details to the user. Use simple language.

Current journey: {json.dumps(journey_json, indent=2)}
User's last message: {user_message}

Generate a helpful prompt that:
1. Summarizes what has been done so far
2. Asks for specific information needed next
3. Provides options for the user (if applicable)
4. Explains how to confirm, change or cancel
"""
                prompt_response = model.generate_content(next_prompt_prompt)
                next_prompt = prompt_response.text.strip()
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response: {response.text}")
                next_prompt = "I'm having trouble understanding that. Could you please clarify your requirements for the journey?"
        
        except Exception as e:
            logger.error(f"Error processing with Gemini: {str(e)}")
            next_prompt = "Sorry, I encountered an error processing your request. Please try again."
    
    # Add response to message history (if not confirmation/cancellation)
    if not is_final and user_message.lower() != 'cancel':
        session_data["messages"].append({"role": "assistant", "content": json.dumps(session_data["journey"])})
    
    logger.info(f"Processed message for session {session_id}, is_final={is_final}")
    return jsonify({
        "journey_json": session_data["journey"],
        "next_prompt": next_prompt,
        "final": is_final
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)