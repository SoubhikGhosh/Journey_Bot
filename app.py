from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import uuid
import logging
import json
import re
import requests
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

# Secondary backend API URL (configure as needed)
SECONDARY_BACKEND_URL = "http://secondary-backend-service:8080"

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

# Function to fetch all screen components with their field components from secondary backend
def fetch_all_components():
    """Fetch all screen components and their field components from secondary backend"""
    # For development/testing: using hardcoded data instead of API call
    # In production, uncomment the API call below
    
    # try:
    #     response = requests.get(f"{SECONDARY_BACKEND_URL}/fetchAll")
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         logger.error(f"Failed to fetch components from secondary backend. Status code: {response.status_code}")
    #         return []
    # except Exception as e:
    #     logger.error(f"Error fetching components from secondary backend: {str(e)}")
    #     return []
    
    # Hardcoded component data for development
    return [
        {
            "screenComponentId": 1,
            "screenComponentName": "aadhar",
            "style": "defaultScreenComponentStyle",
            "fieldComponents": [
                {
                    "fieldComponentId": 1,
                    "fieldType": "drop_down",
                    "fieldName": "country",
                    "fieldLabel": "Country",
                    "validations": {},
                    "dataSource": "get_countries",
                    "dependencies": None,
                    "isTriggerComponent": True,
                    "themeStyle": {
                        "styleId": 2,
                        "styleName": "defaultFieldStyle",
                        "styleConfig": {
                            "padding": "12.0",
                            "borderRadius": "4.0",
                            "borderColor": "#CCCCCC",
                            "backgroundColor": "#FFFFFF",
                            "fontSize": "14",
                            "textColor": "#000000"
                        },
                        "theme": {
                            "themeId": 1,
                            "themeName": "lightTheme",
                            "primaryColor": "#f8f8f8",
                            "accentColor": "#0000FF",
                            "textstyle": {
                                "fontSize": 14,
                                "fontFamily": "Roboto",
                                "color": "#123456"
                            },
                            "createdAt": None,
                            "updatedAt": None
                        }
                    },
                    "createdAt": "2025-02-26T15:40:43.556707",
                    "updatedAt": "2025-02-26T15:40:43.524369"
                },
                {
                    "fieldComponentId": 2,
                    "fieldType": "button",
                    "fieldName": "aadharSubmitBtn",
                    "fieldLabel": "Submit Aadhar",
                    "validations": {},
                    "dataSource": None,
                    "dependencies": None,
                    "isTriggerComponent": True,
                    "themeStyle": {
                        "styleId": 2,
                        "styleName": "defaultFieldStyle"
                    },
                    "createdAt": "2025-02-26T15:40:43.556707",
                    "updatedAt": "2025-02-26T15:40:43.524369"
                }
            ],
            "createdAt": "2025-02-26T15:40:50.960744",
            "updatedAt": "2025-02-26T15:40:50.960748"
        },
        {
            "screenComponentId": 2,
            "screenComponentName": "pan",
            "style": "defaultScreenComponentStyle",
            "fieldComponents": [
                {
                    "fieldComponentId": 3,
                    "fieldType": "drop_down",
                    "fieldName": "country",
                    "fieldLabel": "Country",
                    "validations": {},
                    "dataSource": "get_countries",
                    "dependencies": None,
                    "isTriggerComponent": False,
                    "themeStyle": {
                        "styleId": 2,
                        "styleName": "defaultFieldStyle",
                        "styleConfig": {
                            "padding": "12.0",
                            "borderRadius": "4.0",
                            "borderColor": "#CCCCCC",
                            "backgroundColor": "#FFFFFF",
                            "fontSize": "14",
                            "textColor": "#000000"
                        },
                        "theme": {
                            "themeId": 1,
                            "themeName": "lightTheme",
                            "primaryColor": "#f8f8f8",
                            "accentColor": "#0000FF",
                            "textstyle": {
                                "fontSize": 14,
                                "fontFamily": "Roboto",
                                "color": "#123456"
                            },
                            "createdAt": None,
                            "updatedAt": None
                        }
                    },
                    "createdAt": "2025-02-26T15:40:43.556707",
                    "updatedAt": "2025-02-26T15:40:43.524369"
                },
                {
                    "fieldComponentId": 4,
                    "fieldType": "button",
                    "fieldName": "panSubmitBtn",
                    "fieldLabel": "Submit PAN",
                    "validations": {},
                    "dataSource": None,
                    "dependencies": None,
                    "isTriggerComponent": True,
                    "themeStyle": {
                        "styleId": 2,
                        "styleName": "defaultFieldStyle"
                    },
                    "createdAt": "2025-02-26T15:40:43.556707",
                    "updatedAt": "2025-02-26T15:40:43.524369"
                },
                {
                    "fieldComponentId": 5,
                    "fieldType": "button",
                    "fieldName": "verifyPanBtn", 
                    "fieldLabel": "Verify PAN",
                    "validations": {},
                    "dataSource": None,
                    "dependencies": None,
                    "isTriggerComponent": True,
                    "themeStyle": {
                        "styleId": 2,
                        "styleName": "defaultFieldStyle"
                    },
                    "createdAt": "2025-02-26T15:40:43.556707",
                    "updatedAt": "2025-02-26T15:40:43.524369"
                }
            ],
            "createdAt": "2025-02-26T15:40:50.960744",
            "updatedAt": "2025-02-26T15:40:50.960748"
        }
    ]

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

