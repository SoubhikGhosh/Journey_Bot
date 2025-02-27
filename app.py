from flask import Flask, request, jsonify, session
from flask_cors import CORS
import google.generativeai as genai
import uuid
import logging
import json
import re
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
genai.configure(api_key="AIzaSyCD6DGeERwWQbBC6BK1Hq0ecagQj72rqyQ")
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

# New endpoint to fetch field components for a screen component
@app.route('/journey/api/field-components/<screen_component_name>', methods=['GET'])
def get_field_components(screen_component_name):
    """API endpoint to get field components for a specific screen component"""
    field_components = fetch_field_components(screen_component_name)
    return jsonify(field_components)

# Function to extract trigger component selection from user message
def extract_trigger_selection(message, screen_names):
    """
    Extract trigger component selection from user message
    Returns a dict with screen_id/name as key and trigger_id as value
    """
    selections = {}
    
    # Common patterns for trigger selection
    patterns = [
        r"use trigger (?:component )?(id )?(\d+) for (?:screen )?(?:id )?(\d+|[a-zA-Z]+)",
        r"for (?:screen )?(?:id )?(\d+|[a-zA-Z]+) use trigger (?:component )?(id )?(\d+)",
        r"select trigger (?:component )?(id )?(\d+) for (?:screen )?(?:id )?(\d+|[a-zA-Z]+)",
        r"choose trigger (?:component )?(id )?(\d+) for (?:screen )?(?:id )?(\d+|[a-zA-Z]+)"
    ]
    
    # Try to match patterns
    for pattern in patterns:
        matches = re.findall(pattern, message.lower())
        if matches:
            for match in matches:
                if len(match) == 3:  # pattern with "for screen X use trigger Y"
                    screen_identifier = match[2]
                    trigger_id = match[1]
                elif len(match) == 2:  # pattern with "use trigger X for screen Y"
                    trigger_id = match[1]
                    screen_identifier = match[0]
                
                # Try to convert screen identifier to id if it's a number
                try:
                    screen_id = int(screen_identifier)
                    selections[screen_id] = int(trigger_id)
                except ValueError:
                    # It might be a screen name
                    screen_name = screen_identifier.lower()
                    if screen_name in screen_names:
                        selections[screen_name] = int(trigger_id)
    
    return selections

