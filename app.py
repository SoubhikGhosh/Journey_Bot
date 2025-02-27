from flask import Flask, request, jsonify, session
from flask_cors import CORS
import google.generativeai as genai
import uuid
import logging
import json
from datetime import datetime

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

# Function to get response from Gemini
def get_gemini_response(prompt_text):
    try:
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return '{}'

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

# Sample field components response - used for mocking only
SAMPLE_FIELD_COMPONENTS = {
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

# Function to fetch field components for a screen component
def fetch_field_components(screen_component_name):
    """
    Function to fetch field components for a screen component from secondary backend
    
    For now, we'll use a mock implementation, but in production:
    import requests
    response = requests.get(f"https://backend.example.com/api/field-components/{screen_component_name}")
    return response.json()
    """
    logger.info(f"Fetching field components for: {screen_component_name}")
    
    # Mock response - this would be replaced with actual API call
    if screen_component_name == "CustomerDetails":
        # Return a more complete field components list from the document
        return [
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
            },
            {
                "fieldComponentId": 2,
                "fieldType": "text_field",
                "fieldName": "lastname",
                "fieldLabel": "Last Name",
                "validations": {
                    "required": True,
                    "requiredMessage": "Last Name is required",
                    "minLength": 3,
                    "minLengthMessage": "Lastname must be at least 3 characters",
                    "helperText": "Enter a Lastname between 3-20 characters"
                },
                "dataSource": None,
                "dependencies": None,
                "isTriggerComponent": False,
                "createdAt": "2025-02-23T12:07:33.156551",
                "updatedAt": "2025-02-23T12:07:33.136884",
                "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 10,
                "fieldType": "button",
                "fieldName": "customDtlBtn",
                "fieldLabel": "Proceed >",
                "validations": {},
                "dataSource": None,
                "dependencies": None,
                "isTriggerComponent": True,
                "createdAt": "2025-02-23T12:15:13.945457",
                "updatedAt": "2025-02-23T12:15:13.930879",
                "style": "defaultFieldStyle"
            }
        ]
    elif screen_component_name == "pan":
        return [
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
            },
            {
                "fieldComponentId": 12,
                "fieldType": "text_field",
                "fieldName": "pan",
                "fieldLabel": "PAN",
                "validations": {
                    "required": True,
                    "pattern": "[A-Z]{5}[0-9]{4}[A-Z]",
                    "patternError": "Please enter a valid PAN number"
                },
                "dataSource": None,
                "dependencies": None,
                "isTriggerComponent": False,
                "createdAt": "2025-02-23T12:18:15.277552",
                "updatedAt": "2025-02-23T12:18:15.26131",
                "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 13,
                "fieldType": "button",
                "fieldName": "validatePanBtn",
                "fieldLabel": "Validate PAN",
                "validations": {},
                "dataSource": None,
                "dependencies": None,
                "isTriggerComponent": True,
                "createdAt": "2025-02-23T12:19:33.008951",
                "updatedAt": "2025-02-23T12:19:32.995502",
                "style": "defaultFieldStyle"
            }
        ]
    elif screen_component_name == "aadhar":
        return [
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
            },
            {
                "fieldComponentId": 15,
                "fieldType": "text_field",
                "fieldName": "aadhar",
                "fieldLabel": "Aadhar Number",
                "validations": {
                    "required": True,
                    "pattern": "[0-9]{12}",
                    "patternError": "Please enter a valid Aadhar number"
                },
                "dataSource": None,
                "dependencies": None,
                "isTriggerComponent": False,
                "createdAt": "2025-02-23T12:28:06.266728",
                "updatedAt": "2025-02-23T12:28:06.257313",
                "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 16,
                "fieldType": "button",
                "fieldName": "validateAadhar",
                "fieldLabel": "Validate Aadhar",
                "validations": {},
                "dataSource": "validateaadhar",
                "dependencies": None,
                "isTriggerComponent": True,
                "createdAt": "2025-02-23T12:28:51.948309",
                "updatedAt": "2025-02-23T12:28:51.923045",
                "style": "defaultFieldStyle"
            }
        ]
    elif screen_component_name == "otp":
        return [
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
            },
            {
                "fieldComponentId": 18,
                "fieldType": "otp",
                "fieldName": "otp",
                "fieldLabel": "OTP",
                "validations": {},
                "dataSource": None,
                "dependencies": None,
                "isTriggerComponent": False,
                "createdAt": "2025-02-23T12:29:30.918031",
                "updatedAt": "2025-02-23T12:29:30.908255",
                "style": "defaultFieldStyle"
            }
        ]
    elif screen_component_name == "status":
        return [
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
            },
            {
                "fieldComponentId": 20,
                "fieldType": "button",
                "fieldName": "homeScreenButton",
                "fieldLabel": "Home Screen",
                "validations": {},
                "dataSource": "gotohomescreen",
                "dependencies": None,
                "isTriggerComponent": False,
                "createdAt": "2025-02-23T23:25:36.440081",
                "updatedAt": "2025-02-23T23:25:36.419469",
                "style": "defaultFieldStyle"
            }
        ]
    
    # Default empty array for unknown components
    return []

