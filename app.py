from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import uuid
import logging
import json
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

# Helper function to detect ambiguous inputs
def is_ambiguous_input(message):
    """Check if the user message is too vague to generate a journey structure"""
    ambiguous_patterns = [r'^add \d+ screens?$', r'^create \d+ screens?$', r'^make \d+ screens?$']
    return any(re.match(pattern.strip(), message.strip(), re.IGNORECASE) for pattern in ambiguous_patterns)

# Function to get response from Gemini
def get_gemini_response(prompt_text, user_message=None):
    try:
        # Check if user message is ambiguous before sending to Gemini
        if user_message and is_ambiguous_input(user_message):
            return "I need more specific information. Please provide details about what kind of screens you'd like to add, their names, and their components."
        
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return '{}'

# Function to fetch screen components (mocked)
def fetch_screen_components():
    """Mock function to fetch screen components from secondary backend"""
    return MOCK_SCREEN_COMPONENTS

# Function to fetch field components for a screen component
def fetch_field_components(screen_component_name):
    """Simplified field components fetch function with minimal data"""
    logger.info(f"Fetching field components for: {screen_component_name}")
    
    # Basic components for different screen types (simplified)
    basic_components = {
        "CustomerDetails": [
            {"fieldComponentId": 1, "fieldType": "largetext", "fieldName": "customerDetailsHeading", "fieldLabel": "Enter Customer Details", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"},
            {"fieldComponentId": 10, "fieldType": "button", "fieldName": "customDtlBtn", "fieldLabel": "Proceed >", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": True, "style": "defaultFieldStyle"}
        ],
        "pan": [
            {"fieldComponentId": 11, "fieldType": "largetext", "fieldName": "panDetailsHeading", "fieldLabel": "Enter PAN Details", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"},
            {"fieldComponentId": 13, "fieldType": "button", "fieldName": "validatePanBtn", "fieldLabel": "Validate PAN", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": True, "style": "defaultFieldStyle"}
        ],
        "aadhar": [
            {"fieldComponentId": 14, "fieldType": "largetext", "fieldName": "aadharHeadingDetails", "fieldLabel": "Enter Aadhar Details", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"},
            {"fieldComponentId": 16, "fieldType": "button", "fieldName": "validateAadhar", "fieldLabel": "Validate Aadhar", 
             "validations": {}, "dataSource": "validateaadhar", "dependencies": None, "isTriggerComponent": True, "style": "defaultFieldStyle"}
        ],
        "otp": [
            {"fieldComponentId": 17, "fieldType": "largetext", "fieldName": "otpHeading", "fieldLabel": "Enter OTP", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"},
            {"fieldComponentId": 18, "fieldType": "otp", "fieldName": "otp", "fieldLabel": "OTP", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"}
        ],
        "status": [
            {"fieldComponentId": 19, "fieldType": "statustext", "fieldName": "status", "fieldLabel": "status", 
             "validations": {}, "dataSource": None, "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"},
            {"fieldComponentId": 20, "fieldType": "button", "fieldName": "homeScreenButton", "fieldLabel": "Home Screen", 
             "validations": {}, "dataSource": "gotohomescreen", "dependencies": None, "isTriggerComponent": False, "style": "defaultFieldStyle"}
        ]
    }
    
    return basic_components.get(screen_component_name, [])

# Function to extract trigger component selection from user message
def extract_trigger_selection(message, screen_names):
    """Extract trigger component selection from user message"""
    selections = {}
    patterns = [
        r"use trigger (?:component )?(id )?(\d+) for (?:screen )?(?:id )?(\d+|[a-zA-Z]+)",
        r"for (?:screen )?(?:id )?(\d+|[a-zA-Z]+) use trigger (?:component )?(id )?(\d+)",
        r"select trigger (?:component )?(id )?(\d+) for (?:screen )?(?:id )?(\d+|[a-zA-Z]+)",
        r"choose trigger (?:component )?(id )?(\d+) for (?:screen )?(?:id )?(\d+|[a-zA-Z]+)"
    ]
    
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
    """Validate the journey for completeness and correctness"""
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
    
    # Skip detailed validation if not doing a full check
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
    user_msg_lower = user_message.lower().strip()
    
    # Command synonyms
    confirm_commands = ['confirm', 'yes', 'ok', 'finished', 'done', 'complete', 'save', 'submit']
    cancel_commands = ['cancel', 'reset', 'restart', 'start over', 'clear', 'begin again']
    quit_commands = ['quit', 'exit', 'close', 'end', 'terminate', 'goodbye', 'bye']
    
    if any(user_msg_lower == cmd for cmd in confirm_commands):
        # Validate the journey before confirming
        validation_result = validate_journey(current_journey)
        if validation_result["valid"]:
            is_final = True
            next_prompt = "Your journey has been confirmed and saved. Thank you!"
            # Clean up the session after successful confirmation
            if session_id in sessions:
                del sessions[session_id]
                logger.info(f"Session {session_id} cleared after confirmation")
        else:
            next_prompt = f"Your journey cannot be confirmed yet. {validation_result['message']}"
    
    elif any(user_msg_lower == cmd for cmd in cancel_commands):
        # Reset journey
        session_data["journey"] = {
            "journey_name": "",
            "journey_type": "single",
            "no_screens": 0,
            "screens": [],
            "navigation": []
        }
        next_prompt = "Journey creation has been cancelled. Let's start again. What would you like to name this journey?"
    
    elif any(user_msg_lower == cmd for cmd in quit_commands):
        # Clean up the session when user quits
        if session_id in sessions:
            del sessions[session_id]
            logger.info(f"Session {session_id} cleared after quit command")
        next_prompt = "Your journey session has been closed. Thank you for using our service."
        is_final = True
        
    else:
        # Check if user message is too ambiguous
        if is_ambiguous_input(user_message):
            next_prompt = ("I need more specific information. Please provide details about what kind of screens "
                          "you'd like to add, their names, and their components. You can choose from these components: " +
                          ", ".join([comp["screen_component_name"] for comp in session_data["screen_components"]]))
            return jsonify({
                "journey_json": current_journey,
                "next_prompt": next_prompt,
                "final": False,
                "needs_trigger_selection": any("trigger_component_id" not in nav for nav in current_journey.get("navigation", []))
            })
            
        # Process trigger component selections if any
        screen_names_map = {screen["screen_name"].lower(): screen["screen_id"] for screen in current_journey.get("screens", []) if "screen_name" in screen}
        trigger_selections = extract_trigger_selection(user_message, screen_names_map)
        
        # Apply trigger selections to navigation
        if trigger_selections:
            for nav in current_journey.get("navigation", []):
                if "source_screen_id" in nav and "trigger_component_id" not in nav:
                    source_id = nav["source_screen_id"]
                    if source_id in trigger_selections:
                        nav["trigger_component_id"] = trigger_selections[source_id]
        
        # Process with Gemini
        try:
            # Format available screen components
            screen_components_info = "\n".join([
                f"- ID: {sc['screen_component_id']}, Name: {sc['screen_component_name']}" 
                for sc in session_data["screen_components"]
            ])
            
            # Create prompt for Gemini
            gemini_prompt = f"""
You are an AI assistant that helps users create journey JSON configurations for a banking application. 
Your task is to generate JSON based on user requirements, following these rules:

1. You must ONLY return valid JSON in your response - no explanations, no comments, no additional text.
2. DO NOT make assumptions about the journey structure. If the user's request is vague or ambiguous, 
   do not generate JSON. Instead, return a plain text message asking for more specific details.
3. Only add elements that the user explicitly requests. Do not populate screens or components unless 
   specifically instructed by the user.
4. The journey structure MUST EXACTLY follow this format:
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
   
5. EVERY screen MUST have these exact fields:
   - screen_id
   - screen_name
   - template (always "defaultTemplate")
   - style (always "defaultScreenStyle")
   - screen_components (array)

6. EVERY screen_component MUST have these exact fields:
   - screen_component_id
   - screen_component_name
   - screen_component_style (always "defaultScreenComponentStyle")
   - field_components (array)

7. EVERY navigation MUST have these exact fields:
   - source_screen_id
   - target_screen_id
   - trigger_component_id
   - navigation_type (always "button_click")

8. You can ONLY use the screen components available in the list below. DO NOT create new screen components.

9. The no_screens field MUST match the number of items in the screens array.

10. NEVER use names like "from_screen_id" or "to_screen_id" - use EXACTLY "source_screen_id" and "target_screen_id".

11. NEVER use a structure like "screen_component": {{ "id": 4, "name": "otp" }} - instead use the proper structure with screen_components as an array of objects.

12. Do NOT ASSUME or CREATE any data. Let the unknown fields be empty.

13. If the user request is ambiguous (like "add 3 screens" without specifying what screens), add empty but structured screens objects with empty values and direct the user to put in values for each field politely.

Available screen components (ONLY USE THESE - no exceptions): 
{screen_components_info}

Current journey state:
{json.dumps(session_data['journey'], indent=2)}

User message: {user_message}

Create or update the journey JSON based on the user's message. 
Return ONLY the JSON with no explanations or additional text.
If the input is too vague or ambiguous, do not generate a JSON structure - instead return plain text asking for more details.
"""
            # Get Gemini's response
            response_text = get_gemini_response(gemini_prompt, user_message)
            
            # Check if the response is a clarification request rather than JSON
            if not response_text.startswith('{') and not response_text.startswith('[') and '```json' not in response_text:
                # This is a text response asking for clarification, not JSON
                next_prompt = response_text
                logger.info(f"Received clarification request from Gemini: {response_text}")
                
                # Return early without updating the journey
                return jsonify({
                    "journey_json": current_journey,
                    "next_prompt": next_prompt,
                    "final": False,
                    "needs_trigger_selection": any("trigger_component_id" not in nav for nav in current_journey.get("navigation", []))
                })
            
            # Process JSON response
            try:
                # Clean the response if it contains markdown code blocks
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse JSON
                journey_json = json.loads(response_text)
                
                # Process screens and components
                for screen in journey_json.get("screens", []):
                    # Ensure required screen fields
                    if "template" not in screen:
                        screen["template"] = "defaultTemplate"
                    if "style" not in screen:
                        screen["style"] = "defaultScreenStyle"
                    
                    # Process screen components
                    for sc in screen.get("screen_components", []):
                        if "screen_component_style" not in sc:
                            sc["screen_component_style"] = "defaultScreenComponentStyle"
                        
                        # Fetch field components if needed
                        component_name = sc.get("screen_component_name")
                        if not sc.get("field_components") and component_name:
                            sc["field_components"] = fetch_field_components(component_name)
                
                # Process navigation
                for nav in journey_json.get("navigation", []):
                    if "navigation_type" not in nav:
                        nav["navigation_type"] = "button_click"
                
                # Update session data with processed journey
                session_data["journey"] = journey_json
                
                # Check for journey validation issues
                journey_status = validate_journey(journey_json, full_check=False)
                journey_status_message = ""
                if not journey_status["valid"]:
                    journey_status_message = f"\n\nTo complete your journey, you need to: {journey_status['message']}"
                
                # Generate next prompt for user guidance
                next_prompt_prompt = f"""
Based on the current journey JSON and the user's last message, generate a friendly, non-technical prompt 
to guide the user to the next step in creating their journey. 

Current journey: {json.dumps(journey_json, indent=2)}
User's last message: {user_message}

Generate a helpful prompt that:
1. Summarizes what has been done so far
2. Lists the EXACT available screen components by name and asks the user to choose from ONLY these options
3. If there are journey completion requirements, include the message about what's needed to complete the journey
4. Explains how to confirm, change or cancel
5. If the user request is ambiguous (like "add 3 screens" without specifying what screens), add empty but structured screens objects with empty values and direct the user to put in values for each field politely.


IMPORTANT: DO NOT mention any components or options not in the available screen components list.
If the user tries to navigate to a non-existent screen, politely explain that they can only create navigation 
between screens that already exist in the journey.
"""
                next_prompt = get_gemini_response(next_prompt_prompt)
                
                # Add journey status message if not already included
                if journey_status_message and journey_status_message not in next_prompt:
                    next_prompt = f"{next_prompt}{journey_status_message}"
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Gemini response: {response_text}")
                next_prompt = "I'm having trouble understanding that. Could you please clarify your requirements for the journey?"
                # Do not update journey on error
        
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

# API endpoint to get field components (simplified)
@app.route('/journey/api/field-components/<screen_component_name>', methods=['GET'])
def get_field_components(screen_component_name):
    """API endpoint to get field components for a specific screen component"""
    field_components = fetch_field_components(screen_component_name)
    return jsonify(field_components)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)