# Function to validate the journey
def validate_journey(journey, full_check=True):
    """
    Validate the journey for completeness and correctness
    Returns dict with valid (bool) and message (str) keys
    """
    # Check for required top-level fields
    if not journey.get("journey_name"):
        return {"valid": False, "message": "Add a name for your journey."}
    
    # Check for screens
    screens = journey.get("screens", [])
    if not screens:
        return {"valid": False, "message": "Add at least one screen to your journey."}
    
    # Verify no_screens matches actual screen count
    if journey.get("no_screens", 0) != len(screens):
        journey["no_screens"] = len(screens)
    
    # Don't perform detailed validation unless we're doing a full check (e.g., for confirmation)
    if not full_check:
        return {"valid": True, "message": ""}
    
    # Check for required fields in each screen
    for screen in screens:
        if "screen_id" not in screen:
            return {"valid": False, "message": "All screens must have a screen_id."}
        if "screen_name" not in screen:
            return {"valid": False, "message": f"Screen with ID {screen['screen_id']} is missing a screen_name."}
        if "template" not in screen:
            return {"valid": False, "message": f"Screen {screen['screen_name']} is missing a template."}
        if "style" not in screen:
            return {"valid": False, "message": f"Screen {screen['screen_name']} is missing a style."}
        if "screen_components" not in screen:
            return {"valid": False, "message": f"Screen {screen['screen_name']} is missing screen_components."}
        
        # Check each screen component
        for sc in screen.get("screen_components", []):
            if "screen_component_id" not in sc:
                return {"valid": False, "message": f"A screen component in screen {screen['screen_name']} is missing a screen_component_id."}
            if "screen_component_name" not in sc:
                return {"valid": False, "message": f"Screen component {sc.get('screen_component_id')} in screen {screen['screen_name']} is missing a screen_component_name."}
            if "screen_component_style" not in sc:
                return {"valid": False, "message": f"Screen component {sc.get('screen_component_name')} in screen {screen['screen_name']} is missing a screen_component_style."}
            if "field_components" not in sc:
                return {"valid": False, "message": f"Screen component {sc.get('screen_component_name')} in screen {screen['screen_name']} is missing field_components."}
    
    # Check navigation completeness
    navigation = journey.get("navigation", [])
    if not navigation and len(screens) > 1:
        return {"valid": False, "message": "Add navigation between your screens."}
    
    # Check required fields in navigation
    for nav in navigation:
        if "source_screen_id" not in nav:
            return {"valid": False, "message": "A navigation rule is missing source_screen_id."}
        if "target_screen_id" not in nav:
            return {"valid": False, "message": "A navigation rule is missing target_screen_id."}
        if "navigation_type" not in nav:
            return {"valid": False, "message": "A navigation rule is missing navigation_type."}
    
    # Check for missing trigger components in navigation
    missing_triggers = []
    for nav in navigation:
        if "source_screen_id" in nav and "target_screen_id" in nav:
            if "trigger_component_id" not in nav:
                source_id = nav["source_screen_id"]
                source_screen = next((s for s in screens if s.get("screen_id") == source_id), None)
                if source_screen and "screen_name" in source_screen:
                    missing_triggers.append(f"navigation from {source_screen['screen_name']} (ID: {source_id})")
                else:
                    missing_triggers.append(f"navigation from screen ID {source_id}")
    
    if missing_triggers:
        return {"valid": False, "message": f"Choose trigger components for: {', '.join(missing_triggers)}"}
    
    # Check for disconnected screens
    if len(screens) > 1:
        # Create a graph of screen connections
        connected_screens = set()
        for nav in navigation:
            if "source_screen_id" in nav and "target_screen_id" in nav:
                connected_screens.add(nav["source_screen_id"])
                connected_screens.add(nav["target_screen_id"])
        
        # Find disconnected screens
        disconnected = []
        for screen in screens:
            if "screen_id" in screen and screen["screen_id"] not in connected_screens:
                if "screen_name" in screen:
                    disconnected.append(f"{screen['screen_name']} (ID: {screen['screen_id']})")
                else:
                    disconnected.append(f"Screen ID {screen['screen_id']}")
        
        if disconnected:
            return {"valid": False, "message": f"Connect these screens to your journey: {', '.join(disconnected)}"}
    
    # All checks passed
    return {"valid": True, "message": ""}

        

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
    current_journey = session_data["journey"]
    
    # Check for confirmation or cancellation commands
    is_final = False
    if user_message.lower() == 'confirm':
        # Validate the journey before confirming
        validation_result = validate_journey(current_journey)
        if validation_result["valid"]:
            is_final = True
            next_prompt = "Your journey has been confirmed and saved. Thank you!"
        else:
            next_prompt = f"Your journey cannot be confirmed yet. {validation_result['message']}"
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
        # Check if the message contains trigger component selection
        # Build a map of screen names to screen IDs for easier reference
        screen_names_map = {}
        for screen in current_journey.get("screens", []):
            if "screen_name" in screen and "screen_id" in screen:
                screen_names_map[screen["screen_name"].lower()] = screen["screen_id"]
        
        # Extract trigger selections if any
        trigger_selections = extract_trigger_selection(user_message, screen_names_map)
        
        # Apply any trigger selections to the navigation
        if trigger_selections:
            # Track which selections were successfully applied
            applied_selections = []
            
            for nav in current_journey.get("navigation", []):
                if "source_screen_id" in nav and "trigger_component_id" not in nav:
                    source_id = nav["source_screen_id"]
                    
                    # Check if we have a selection for this screen (by ID)
                    if source_id in trigger_selections:
                        nav["trigger_component_id"] = trigger_selections[source_id]
                        applied_selections.append(f"Screen ID {source_id}")
                    
                    # Check if we have a selection for this screen (by name)
                    source_screen = next((s for s in current_journey.get("screens", []) 
                                        if s.get("screen_id") == source_id), None)
                    if source_screen and "screen_name" in source_screen:
                        screen_name = source_screen["screen_name"].lower()
                        if screen_name in trigger_selections:
                            nav["trigger_component_id"] = trigger_selections[screen_name]
                            applied_selections.append(f"Screen '{source_screen['screen_name']}'")
            
            # If we applied any selections, notify the user but continue with regular processing
            if applied_selections:
                logger.info(f"Applied trigger selections for: {', '.join(applied_selections)}")
        
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
2. The journey structure MUST EXACTLY follow this format:
   ```json
   {{
     "journey_name": "Name of the journey (e.g., SavingAccountJourney)",
     "journey_type": "single",
     "no_screens": 2,
     "screens": [
       {{
         "screen_id": 1,
         "screen_name": "CustomerDetails",
         "template": "defaultTemplate",
         "style": "defaultScreenStyle",
         "screen_components": [
           {{
             "screen_component_id": 1,
             "screen_component_name": "CustomerDetails",
             "screen_component_style": "defaultScreenComponentStyle",
             "field_components": []
           }}
         ]
       }}
     ],
     "navigation": [
       {{
         "source_screen_id": 1,
         "target_screen_id": 2,
         "trigger_component_id": 10,
         "navigation_type": "button_click"
       }}
     ]
   }}
   ```
   