@app.route('/journey/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/journey/api/start', methods=['GET'])
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
        "screen_components": screen_components
    }
    
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

@app.route('/journey/api/process', methods=['POST'])
def process_message():
    """Process user message and progress the journey creation"""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')
    
    if not session_id or not user_message or session_id not in sessions:
        logger.error(f"Invalid request: session_id={session_id}")
        return jsonify({"error": "Invalid session ID or message"}), 400
    
    session_data = sessions[session_id]
    
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
            # Format available screen components
            screen_components_info = "\n".join([
                f"- ID: {sc['screen_component_id']}, Name: {sc['screen_component_name']}" 
                for sc in session_data["screen_components"]
            ])
            
            # Create a message for Gemini that includes the current journey state
            gemini_prompt = f"""
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

4. Each screen_component object MUST contain all of these fields:
   - screen_component_id: Numeric ID 
   - screen_component_name: Name of the component
   - screen_component_style: Use "defaultScreenComponentStyle"
   - field_components: Array (can be empty, will be filled automatically)

5. Each navigation object MUST contain all of these fields:
   - source_screen_id: ID of the starting screen
   - target_screen_id: ID of the destination screen
   - trigger_component_id: ID of the field component that triggers navigation
   - navigation_type: Use "button_click"

6. For trigger_component_id in navigation: 
   - Use the fieldComponentId of a component in the source screen where "isTriggerComponent": true
   - If multiple trigger components exist, ask the user to choose
   - If no trigger component exists, create navigation but ask the user to add one

7. You CANNOT create new screen_components or field_components. You must use existing ones from the provided lists.

8. When the user wants to add a new screen, you must:
   - Select an appropriate screen_component from the available list
   - For field_components, the system will automatically fetch them - just include an empty field_components array

9. If the user requests a specific screen component by name or function, choose the most appropriate one from the available options. If the user's request is ambiguous, select the most relevant screen component.

10. Be polite when asking for missing information. If the user doesn't specify something important, ask for it specifically.

11. Keep track of the current state of the journey as the conversation progresses.

Available screen components: 
{screen_components_info}

Current journey state:
{json.dumps(session_data['journey'], indent=2)}

User message: {user_message}

Create or update the journey JSON based on the user's message. 
Return ONLY the JSON with no explanations or additional text.
"""
            # Get Gemini's response
            response_text = get_gemini_response(gemini_prompt)
            
            # Extract JSON from response
            try:
                # Clean the response if it contains markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                journey_json = json.loads(response_text)
                
                # Check if new screens have been added or updated that need field components
                current_screens = session_data["journey"].get("screens", [])
                new_screens = journey_json.get("screens", [])
                
                # Process each screen to see if we need to fetch field components
                for screen in new_screens:
                    # Find if this screen already exists in the current journey
                    existing_screen = next((s for s in current_screens if s.get("screen_id") == screen.get("screen_id")), None)
                    
                    # Process screen components for this screen
                    for screen_component in screen.get("screen_components", []):
                        # Ensure all required fields are present in screen_component
                        if "screen_component_id" not in screen_component:
                            # If missing, try to find from available components by name
                            component_name = screen_component.get("screen_component_name")
                            matching_component = next((c for c in session_data["screen_components"] 
                                                    if c.get("screen_component_name") == component_name), None)
                            if matching_component:
                                screen_component["screen_component_id"] = matching_component.get("screen_component_id")
                            else:
                                # Assign a default ID if not found
                                screen_component["screen_component_id"] = 999
                        
                        # Ensure screen_component_name is present
                        if "screen_component_name" not in screen_component:
                            # Try to find from available components by ID
                            component_id = screen_component.get("screen_component_id")
                            matching_component = next((c for c in session_data["screen_components"] 
                                                    if c.get("screen_component_id") == component_id), None)
                            if matching_component:
                                screen_component["screen_component_name"] = matching_component.get("screen_component_name")
                            else:
                                # Assign a default name if not found
                                screen_component["screen_component_name"] = "DefaultComponent"
                        
                        # Ensure screen_component_style is present
                        if "screen_component_style" not in screen_component:
                            screen_component["screen_component_style"] = "defaultScreenComponentStyle"
                        
                        # If this is a new screen component or has no field components yet, fetch them
                        if not existing_screen or not any(
                            sc.get("screen_component_id") == screen_component.get("screen_component_id") 
                            for sc in existing_screen.get("screen_components", [])
                        ) or "field_components" not in screen_component or not screen_component["field_components"]:
                            # Get the component name
                            component_name = screen_component.get("screen_component_name")
                            if component_name:
                                # Fetch field components from API
                                logger.info(f"Fetching field components for {component_name}")
                                field_components = fetch_field_components(component_name)
                                screen_component["field_components"] = field_components
                
                # Process navigation to ensure all required fields are present
                for navigation in journey_json.get("navigation", []):
                    # Ensure all required fields are present
                    if "navigation_type" not in navigation:
                        navigation["navigation_type"] = "button_click"
                    
                    # Check if trigger_component_id is missing
                    if "trigger_component_id" not in navigation:
                        source_screen_id = navigation.get("source_screen_id")
                        source_screen = next((s for s in journey_json.get("screens", []) 
                                            if s.get("screen_id") == source_screen_id), None)
                        
                        if source_screen:
                            # Find trigger components in the source screen
                            trigger_components = []
                            for sc in source_screen.get("screen_components", []):
                                for fc in sc.get("field_components", []):
                                    if fc.get("isTriggerComponent") == True:
                                        trigger_components.append(fc)
                            
                            if len(trigger_components) == 1:
                                # If only one trigger component, use it
                                navigation["trigger_component_id"] = trigger_components[0].get("fieldComponentId")
                            elif len(trigger_components) > 1:
                                # If multiple, use the first one but log a warning
                                navigation["trigger_component_id"] = trigger_components[0].get("fieldComponentId")
                                logger.warning(f"Multiple trigger components found for screen {source_screen_id}. Using first one.")
                            else:
                                # If none, assign a default
                                logger.warning(f"No trigger component found for screen {source_screen_id}. Using default.")
                                navigation["trigger_component_id"] = 999
                
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
2. Asks for specific information needed next (only required fields)
3. Does not contain any suggestion for creating any field component or screen component
4. Explains how to confirm, change or cancel
"""
                next_prompt = get_gemini_response(next_prompt_prompt)
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response: {response_text}")
                next_prompt = "I'm having trouble understanding that. Could you please clarify your requirements for the journey?"
        
        except Exception as e:
            logger.error(f"Error processing with Gemini: {str(e)}")
            next_prompt = "Sorry, I encountered an error processing your request. Please try again."
    
    logger.info(f"Processed message for session {session_id}, is_final={is_final}")
    return jsonify({
        "journey_json": session_data["journey"],
        "next_prompt": next_prompt,
        "final": is_final
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)