# Function to find valid trigger components in a screen
def find_trigger_components(screen):
    """Find all valid trigger components (isTriggerComponent=True) in a screen"""
    trigger_components = []
    if not screen:
        return trigger_components
        
    for sc in screen.get("screen_components", []):
        for fc in sc.get("field_components", []):
            if fc.get("isTriggerComponent") is True:
                trigger_components.append({
                    "id": fc.get("fieldComponentId"),
                    "name": fc.get("fieldName", "Unknown"),
                    "label": fc.get("fieldLabel", ""),
                    "type": fc.get("fieldType", "Unknown")
                })
    
    return trigger_components

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
    
    # Fetch all components in a single API call
    all_components = fetch_all_components()
    
    # Initialize session with components info
    sessions[session_id] = {
        "journey": {
            "journey_name": "",
            "journey_type": "single",
            "no_screens": 0,
            "screens": [],
            "navigation": []
        },
        "all_components": all_components
    }
    
    # Create welcome message with available components
    component_names = ", ".join([comp.get("screenComponentName", "") for comp in all_components])
    
    next_prompt = (f"Hi! I'll help you create a journey for your banking application. "
                  f"What would you like to name this journey? "
                  f"Please tell me what type of journey you want to create (e.g., Savings Account Opening, Loan Application). "
                  f"You can use these components: {component_names}")
    
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
    all_components = session_data["all_components"]
    
    # Track special cases for UI feedback
    navigation_added = False
    auto_selected_trigger = None
    no_triggers_found = False
    
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
            component_names = ", ".join([comp.get("screenComponentName", "") for comp in all_components])
            next_prompt = ("I need more specific information. Please provide details about what kind of screens "
                          "you'd like to add, their names, and their components. You can choose from these components: " + 
                          component_names)
            return jsonify({
                "journey_json": current_journey,
                "next_prompt": next_prompt,
                "final": False,
                "needs_trigger_selection": any("trigger_component_id" not in nav for nav in current_journey.get("navigation", []))
            })
            
        # Process trigger component selections if any
        screen_names_map = {screen["screen_name"].lower(): screen["screen_id"] for screen in current_journey.get("screens", []) if "screen_name" in screen}
        trigger_selections = extract_trigger_selection(user_message, screen_names_map)
        
        # Apply trigger selections to navigation - but only apply to valid trigger components
        if trigger_selections:
            for nav in current_journey.get("navigation", []):
                if "source_screen_id" in nav and "trigger_component_id" not in nav:
                    source_id = nav["source_screen_id"]
                    if source_id in trigger_selections:
                        # Verify the selected trigger ID actually exists and is a trigger component
                        selected_id = trigger_selections[source_id]
                        source_screen = next((s for s in current_journey.get("screens", []) if s.get("screen_id") == source_id), None)
                        if source_screen:
                            # Find if the selected ID is a valid trigger component
                            is_valid_trigger = False
                            for sc in source_screen.get("screen_components", []):
                                for fc in sc.get("field_components", []):
                                    if fc.get("fieldComponentId") == selected_id and fc.get("isTriggerComponent") is True:
                                        is_valid_trigger = True
                                        nav["trigger_component_id"] = selected_id
                                        break
        
        # Process with Gemini
        try:
            # Check if user is trying to create navigation between screens
            nav_patterns = [
                r"(?:go|navigate|move|proceed)\s+from\s+(?:screen\s*)?(\w+)\s+to\s+(?:screen\s*)?(\w+)",
                r"(?:connect|link)\s+(?:screen\s*)?(\w+)\s+(?:to|and|with)\s+(?:screen\s*)?(\w+)",
                r"(?:create|add|make)\s+(?:a\s+)?(?:navigation|link|connection)\s+(?:from\s+)?(?:screen\s*)?(\w+)\s+to\s+(?:screen\s*)?(\w+)"
            ]
            
            for pattern in nav_patterns:
                matches = re.search(pattern, user_message.lower())
                if matches:
                    source = matches.group(1)
                    target = matches.group(2)
                    
                    # Try to identify screens by name or ID
                    source_screen = None
                    target_screen = None
                    
                    # Check if source/target are numbers (screen IDs) or names
                    try:
                        source_id = int(source)
                        source_screen = next((s for s in current_journey.get("screens", []) if s.get("screen_id") == source_id), None)
                    except ValueError:
                        # Try to match by name (case insensitive)
                        source_screen = next((s for s in current_journey.get("screens", []) if s.get("screen_name", "").lower() == source.lower()), None)
                    
                    try:
                        target_id = int(target)
                        target_screen = next((s for s in current_journey.get("screens", []) if s.get("screen_id") == target_id), None)
                    except ValueError:
                        # Try to match by name (case insensitive)
                        target_screen = next((s for s in current_journey.get("screens", []) if s.get("screen_name", "").lower() == target.lower()), None)
                    
                    if source_screen and target_screen:
                        # Add navigation entry if both screens exist and navigation doesn't already exist
                        source_id = source_screen.get("screen_id")
                        target_id = target_screen.get("screen_id")
                        
                        # Check if this navigation already exists
                        nav_exists = any(
                            nav.get("source_screen_id") == source_id and 
                            nav.get("target_screen_id") == target_id 
                            for nav in current_journey.get("navigation", [])
                        )
                        
                        if not nav_exists:
                            navigation_request = {
                                "source_screen_id": source_id,
                                "target_screen_id": target_id,
                                "navigation_type": "button_click"
                            }
                            
                            # Find trigger components in source screen
                            trigger_components = find_trigger_components(source_screen)
                            
                            # If only one trigger component exists, use it automatically
                            if len(trigger_components) == 1:
                                navigation_request["trigger_component_id"] = trigger_components[0]["id"]
                                # Make a note to inform the user about automatic selection
                                auto_selected_trigger = {
                                    "source_screen_id": source_id,
                                    "source_screen_name": source_screen.get("screen_name", f"Screen {source_id}"),
                                    "trigger_id": trigger_components[0]["id"],
                                    "trigger_name": trigger_components[0].get("label") or trigger_components[0].get("name")
                                }
                            elif len(trigger_components) == 0:
                                # Make a note that no trigger components were found
                                no_triggers_found = True
                            
                            # Add the navigation
                            if "navigation" not in current_journey:
                                current_journey["navigation"] = []
                            
                            current_journey["navigation"].append(navigation_request)
                            navigation_added = True
                    
                    break
            
            # Format available screen components
            screen_components_info = "\n".join([
                f"- Name: {sc.get('screenComponentName', '')}, ID: {sc.get('screenComponentId', '')}" 
                for sc in all_components
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
                
                # Check if it's asking for trigger component selection
                needs_trigger = any("trigger_component_id" not in nav for nav in current_journey.get("navigation", []))
                if needs_trigger and ("trigger" in response_text.lower() or "navigation" in response_text.lower()):
                    # Find missing trigger components and offer user-friendly options
                    trigger_options = []
                    no_trigger_screens = []
                    auto_selected_screens = []
                    
                    for nav in current_journey.get("navigation", []):
                        if "source_screen_id" in nav and "trigger_component_id" not in nav:
                            source_id = nav["source_screen_id"]
                            source_screen = next((s for s in current_journey.get("screens", []) if s.get("screen_id") == source_id), None)
                            
                            if source_screen:
                                screen_name = source_screen.get("screen_name", f"Screen {source_id}")
                                # Find ONLY trigger components in this screen (isTriggerComponent: true)
                                trigger_components = find_trigger_components(source_screen)
                            
                                # If only one trigger component, select it automatically
                                if len(trigger_components) == 1:
                                    nav["trigger_component_id"] = trigger_components[0]["id"]
                                    auto_selected_screens.append({
                                        "screen_name": screen_name,
                                        "trigger_name": trigger_components[0].get("label") or trigger_components[0].get("name"),
                                        "trigger_id": trigger_components[0]["id"]
                                    })
                                elif len(trigger_components) > 1:
                                    # Multiple options - let user choose
                                    options = ", ".join([f"{t['name']} (ID: {t['id']})" for t in trigger_components])
                                    trigger_options.append(f"For {screen_name}: {options}")
                                else:
                                    no_trigger_screens.append(screen_name)
                    
                    # Build user-friendly response
                    if auto_selected_screens:
                        auto_msg = "I've automatically selected trigger components for screens with only one option:\n" + \
                                "\n".join([f"• {s['screen_name']}: '{s['trigger_name']}' (ID: {s['trigger_id']})" for s in auto_selected_screens])
                        trigger_options.insert(0, auto_msg)
                    
                    if no_trigger_screens:
                        no_trigger_msg = "The following screens have no trigger components (buttons, etc.): " + ", ".join(no_trigger_screens) + ". " + \
                                    "You need to add at least one component with 'isTriggerComponent: true' to each source screen."
                        trigger_options.append(no_trigger_msg)
                    
                    if trigger_options:
                        if all("trigger_component_id" in nav for nav in current_journey.get("navigation", [])):
                            next_prompt = "Great! All your navigations now have trigger components assigned. You can continue building your journey or type 'confirm' when ready."
                        else:
                            next_prompt = "To set up navigation between screens, please select a trigger component.\n\n" + \
                                        "Available trigger components:\n" + "\n".join(trigger_options)
                            
                            if any(("For " in opt and ":" in opt) for opt in trigger_options):
                                next_prompt += "\n\nFor screens with multiple options, you can select one by saying 'use trigger component ID X for screen Y'."
                    else:
                        next_prompt = "I need to know which component should trigger the navigation. However, I couldn't find any trigger components in your source screens. Please add components with isTriggerComponent set to true."
                
                # Return early without updating the journey
                return jsonify({
                    "journey_json": current_journey,
                    "next_prompt": next_prompt,
                    "final": False,
                    "needs_trigger_selection": needs_trigger
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
                        
                        # Find matching component from the fetched components
                        component_name = sc.get("screen_component_name")
                        if component_name and (not sc.get("field_components") or len(sc.get("field_components")) == 0):
                            # Find the complete component details from all_components
                            matching_component = next(
                                (comp for comp in all_components if comp.get("screenComponentName") == component_name), 
                                None
                            )
                            if matching_component:
                                sc["field_components"] = matching_component.get("fieldComponents", [])
                
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
                component_names = ", ".join([comp.get("screenComponentName", "") for comp in all_components])
                
                next_prompt_prompt = f"""
Based on the current journey JSON and the user's last message, generate a friendly, non-technical prompt 
to guide the user to the next step in creating their journey. 

Current journey: {json.dumps(journey_json, indent=2)}
User's last message: {user_message}
Available screen components: {component_names}

Generate a helpful prompt that:
1. Summarizes what has been done so far
2. Lists the EXACT available screen components by name and asks the user to choose from ONLY these options: {component_names}
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
                
                # Add custom notifications for navigation-related messages
                if navigation_added:
                    if auto_selected_trigger:
                        next_prompt = f"I've added navigation between the screens. Since there is only one trigger component in {auto_selected_trigger['source_screen_name']}, I automatically selected '{auto_selected_trigger['trigger_name']}' (ID: {auto_selected_trigger['trigger_id']}) as the trigger component.\n\n{next_prompt}"
                    elif no_triggers_found:
                        next_prompt = "I've added the navigation connection, but couldn't find any trigger components in the source screen. Please add a button or other component with 'isTriggerComponent' set to true to complete the navigation setup.\n\n" + next_prompt
                
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)