3. EVERY screen MUST have these exact fields:
   - screen_id
   - screen_name
   - template (always "defaultTemplate")
   - style (always "defaultScreenStyle")
   - screen_components (array)

4. EVERY screen_component MUST have these exact fields:
   - screen_component_id
   - screen_component_name
   - screen_component_style (always "defaultScreenComponentStyle")
   - field_components (array)

5. EVERY navigation MUST have these exact fields:
   - source_screen_id
   - target_screen_id
   - trigger_component_id
   - navigation_type (always "button_click")

6. You can ONLY use the screen components available in the list below. DO NOT create new screen components.

7. The no_screens field MUST match the number of items in the screens array.

8. NEVER use names like "from_screen_id" or "to_screen_id" - use EXACTLY "source_screen_id" and "target_screen_id".

9. NEVER use a structure like "screen_component": {{ "id": 4, "name": "otp" }} - instead use the proper structure with screen_components as an array of objects.

Available screen components (ONLY USE THESE - no exceptions): 
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
                
                # Ensure no_screens matches the actual number of screens
                if "screens" in journey_json:
                    journey_json["no_screens"] = len(journey_json["screens"])
                
                # Check if new screens have been added or updated
                current_screens = current_journey.get("screens", [])
                new_screens = journey_json.get("screens", [])
                
                # Process each screen to ensure proper structure
                for screen in new_screens:
                    # Ensure required screen fields exist
                    if "screen_id" not in screen:
                        screen["screen_id"] = len(new_screens)  # Assign default ID
                    if "screen_name" not in screen:
                        screen["screen_name"] = f"Screen{screen['screen_id']}"
                    if "template" not in screen:
                        screen["template"] = "defaultTemplate"
                    if "style" not in screen:
                        screen["style"] = "defaultScreenStyle"
                    if "screen_components" not in screen:
                        screen["screen_components"] = []
                    
                    # Check if this is a new screen or an existing one
                    existing_screen = next((s for s in current_screens if s.get("screen_id") == screen.get("screen_id")), None)
                    
                    # Process each screen component in this screen
                    if "screen_components" in screen:
                        # Handle case where screen_components is not a list
                        if not isinstance(screen["screen_components"], list):
                            if isinstance(screen["screen_components"], dict):
                                screen["screen_components"] = [screen["screen_components"]]
                            else:
                                screen["screen_components"] = []
                        
                        for i, screen_component in enumerate(screen["screen_components"]):
                            # Ensure screen_component is properly structured
                            if isinstance(screen_component, dict):
                                # Handle different field naming cases
                                if "id" in screen_component and "screen_component_id" not in screen_component:
                                    screen_component["screen_component_id"] = screen_component.pop("id")
                                if "name" in screen_component and "screen_component_name" not in screen_component:
                                    screen_component["screen_component_name"] = screen_component.pop("name")
                                
                                # Ensure all required fields exist
                                if "screen_component_id" not in screen_component:
                                    # Find from available components
                                    if "screen_component_name" in screen_component:
                                        component_name = screen_component["screen_component_name"]
                                        matching = next((c for c in session_data["screen_components"] 
                                                      if c.get("screen_component_name") == component_name), None)
                                        if matching:
                                            screen_component["screen_component_id"] = matching.get("screen_component_id")
                                        else:
                                            screen_component["screen_component_id"] = i + 1
                                    else:
                                        screen_component["screen_component_id"] = i + 1
                                
                                if "screen_component_name" not in screen_component:
                                    # Find from available components
                                    if "screen_component_id" in screen_component:
                                        component_id = screen_component["screen_component_id"]
                                        matching = next((c for c in session_data["screen_components"] 
                                                      if c.get("screen_component_id") == component_id), None)
                                        if matching:
                                            screen_component["screen_component_name"] = matching.get("screen_component_name")
                                        else:
                                            screen_component["screen_component_name"] = f"Component{i+1}"
                                    else:
                                        screen_component["screen_component_name"] = f"Component{i+1}"
                                
                                if "screen_component_style" not in screen_component:
                                    screen_component["screen_component_style"] = "defaultScreenComponentStyle"
                                
                                if "field_components" not in screen_component:
                                    screen_component["field_components"] = []
                                elif not isinstance(screen_component["field_components"], list):
                                    screen_component["field_components"] = []
                            
                            # Check if this is a new screen component or doesn't have field_components
                            is_new_component = True
                            if existing_screen and "screen_components" in existing_screen:
                                for existing_component in existing_screen.get("screen_components", []):
                                    if existing_component.get("screen_component_id") == screen_component.get("screen_component_id"):
                                        is_new_component = False
                                        # Copy field_components if they exist in the existing component
                                        if "field_components" in existing_component and existing_component["field_components"]:
                                            screen_component["field_components"] = existing_component["field_components"]
                                        break
                            
                            # If this is a new component or doesn't have field_components, fetch them
                            if is_new_component or not screen_component.get("field_components"):
                                component_name = screen_component.get("screen_component_name")
                                if component_name:
                                    # Fetch field components
                                    logger.info(f"Fetching field components for {component_name}")
                                    field_components = fetch_field_components(component_name)
                                    screen_component["field_components"] = field_components
                
                # Process navigation to ensure proper structure and look for missing trigger components
                has_multiple_triggers = False
                no_triggers_found = False
                trigger_options = {}
                
                if "navigation" in journey_json:
                    # Handle case where navigation is not a list
                    if not isinstance(journey_json["navigation"], list):
                        if isinstance(journey_json["navigation"], dict):
                            journey_json["navigation"] = [journey_json["navigation"]]
                        else:
                            journey_json["navigation"] = []
                    
                    for nav in journey_json["navigation"]:
                        # Fix navigation field names if needed
                        if "from_screen_id" in nav and "source_screen_id" not in nav:
                            nav["source_screen_id"] = nav.pop("from_screen_id")
                        if "to_screen_id" in nav and "target_screen_id" not in nav:
                            nav["target_screen_id"] = nav.pop("to_screen_id")
                        
                        # Ensure all required fields exist
                        if "navigation_type" not in nav:
                            nav["navigation_type"] = "button_click"
                        
                        # Check if target screen exists
                        if "target_screen_id" in nav:
                            target_id = nav["target_screen_id"]
                            target_exists = any(s.get("screen_id") == target_id for s in journey_json.get("screens", []))
                            
                            if not target_exists:
                                # Remove invalid navigation link
                                logger.warning(f"Removing navigation to non-existent screen ID {target_id}")
                                navigation = journey_json.get("navigation", [])
                                if nav in navigation:
                                    navigation.remove(nav)
                                journey_json["navigation"] = navigation
                                continue
                        
                        # Check if trigger_component_id is missing
                        if "trigger_component_id" not in nav and "source_screen_id" in nav:
                            source_screen_id = nav.get("source_screen_id")
                            
                            # Find the source screen
                            source_screen = next((s for s in journey_json.get("screens", []) 
                                                if s.get("screen_id") == source_screen_id), None)
                            
                            if source_screen and "screen_components" in source_screen:
                                # Find all trigger components in this screen
                                trigger_components = []
                                
                                for sc in source_screen.get("screen_components", []):
                                    for fc in sc.get("field_components", []):
                                        if fc.get("isTriggerComponent") == True:
                                            trigger_components.append({
                                                "id": fc.get("fieldComponentId"),
                                                "name": fc.get("fieldName"),
                                                "label": fc.get("fieldLabel")
                                            })
                                
                                if len(trigger_components) == 1:
                                    # If only one trigger component, use it
                                    nav["trigger_component_id"] = trigger_components[0]["id"]
                                elif len(trigger_components) > 1:
                                    # If multiple trigger components, flag for user selection
                                    has_multiple_triggers = True
                                    trigger_options[str(source_screen_id)] = trigger_components
                                else:
                                    # No trigger components found
                                    no_triggers_found = True
                                    logger.warning(f"No trigger components found for screen {source_screen_id}")
                else:
                    journey_json["navigation"] = []
                
                # Ensure no_screens is correct
                if "screens" in journey_json:
                    journey_json["no_screens"] = len(journey_json["screens"])
                else:
                    journey_json["screens"] = []
                    journey_json["no_screens"] = 0
                
                # Handle case where multiple trigger components exist
                multiple_triggers_message = ""
                if has_multiple_triggers:
                    # Format message about trigger options
                    multiple_triggers_message = "I found multiple possible trigger components for navigation:\n\n"
                    
                    for screen_id, triggers in trigger_options.items():
                        screen_name = next((s.get("screen_name", f"Screen {screen_id}") 
                                           for s in journey_json.get("screens", []) 
                                           if s.get("screen_id") == int(screen_id)), f"Screen {screen_id}")
                        
                        multiple_triggers_message += f"For {screen_name} (ID: {screen_id}), please choose one of these trigger components:\n"
                        for trigger in triggers:
                            multiple_triggers_message += f"  - {trigger['label']} (ID: {trigger['id']})\n"
                    
                    multiple_triggers_message += "\nPlease specify which trigger component to use by typing something like 'Use trigger ID 10 for screen 1' or 'For screen CustomerDetails use trigger ID 13'."
                
                # Handle case where no trigger components found
                no_triggers_message = ""
                if no_triggers_found:
                    no_triggers_message = "\n\nI notice some of your screens don't have trigger components for navigation. The following components have 'isTriggerComponent' set to true and can be used for navigation:\n\n"
                    
                    # Find all available trigger components
                    available_triggers = []
                    for screen in journey_json.get("screens", []):
                        screen_id = screen.get("screen_id")
                        screen_name = screen.get("screen_name", f"Screen {screen_id}")
                        
                        for sc in screen.get("screen_components", []):
                            for fc in sc.get("field_components", []):
                                if fc.get("fieldType") == "button":
                                    trigger_status = "is a trigger" if fc.get("isTriggerComponent") == True else "is NOT currently a trigger"
                                    available_triggers.append({
                                        "screen_id": screen_id,
                                        "screen_name": screen_name,
                                        "component_id": fc.get("fieldComponentId"),
                                        "component_name": fc.get("fieldName"),
                                        "component_label": fc.get("fieldLabel"),
                                        "is_trigger": fc.get("isTriggerComponent") == True
                                    })
                    
                    if available_triggers:
                        for trigger in available_triggers:
                            status = "✓ Is a trigger component" if trigger["is_trigger"] else "× Not a trigger component"
                            no_triggers_message += f"  - {trigger['component_label']} (ID: {trigger['component_id']}) on {trigger['screen_name']} - {status}\n"
                        
                        no_triggers_message += "\nPlease choose appropriate trigger components for your navigation. You can only create navigation links between existing screens."
                    else:
                        no_triggers_message += "I couldn't find any button components that could serve as triggers. Please add button components to your screens first."
                
                # Check if the journey is complete or what's missing
                journey_status = validate_journey(journey_json, full_check=False)
                journey_status_message = ""
                if not journey_status["valid"]:
                    journey_status_message = f"\n\nTo complete your journey, you need to: {journey_status['message']}"
                
                # Generate next prompt for user
                next_prompt_prompt = f"""
Based on the current journey JSON and the user's last message, generate a friendly, non-technical prompt 
to guide the user to the next step in creating their journey. 

Current journey: {json.dumps(journey_json, indent=2)}
User's last message: {user_message}

Multiple trigger components flag: {has_multiple_triggers}
Trigger component message: {multiple_triggers_message}
No triggers found flag: {no_triggers_found}
No triggers message: {no_triggers_message}
Journey status message: {journey_status_message}

VERY IMPORTANT: You must ONLY offer the user choices from the available screen components in the list below.
Do NOT suggest or imply that they can add any components not in this list (like generic text, images, buttons, etc.).
Instead, present the exact screen component options available and ask them to choose from these specific options.

ALSO IMPORTANT: Do NOT allow navigation to screens that don't exist. Only allow navigation between screens
that have already been created. Politely refuse any attempts to create navigation to unknown screens.

Available screen components (ONLY THESE can be used):
{screen_components_info}

Generate a helpful prompt that:
1. Summarizes what has been done so far
2. Lists the EXACT available screen components by name and asks the user to choose from ONLY these options
3. If there are multiple trigger components that need user selection, include the formatted message about choosing trigger components
4. If there are no trigger components found on a screen that needs one, include the no_triggers_message
5. If there are journey completion requirements, include the message about what's needed to complete the journey
6. Explains how to confirm, change or cancel

IMPORTANT: DO NOT mention any components or options not in the available screen components list.
If the user tries to navigate to a non-existent screen, politely explain that they can only create navigation 
between screens that already exist in the journey.
"""
                next_prompt = get_gemini_response(next_prompt_prompt)
                
                # If multiple triggers were found, append the trigger selection message
                if has_multiple_triggers and multiple_triggers_message not in next_prompt:
                    next_prompt = f"{next_prompt}\n\n{multiple_triggers_message}"
                
                # If no triggers were found, append the message
                if no_triggers_found and no_triggers_message not in next_prompt:
                    next_prompt = f"{next_prompt}\n\n{no_triggers_message}"
                
                # Add journey status message if not already included
                if journey_status_message and journey_status_message not in next_prompt:
                    next_prompt = f"{next_prompt}{journey_status_message}"
                
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
        "final": is_final,
        "needs_trigger_selection": any("trigger_component_id" not in nav for nav in session_data["journey"].get("navigation", []))
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)