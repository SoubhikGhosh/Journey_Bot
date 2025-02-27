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
genai.configure(api_key="AIzaSyD2ArK74wBtL1ufYmpyrV2LqaOBrSi3mlU")
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
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
    
    # Check navigation completeness
    navigation = journey.get("navigation", [])
    if not navigation and len(screens) > 1:
        return {"valid": False, "message": "Add navigation between your screens."}
    
    # Check for missing trigger components in navigation
    missing_triggers = []
    for i, nav in enumerate(navigation):
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
2. The journey structure follows this format:
   - journey_name: Name of the journey (e.g., "SavingAccountJourney")
   - journey_type: "single" 
   - no_screens: Number of screens in the journey (must match the length of the screens array)
   - screens: Array of screen objects
   - navigation: Array of navigation rules between screens

3. For screens, only include fields that the user has explicitly mentioned or that are necessary.
   Do not assume any structure or required fields.

4. Do not make any assumptions about the required structure of screen_component objects.
   Only include fields that the user has explicitly mentioned.

5. Do not make any assumptions about the structure of navigation objects.
   Only include fields that the user has explicitly mentioned.

6. You can ONLY use the screen components available in the list below. DO NOT create new screen components.

7. If the user requests a component that's not available in the list below:
   - DO NOT try to create or add that component
   - In your next_prompt response (not in the JSON), inform the user that the requested component is not available
   - Suggest they choose from the available components instead
   - DO NOT include unavailable components in the JSON

8. When the user selects a screen component:
   - Add it to the journey with minimal structure
   - Field components will be fetched separately via API
   - DO NOT pre-populate field components

9. Always make sure the no_screens field matches the actual number of screens in the journey.

10. Inform the user of the available screen components.

11. Be polite when asking for missing information. If the user doesn't specify something important, ask for it specifically.

12. Keep track of the current state of the journey as the conversation progresses.

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
                
                # Process each screen
                for screen in new_screens:
                    # Check if this is a new screen or an existing one
                    existing_screen = next((s for s in current_screens if s.get("screen_id") == screen.get("screen_id")), None)
                    
                    # Process each screen component in this screen
                    if "screen_components" in screen:
                        for screen_component in screen["screen_components"]:
                            # Check if this is a new screen component
                            is_new_component = True
                            if existing_screen and "screen_components" in existing_screen:
                                for existing_component in existing_screen["screen_components"]:
                                    if existing_component.get("screen_component_id") == screen_component.get("screen_component_id"):
                                        is_new_component = False
                                        break
                            
                            # If this is a new component or doesn't have field_components, fetch them
                            if is_new_component or "field_components" not in screen_component or not screen_component["field_components"]:
                                component_name = screen_component.get("screen_component_name")
                                if component_name:
                                    # Fetch field components
                                    logger.info(f"Fetching field components for {component_name}")
                                    field_components = fetch_field_components(component_name)
                                    screen_component["field_components"] = field_components
                
                # Process navigation to look for missing trigger components
                has_multiple_triggers = False
                trigger_options = {}
                
                for nav in journey_json.get("navigation", []):
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
                
                # Update the session's journey data
                session_data["journey"] = journey_json
                
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
Journey status message: {journey_status_message}

VERY IMPORTANT: You must ONLY offer the user choices from the available screen components in the list below.
Do NOT suggest or imply that they can add any components not in this list (like text, images, buttons, etc.).
Instead, present the exact screen component options available and ask them to choose from these specific options.

Available screen components (ONLY THESE can be used):
{screen_components_info}

Generate a helpful prompt that:
1. Summarizes what has been done so far
2. Lists the EXACT available screen components by name and asks the user to choose from ONLY these options
3. If there are multiple trigger components that need user selection, include the formatted message about choosing trigger components
4. If there are journey completion requirements, include the message about what's needed to complete the journey
5. Explains how to confirm, change or cancel

IMPORTANT: DO NOT mention any components or options not in the available screen components list.
"""
                next_prompt = get_gemini_response(next_prompt_prompt)
                
                # If multiple triggers were found, append the trigger selection message
                if has_multiple_triggers and multiple_triggers_message not in next_prompt:
                    next_prompt = f"{next_prompt}\n\n{multiple_triggers_message}"
                
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