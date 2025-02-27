import json
import os
import uuid
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure Gemini API
API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyD2ArK74wBtL1ufYmpyrV2LqaOBrSi3mlU')
genai.configure(api_key=API_KEY)

# Gemini model configuration
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

# Mock data for screen components
def get_mock_screen_components():
    return [
        {"id": 1, "name": "CustomerDetails"},
        {"id": 2, "name": "AccountDetails"},
        {"id": 3, "name": "PAN"},
        {"id": 4, "name": "IdentityVerification"},
        {"id": 5, "name": "AddressProof"},
        {"id": 6, "name": "TermsAndConditions"},
        {"id": 7, "name": "AccountSummary"},
        {"id": 8, "name": "DocumentUpload"},
        {"id": 9, "name": "OTP"},
        {"id": 10, "name": "Calendar"}
    ]

# Mock data for field components based on screen component ID
def get_mock_field_components(screen_component_id):
    timestamp = datetime.now().isoformat()
    components = {
        1: [  # CustomerDetails
            {
                "fieldComponentId": 1, "fieldType": "largetext", "fieldName": "customerDetailsHeading",
                "fieldLabel": "Enter Customer Details", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 28, "fieldType": "text_field", "fieldName": "firstname",
                "fieldLabel": "First Name", 
                "validations": {
                    "required": True, "requiredMessage": "First Name is required",
                    "minLength": 3, "minLengthMessage": "Firstname must be at least 3 characters",
                    "helperText": "Enter a Firstname between 3-20 characters"
                },
                "dataSource": None, "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 10, "fieldType": "button", "fieldName": "customDtlBtn",
                "fieldLabel": "Proceed >", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": True,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            }
        ],
        2: [  # AccountDetails
            {
                "fieldComponentId": 20, "fieldType": "largetext", "fieldName": "accountDetailsHeading",
                "fieldLabel": "Enter Account Details", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 21, "fieldType": "text_field", "fieldName": "accountNumber",
                "fieldLabel": "Account Number", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 22, "fieldType": "button", "fieldName": "accountDtlBtn",
                "fieldLabel": "Proceed >", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": True,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            }
        ],
        3: [  # PAN
            {
                "fieldComponentId": 11, "fieldType": "largetext", "fieldName": "panDetailsHeading",
                "fieldLabel": "Enter PAN Details", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 12, "fieldType": "text_field", "fieldName": "pan",
                "fieldLabel": "PAN", 
                "validations": {
                    "required": True, "pattern": "[A-Z]{5}[0-9]{4}[A-Z]",
                    "patternError": "Please enter a valid PAN number"
                },
                "dataSource": None, "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 13, "fieldType": "button", "fieldName": "validatePanBtn",
                "fieldLabel": "Validate PAN", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": True,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            }
        ],
        5: [  # AddressProof
            {
                "fieldComponentId": 30, "fieldType": "largetext", "fieldName": "addressProofHeading",
                "fieldLabel": "Enter Address Proof Details", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 31, "fieldType": "text_field", "fieldName": "addressLine1",
                "fieldLabel": "Address Line 1", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 32, "fieldType": "button", "fieldName": "addressProofBtn",
                "fieldLabel": "Proceed >", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": True,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            }
        ],
        9: [  # OTP
            {
                "fieldComponentId": 40, "fieldType": "largetext", "fieldName": "otpHeading",
                "fieldLabel": "Enter OTP", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 41, "fieldType": "text_field", "fieldName": "otp",
                "fieldLabel": "OTP", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 42, "fieldType": "button", "fieldName": "otpBtn",
                "fieldLabel": "Verify OTP", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": True,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            }
        ],
        10: [  # Calendar
            {
                "fieldComponentId": 50, "fieldType": "largetext", "fieldName": "calendarHeading",
                "fieldLabel": "Select Date", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 51, "fieldType": "date", "fieldName": "selectedDate",
                "fieldLabel": "Date", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": False,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            },
            {
                "fieldComponentId": 52, "fieldType": "button", "fieldName": "calendarBtn",
                "fieldLabel": "Confirm Date", "validations": {}, "dataSource": None,
                "dependencies": None, "isTriggerComponent": True,
                "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
            }
        ]
    }
    
    # Default fields for any component not specifically defined
    default_fields = [
        {
            "fieldComponentId": 99, "fieldType": "largetext", "fieldName": "defaultHeading",
            "fieldLabel": "Default Heading", "validations": {}, "dataSource": None,
            "dependencies": None, "isTriggerComponent": False,
            "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
        },
        {
            "fieldComponentId": 100, "fieldType": "button", "fieldName": "defaultButton",
            "fieldLabel": "Continue", "validations": {}, "dataSource": None,
            "dependencies": None, "isTriggerComponent": True,
            "createdAt": timestamp, "updatedAt": timestamp, "style": "defaultFieldStyle"
        }
    ]
    
    return components.get(screen_component_id, default_fields)

# Initialize a journey structure
def init_journey():
    return {
        "journey_name": "",
        "journey_type": "single",
        "no_screens": 0,
        "screens": [],
        "navigation": []
    }

# Gemini system prompt
SYSTEM_PROMPT = """
You are an AI assistant helping users build a journey configuration for a financial application.

AVAILABLE SCREEN COMPONENTS:
Only use these exact component names - users cannot create custom components:
1. CustomerDetails - For capturing personal details
2. AccountDetails - For capturing account information
3. PAN - For PAN card validation
4. IdentityVerification - For KYC checks
5. AddressProof - For address verification
6. TermsAndConditions - For legal acceptance
7. AccountSummary - For showing account overview
8. DocumentUpload - For uploading required documents
9. OTP - For verification codes
10. Calendar - For date selection

YOUR MAIN TASK is to generate a complete JSON for the journey configuration based on user inputs.

REQUIRED JOURNEY STRUCTURE:
- journey_name: Name of the journey (e.g., "SavingAccountJourney")
- journey_type: Always "single"
- no_screens: Number of screens in the journey
- screens: Array of screen objects
- navigation: Array of navigation rules between screens

FOR EACH SCREEN:
1. Each screen needs a screen_id (starts from 1)
2. Each screen needs a screen_name (e.g., "screenhello", "screenworld")
3. Each screen must have "template": "defaultTemplate" and "style": "defaultScreenStyle"
4. Each screen must have screen_components array with component objects

FOR SCREEN COMPONENTS:
1. Each component must have screen_component_id matching its ID from the available components
2. Each component must have screen_component_name matching its name
3. Each component must have screen_component_style: "defaultScreenComponentStyle"
4. Each component must have field_components array with the appropriate fields

FOR NAVIGATION:
1. For n screens, we need at least one navigation rule
2. Each navigation needs source_screen_id and target_screen_id
3. We'll use button clicks for navigation with "navigation_type": "button_click"
4. Each navigation will use a trigger_component_id from the source screen's field components

IMPORTANT RULES:
1. Always provide the full, updated journey JSON in your response using the format JSON_OUTPUT: {...}
2. DO NOT show the JSON to the user in your conversational response
3. If the user mentions a component not in the list above, ONLY suggest components from the predefined list
4. Guide the user step by step through the journey building process
5. When finalizing, create a flow diagram using Mermaid syntax with the format FLOW_DIAGRAM: ```mermaid...```

USER INTERACTION:
1. Always list the available components when asking for screen components
2. Enforce that users can only select from the predefined component list
3. Be conversational and helpful, explaining each step clearly
4. When confirming the journey, present a clear summary of screens and navigation

RESPONSE FORMAT:
Every response must include:
1. A conversational response to the user (without JSON)
2. Hidden from user: JSON_OUTPUT: <complete journey JSON>
3. If finalizing, include: FLOW_DIAGRAM: ```mermaid...```
"""

# Route for health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Route to start a new conversation
@app.route('/start', methods=['POST'])
def start_conversation():
    # Generate a new session ID
    session_id = str(uuid.uuid4())
    
    # Create session data in app context
    if not hasattr(app, 'session_data'):
        app.session_data = {}
    
    # Initialize journey in session data
    app.session_data[session_id] = {
        'journey': init_journey(),
        'conversation_state': 'initial',
        'chat_history': []
    }
    
    # Get component options
    component_options = ", ".join([f"{comp['id']}. {comp['name']}" for comp in get_mock_screen_components()])
    
    # Initial prompt
    initial_prompt = f"""
    I'll help you build a journey configuration for your financial application.
    
    You can choose from these screen components:
    {component_options}
    
    Let's start by defining the basic details:
    
    1. What would you like to name this journey? (e.g., SavingAccountJourney)
    2. How many screens would you like in this journey?
    
    Once we have these details, I'll guide you through setting up each screen.
    """
    
    # Store system prompt and initial messages
    app.session_data[session_id]['chat_history'] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Help me build a journey configuration."},
        {"role": "assistant", "content": initial_prompt}
    ]
    
    return jsonify({
        "session_id": session_id,
        "message": initial_prompt
    }), 200

# Validate journey completeness before finalization
def validate_journey_completeness(journey):
    errors = []
    
    # Check journey name
    if not journey.get("journey_name"):
        errors.append("Journey name is not set")
    
    # Check number of screens
    no_screens = journey.get("no_screens", 0)
    if no_screens <= 0:
        errors.append("Number of screens must be greater than 0")
    
    # Check screens
    actual_screens = journey.get("screens", [])
    if len(actual_screens) != no_screens:
        errors.append(f"Expected {no_screens} screens but found {len(actual_screens)}")
    
    # Check screen components
    for i, screen in enumerate(actual_screens):
        if not screen.get("screen_components"):
            errors.append(f"Screen {i+1} ({screen.get('screen_name', 'unnamed')}) has no components")
    
    # Check navigation
    if no_screens > 1:
        expected_navigations = 1  # Changed to require at least 1 navigation
        actual_navigations = len(journey.get("navigation", []))
        if actual_navigations < expected_navigations:
            errors.append(f"Expected at least {expected_navigations} navigation but found {actual_navigations}")
    
    return errors

# Handle finalization check
def should_finalize(user_message):
    finalize_keywords = ['finalize', 'complete', 'done', 'finish', 'confirm']
    return any(keyword in user_message.lower() for keyword in finalize_keywords)

# Extract JSON from Gemini's response
def extract_json_from_response(response_text):
    json_start = response_text.find('JSON_OUTPUT:')
    
    if json_start == -1:
        # Try alternative formats
        json_start = response_text.find('```json')
        if json_start != -1:
            json_start += 7  # Move past ```json
            json_end = response_text.find('```', json_start)
            if json_end != -1:
                json_str = response_text[json_start:json_end].strip()
                try:
                    return json.loads(json_str)
                except:
                    return None
        return None
    
    json_text = response_text[json_start + len('JSON_OUTPUT:'):].strip()
    
    # Handle the case where JSON might be enclosed in triple backticks
    if json_text.startswith('```'):
        json_text = json_text[3:]
        end_marker = json_text.find('```')
        if end_marker != -1:
            json_text = json_text[:end_marker]
    
    # Find the actual JSON object
    try:
        # First try to parse the whole remaining text
        return json.loads(json_text)
    except:
        # If that fails, try to extract just the JSON part
        try:
            # Look for opening brace
            brace_start = json_text.find('{')
            if brace_start == -1:
                return None
            
            # Count opening and closing braces to find the end of the JSON object
            count = 0
            for i, char in enumerate(json_text[brace_start:]):
                if char == '{':
                    count += 1
                elif char == '}':
                    count -= 1
                    if count == 0:
                        # Found the end of the JSON object
                        json_str = json_text[brace_start:brace_start+i+1]
                        return json.loads(json_str)
            
            return None
        except:
            return None

# Extract flow diagram from Gemini's response
def extract_flow_diagram(response_text):
    flow_start = response_text.find('FLOW_DIAGRAM:')
    
    if flow_start == -1:
        return None
    
    flow_text = response_text[flow_start + len('FLOW_DIAGRAM:'):].strip()
    
    # Handle the case where diagram is enclosed in triple backticks
    if flow_text.startswith('```mermaid'):
        flow_text = flow_text[len('```mermaid'):].strip()
        end_marker = flow_text.find('```')
        if end_marker != -1:
            flow_text = flow_text[:end_marker].strip()
            return flow_text
    
    return None

# Create a complete journey object with field components
def complete_journey_with_field_components(journey):
    updated_journey = json.loads(json.dumps(journey))  # Deep copy
    
    # Check each screen and its components
    for screen in updated_journey.get("screens", []):
        screen_components = screen.get("screen_components", [])
        
        # Ensure screen_components is a list of objects
        if isinstance(screen_components, list):
            new_components = []
            
            for component in screen_components:
                # If component is just a string, convert to proper object structure
                if isinstance(component, str):
                    # Find component ID
                    component_id = None
                    for comp in get_mock_screen_components():
                        if comp["name"].lower() == component.lower():
                            component_id = comp["id"]
                            break
                    
                    if component_id:
                        # Get field components
                        field_components = get_mock_field_components(component_id)
                        
                        # Create proper component object
                        new_components.append({
                            "screen_component_id": component_id,
                            "screen_component_name": component,
                            "screen_component_style": "defaultScreenComponentStyle",
                            "field_components": field_components
                        })
                # If already an object but missing field_components
                elif isinstance(component, dict) and not component.get("field_components"):
                    component_id = component.get("screen_component_id")
                    if component_id:
                        # Get field components
                        field_components = get_mock_field_components(component_id)
                        component["field_components"] = field_components
                        new_components.append(component)
                else:
                    new_components.append(component)
            
            # Replace the screen components with the updated ones
            screen["screen_components"] = new_components
    
    # Check navigation for any missing trigger_component_id
    for nav in updated_journey.get("navigation", []):
        if not nav.get("trigger_component_id"):
            # Find source screen
            source_screen = next((s for s in updated_journey.get("screens", []) if s.get("screen_id") == nav.get("source_screen_id")), None)
            if source_screen:
                # Find a trigger component in the source screen
                for component in source_screen.get("screen_components", []):
                    for field in component.get("field_components", []):
                        if field.get("fieldType") == "button":
                            nav["trigger_component_id"] = field.get("fieldComponentId")
                            break
                    if nav.get("trigger_component_id"):
                        break
    
    return updated_journey

# Determine conversation state based on journey completeness
def determine_conversation_state(journey):
    # Check journey basics
    if not journey.get("journey_name") or not journey.get("no_screens"):
        return "initial"
    
    # Check screens
    if len(journey.get("screens", [])) < journey.get("no_screens", 0):
        return "defining_screens"
    
    # Check if all screens have components
    for screen in journey.get("screens", []):
        if not screen.get("screen_components"):
            return "defining_screens"
    
    # Check navigation
    if journey.get("no_screens", 0) > 1:
        if len(journey.get("navigation", [])) < 1:
            return "defining_navigation"
    
    return "complete"

# Main process endpoint
@app.route('/process', methods=['POST'])
def process_message():
    # Get data from request
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message', '')
    
    # Validate session exists
    if not session_id or not hasattr(app, 'session_data') or session_id not in app.session_data:
        return jsonify({"error": "Invalid or expired session ID. Please start a new conversation."}), 400
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get session data
    session_data = app.session_data[session_id]
    journey = session_data.get('journey', init_journey())
    
    # Add user message to chat history
    session_data['chat_history'].append({"role": "user", "content": user_message})
    
    # Check for finalization request
    finalizing = should_finalize(user_message)
    
    # Format the current journey context for Gemini
    component_details = "\n".join([f"{comp['id']}. {comp['name']}" for comp in get_mock_screen_components()])
    journey_context = f"""
    Current journey configuration:
    {json.dumps(journey, indent=2)}
    
    Available screen components:
    {component_details}
    
    Remember to generate a complete, updated journey JSON in your response using the format:
    JSON_OUTPUT: {{...}}
    
    DO NOT show the JSON to the user in your conversational response.
    
    If this appears to be a finalization request, please also include a flow diagram using Mermaid syntax:
    FLOW_DIAGRAM: ```mermaid
    flowchart TD
    ...
    ```
    """
    
    try:
        # Format history for Gemini
        prompt = SYSTEM_PROMPT + "\n\n"
        
        # Add conversation history (excluding system messages since already added)
        for msg in session_data['chat_history'][-5:]:  # Only use last 5 messages to keep context manageable
            if msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        
        # Add current context and prepare for assistant response
        prompt += f"Current journey context:\n{journey_context}\n\nUser: {user_message}\n\nAssistant: "
        
        logger.info(f"Sending prompt to Gemini of length {len(prompt)}")
        
        gemini_response = model.generate_content(prompt)
        ai_response = gemini_response.text
        
        # Extract JSON from Gemini's response
        extracted_journey = extract_json_from_response(ai_response)
        
        # Extract flow diagram if finalizing
        flow_diagram = None
        if finalizing:
            flow_diagram = extract_flow_diagram(ai_response)
        
        if extracted_journey:
            # Complete the journey with field components
            completed_journey = complete_journey_with_field_components(extracted_journey)
            
            # Update session with new journey
            session_data['journey'] = completed_journey
            
            # Clean the AI response by removing the JSON and flow diagram parts
            cleaned_response = ai_response
            
            json_start = ai_response.find('JSON_OUTPUT:')
            if json_start != -1:
                cleaned_response = ai_response[:json_start].strip()
            
            flow_start = cleaned_response.find('FLOW_DIAGRAM:')
            if flow_start != -1:
                cleaned_response = cleaned_response[:flow_start].strip()
        else:
            # If no JSON was extracted, keep the original journey
            completed_journey = journey
            cleaned_response = ai_response
            
            # Still clean any FLOW_DIAGRAM part
            flow_start = cleaned_response.find('FLOW_DIAGRAM:')
            if flow_start != -1:
                cleaned_response = cleaned_response[:flow_start].strip()
        
        # Add AI response to chat history
        session_data['chat_history'].append({"role": "assistant", "content": cleaned_response})
        
        # Check if we should finalize
        if finalizing:
            validation_errors = validate_journey_completeness(completed_journey)
            if validation_errors:
                error_message = "Cannot finalize the journey due to the following issues:\n- " + "\n- ".join(validation_errors)
                return jsonify({
                    "message": error_message,
                    "journey_state": determine_conversation_state(completed_journey),
                    "session_id": session_id,
                    "journey_json": completed_journey
                }), 200
            else:
                # If we have a flow diagram, include it in the response
                if flow_diagram:
                    finalize_message = f"Journey '{completed_journey.get('journey_name', 'Unnamed')}' has been finalized.\n\nHere's a visualization of your journey flow:"
                    return jsonify({
                        "message": finalize_message,
                        "journey_state": "complete",
                        "session_id": session_id,
                        "journey_json": completed_journey,
                        "flow_diagram": flow_diagram
                    }), 200
                else:
                    # Journey is complete but no flow diagram
                    return jsonify({
                        "message": f"Journey '{completed_journey.get('journey_name', 'Unnamed')}' has been finalized.",
                        "journey_state": "complete",
                        "session_id": session_id,
                        "journey_json": completed_journey
                    }), 200
        
        # Regular response during journey building
        return jsonify({
            "message": cleaned_response,
            "journey_state": determine_conversation_state(completed_journey),
            "session_id": session_id,
            "journey_json": completed_journey  # Always include journey JSON in the response
        }), 200
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            "error": f"Failed to process message: {str(e)}",
            "journey_state": determine_conversation_state(journey),
            "session_id": session_id,
            "journey_json": journey  # Include journey JSON even on error
        }), 500

# Main entry point
def main():
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting Journey Builder Chatbot on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()