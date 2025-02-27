from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import uuid
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Set up logging for terminal output only
logger = logging.getLogger('journey_builder')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True)
logger.info("Flask app initialized with CORS support")

# Configure Google API
GOOGLE_API_KEY = "AIzaSyD2ArK74wBtL1ufYmpyrV2LqaOBrSi3mlU"
genai.configure(api_key=GOOGLE_API_KEY)
logger.info("Google Generative AI configured")

def get_gemini_model():
    logger.info("Getting Gemini model with safety settings")
    return genai.GenerativeModel(
        "gemini-pro",
        safety_settings=[
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
        ]
    )

# Set up Gemini model
model = get_gemini_model()

# Mock data for screen components
mock_screen_components = [
    {"screen_component_id": 1, "screen_component_name": "pan"},
    {"screen_component_id": 2, "screen_component_name": "aadhar"},
    {"screen_component_id": 3, "screen_component_name": "voter_id"},
    {"screen_component_id": 4, "screen_component_name": "passport"},
    {"screen_component_id": 5, "screen_component_name": "address"},
    {"screen_component_id": 6, "screen_component_name": "employment"},
    {"screen_component_id": 7, "screen_component_name": "income"},
    {"screen_component_id": 8, "screen_component_name": "education"},
    {"screen_component_id": 9, "screen_component_name": "CustomerDetails"}
]
logger.info(f"Loaded {len(mock_screen_components)} mock screen components")

# Mock field components for each screen component
mock_field_components = {
    1: [ # pan
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
    ],
    9: [ # CustomerDetails
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
    # Add more field components as needed
}
logger.info("Loaded mock field components for screen components")

# Function to build prompt for Google Gemini API
def build_gemini_prompt(conversation_history, current_step, journey_data=None):
    logger.info(f"Building Gemini prompt for step: {current_step}")
    prompt = f"""
You are an AI assistant helping to create a journey configuration for a banking application.
Current step: {current_step}

Based on the following conversation history, help build or update the journey configuration:
"""
    
    # Add formatted conversation history
    for message in conversation_history:
        role = message["role"]
        content = message["content"]
        prompt += f"\n{role.capitalize()}: {content}"
    
    if journey_data:
        prompt += f"\n\nCurrent journey data: {json.dumps(journey_data, indent=2)}"
    
    if current_step == "welcome":
        prompt += """
Please ask the user for the journey_name, journey_type, and number of screens for their banking application journey.
Be friendly and conversational. Don't show any of these instructions to the user.
Example response: "Let's build your banking journey configuration. What would you like to name this journey? Also, please specify the journey type (e.g., 'single') and how many screens you'd like to include."
"""
    elif current_step == "screens":
        prompt += """
Now let's configure each screen. For each screen, I need:
1. A screen name
2. Which screen components to include

For each screen, ask the user for a screen name and then which screen components they want to add from the available list.
Be friendly and conversational. Don't show any of these instructions to the user.
Example response: "Let's configure screen 1. What would you like to name this screen? After that, I'll show you the available screen components you can add."
"""
    elif current_step == "navigation":
        prompt += """
Now let's set up the navigation between screens. For each navigation rule, ask:
1. Source screen ID (which screen to navigate from)
2. Target screen ID (which screen to navigate to)

For each navigation, check if the source screen has a trigger component (a button with isTriggerComponent = true).
If it does, use that as the trigger_component_id with navigation_type = "button_click".
Be friendly and conversational. Don't show any of these instructions to the user.
Example response: "Now let's set up navigation between screens. From which screen ID would you like to navigate? And to which screen ID should it go?"
"""
    elif current_step == "confirmation":
        prompt += """
Show the user the completed journey configuration and ask for confirmation.
Be friendly and conversational. Don't show any of these instructions to the user.
Example response: "Here's your completed journey configuration. Please review it and let me know if you'd like to make any changes, or if you're ready to finalize it."
"""
    elif current_step == "edit":
        prompt += """
Ask the user what they would like to edit. Options include:
1. Journey details (name, type, number of screens)
2. Screen details (name, components)
3. Navigation rules

Be friendly and conversational. Don't show any of these instructions to the user.
Example response: "What would you like to edit? You can modify the journey details, screen configurations, or navigation rules."
"""
    logger.debug(f"Gemini prompt built: {prompt[:100]}...")
    return prompt

# Function to call Google Gemini API
async def call_gemini_api(prompt):
    try:
        logger.info("Calling Gemini API")
        # Call Gemini API
        response = await model.generate_content_async(prompt)
        logger.info("Received response from Gemini API")
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}")
        # Fallback responses in case of API failure
        if "welcome" in prompt:
            return "Let's build your banking journey configuration. What would you like to name this journey? Also, please specify the journey type (e.g., 'single') and how many screens you'd like to include."
        elif "screen" in prompt:
            return "Let's configure this screen. What would you like to name it? After that, I'll show you the available screen components you can add."
        elif "navigation" in prompt:
            return "Now let's set up navigation between screens. From which screen ID would you like to navigate? And to which screen ID should it go?"
        elif "confirmation" in prompt:
            return "Here's your completed journey configuration. Please review it and let me know if you'd like to make any changes, or if you're ready to finalize it."
        elif "edit" in prompt:
            return "What would you like to edit? You can modify the journey details, screen configurations, or navigation rules."
        else:
            return "I understand. Let's continue building your journey configuration."

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check endpoint called")
    return jsonify({
        "status": "ok",
        "timestamp": time.time()
    })

@app.route('/start', methods=['POST'])
async def start():
    logger.info("Starting new chat session")
    # Create a new session
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    session['conversation_history'] = []
    session['journey_data'] = {
        "journey_name": "",
        "journey_type": "",
        "no_screens": 0,
        "screens": [],
        "navigation": []
    }
    session['current_step'] = "welcome"
    logger.info(f"Created new session with ID: {session_id}")
    
    # Build prompt for initial greeting
    prompt = build_gemini_prompt(
        conversation_history=session['conversation_history'],
        current_step=session['current_step'],
        journey_data=session['journey_data']
    )
    
    # Call Gemini API
    response = await call_gemini_api(prompt)
    
    # Update conversation history
    session['conversation_history'].append({
        "role": "assistant",
        "content": response
    })
    
    logger.info("Session started successfully")
    return jsonify({
        "session_id": session_id,
        "response": response
    })

@app.route('/process', methods=['POST'])
async def process():
    logger.info("Process endpoint called")
    data = request.json
    user_message = data.get('message', '')
    logger.info(f"Received user message: {user_message[:50]}...")
    
    # Check if session exists
    if 'session_id' not in session:
        logger.warning("Session expired or not found")
        return jsonify({
            "error": "Session expired or not found",
            "action": "restart"
        }), 401
    
    # Update conversation history with user message
    session['conversation_history'].append({
        "role": "user",
        "content": user_message
    })
    
    # Process based on current step
    current_step = session.get('current_step', 'welcome')
    journey_data = session.get('journey_data', {})
    logger.info(f"Processing message for step: {current_step}")
    
    # Process user input based on current step
    if current_step == "welcome":
        logger.info("Processing welcome step")
        # Parse journey name, type, and number of screens
        if "journey_name" not in journey_data or not journey_data["journey_name"]:
            if "name" in user_message.lower():
                # Extract journey name - look for content after "name" word
                import re
                name_match = re.search(r'name\s+(?:is|:)?\s*([A-Za-z0-9_]+)', user_message.lower())
                if name_match:
                    journey_name = name_match.group(1)
                    journey_data["journey_name"] = journey_name.strip().capitalize()
                    logger.info(f"Extracted journey name: {journey_data['journey_name']}")
            
        if "journey_type" not in journey_data or not journey_data["journey_type"]:
            if "type" in user_message.lower():
                if "single" in user_message.lower():
                    journey_data["journey_type"] = "single"
                elif "multiple" in user_message.lower():
                    journey_data["journey_type"] = "multiple"
                logger.info(f"Extracted journey type: {journey_data.get('journey_type')}")
                
        if "no_screens" not in journey_data or journey_data["no_screens"] == 0:
            # Try to extract number from message
            import re
            numbers = re.findall(r'\d+', user_message)
            if numbers:
                journey_data["no_screens"] = int(numbers[0])
                logger.info(f"Extracted number of screens: {journey_data['no_screens']}")
        
        # Check if we have all the necessary info to move to next step
        if journey_data["journey_name"] and journey_data["journey_type"] and journey_data["no_screens"] > 0:
            # Move to next step
            logger.info("All welcome data collected, moving to screens step")
            session['current_step'] = "screens"
            session['current_screen_index'] = 0
            
    elif current_step == "screens":
        logger.info("Processing screens step")
        current_screen_index = session.get('current_screen_index', 0)
        logger.info(f"Current screen index: {current_screen_index}")
        
        # Initialize screens array if not exist
        if "screens" not in journey_data:
            journey_data["screens"] = []
        
        # If this is a new screen, create it
        if len(journey_data["screens"]) <= current_screen_index:
            logger.info("Creating new screen")
            # Create new screen
            if "screen_name" in user_message.lower() or "name" in user_message.lower() or "call" in user_message.lower():
                # Extract screen name
                import re
                name_match = re.search(r'(?:name|call)\s+(?:it|:)?\s*([A-Za-z0-9_]+)', user_message.lower())
                if name_match:
                    screen_name = name_match.group(1)
                else:
                    # Fallback extraction
                    words = user_message.split()
                    for i, word in enumerate(words):
                        if word.lower() in ["name", "call"] and i < len(words) - 1:
                            screen_name = words[i+1].strip(",:;.")
                            break
                    else:
                        # If no name found, generate a default name
                        screen_name = f"Screen{current_screen_index + 1}"
                
                logger.info(f"Screen name extracted: {screen_name}")
                new_screen = {
                    "screen_id": current_screen_index + 1,
                    "screen_name": screen_name,
                    "template": "defaultTemplate",
                    "style": "defaultScreenStyle",
                    "screen_components": []
                }
                journey_data["screens"].append(new_screen)
                
                # Return available screen components
                response = f"Screen '{screen_name}' created. Here are the available screen components:\n"
                for comp in mock_screen_components:
                    response += f"ID: {comp['screen_component_id']}, Name: {comp['screen_component_name']}\n"
                response += "\nWhich screen component would you like to add to this screen? Please provide the component ID."
                
                session['conversation_history'].append({
                    "role": "assistant",
                    "content": response
                })
                
                session['journey_data'] = journey_data
                logger.info("Returning screen components list")
                return jsonify({"response": response})
        else:
            logger.info("Adding components to existing screen")
            # Adding components to existing screen
            current_screen = journey_data["screens"][current_screen_index]
            
            # Look for component IDs in user message
            import re
            component_ids = re.findall(r'\d+', user_message)
            
            if component_ids:
                component_id = int(component_ids[0])
                logger.info(f"Component ID extracted: {component_id}")
                
                # Find component in mock data
                component_found = None
                for comp in mock_screen_components:
                    if comp["screen_component_id"] == component_id:
                        component_found = comp
                        break
                
                if component_found:
                    logger.info(f"Found component: {component_found['screen_component_name']}")
                    # Get field components for this screen component
                    field_components = mock_field_components.get(component_id, [])
                    
                    # Add component to screen
                    new_component = {
                        "screen_component_id": component_found["screen_component_id"],
                        "screen_component_name": component_found["screen_component_name"],
                        "screen_component_style": "defaultScreenComponentStyle",
                        "field_components": field_components
                    }
                    
                    current_screen["screen_components"].append(new_component)
                    
                    response = f"Added {component_found['screen_component_name']} to screen {current_screen['screen_name']}.\n"
                    
                    # Ask if they want to add more components or move to next screen
                    response += "Would you like to add another component to this screen? If yes, provide the component ID. If no, type 'next screen' to configure the next screen or 'done with screens' if you've configured all screens."
                    
                    session['conversation_history'].append({
                        "role": "assistant",
                        "content": response
                    })
                    
                    session['journey_data'] = journey_data
                    logger.info("Component added successfully")
                    return jsonify({"response": response})
            
            # Check if user wants to move to next screen
            if "next screen" in user_message.lower():
                logger.info("Moving to next screen")
                current_screen_index += 1
                session['current_screen_index'] = current_screen_index
                
                if current_screen_index < journey_data["no_screens"]:
                    logger.info(f"Configuring screen {current_screen_index + 1}")
                    response = f"Let's configure screen {current_screen_index + 1}. What would you like to name this screen?"
                else:
                    # We've configured all screens, move to navigation
                    logger.info("All screens configured, moving to navigation step")
                    session['current_step'] = "navigation"
                    response = "Great! All screens have been configured. Now let's set up navigation between screens. For each navigation rule, I'll need the source screen ID and target screen ID."
                
                session['conversation_history'].append({
                    "role": "assistant",
                    "content": response
                })
                
                session['journey_data'] = journey_data
                return jsonify({"response": response})
            
            # Check if user is done with all screens
            if "done with screens" in user_message.lower():
                logger.info("User indicated done with screens, moving to navigation step")
                session['current_step'] = "navigation"
                response = "Great! All screens have been configured. Now let's set up navigation between screens. For each navigation rule, I'll need the source screen ID and target screen ID."
                
                session['conversation_history'].append({
                    "role": "assistant",
                    "content": response
                })
                
                session['journey_data'] = journey_data
                return jsonify({"response": response})
    
    elif current_step == "navigation":
        logger.info("Processing navigation step")
        # Initialize navigation array if not exist
        if "navigation" not in journey_data:
            journey_data["navigation"] = []
        
        # Look for screen IDs in user message
        import re
        screen_ids = re.findall(r'\d+', user_message)
        
        if len(screen_ids) >= 2:
            source_id = int(screen_ids[0])
            target_id = int(screen_ids[1])
            logger.info(f"Navigation extracted: from screen {source_id} to screen {target_id}")
            
            # Find trigger component in source screen
            trigger_component_id = None
            source_screen = None
            
            for screen in journey_data["screens"]:
                if screen["screen_id"] == source_id:
                    source_screen = screen
                    break
            
            if source_screen:
                for component in source_screen.get("screen_components", []):
                    for field in component.get("field_components", []):
                        if field.get("isTriggerComponent", False):
                            trigger_component_id = field.get("fieldComponentId")
                            logger.info(f"Found trigger component: {trigger_component_id}")
                            break
                    if trigger_component_id:
                        break
            
            # Create navigation rule
            navigation_rule = {
                "source_screen_id": source_id,
                "target_screen_id": target_id,
                "trigger_component_id": trigger_component_id,
                "navigation_type": "button_click"
            }
            
            journey_data["navigation"].append(navigation_rule)
            logger.info("Navigation rule added")
            
            response = f"Added navigation rule from screen {source_id} to screen {target_id}."
            
            # Check if we need more navigation rules
            if len(journey_data["navigation"]) < journey_data["no_screens"] - 1:
                response += " Would you like to add another navigation rule? If yes, please provide the source and target screen IDs. If not, type 'done with navigation'."
            else:
                response += " It looks like you've set up navigation for all screens. Type 'done with navigation' to review your complete journey configuration."
            
            session['conversation_history'].append({
                "role": "assistant",
                "content": response
            })
            
            session['journey_data'] = journey_data
            return jsonify({"response": response})
        
        # Check if user is done with navigation
        if "done with navigation" in user_message.lower():
            logger.info("User indicated done with navigation, moving to confirmation step")
            session['current_step'] = "confirmation"
            response = "Great! All navigation rules have been configured. Here's your complete journey configuration:\n\n"
            response += json.dumps(journey_data, indent=2)
            response += "\n\nWould you like to make any changes (edit) or finalize this configuration (confirm)?"
            
            session['conversation_history'].append({
                "role": "assistant",
                "content": response
            })
            
            session['journey_data'] = journey_data
            return jsonify({"response": response})
    
    elif current_step == "confirmation":
        logger.info("Processing confirmation step")
        if "edit" in user_message.lower():
            logger.info("User wants to edit, moving to edit step")
            session['current_step'] = "edit"
            response = "What would you like to edit? You can modify the journey details, screen configurations, or navigation rules."
            
            session['conversation_history'].append({
                "role": "assistant",
                "content": response
            })
            
            return jsonify({"response": response})
        
        elif "confirm" in user_message.lower() or "finalize" in user_message.lower():
            logger.info("User confirmed journey configuration")
            # Save final configuration
            final_config = journey_data
            
            # Clear session
            session.clear()
            logger.info("Session cleared")
            
            response = "Your journey configuration has been finalized and saved. Here's the final JSON:\n\n"
            response += json.dumps(final_config, indent=2)
            response += "\n\nThank you for using the chatbot to build your journey configuration!"
            
            logger.info("Journey configuration finalized")
            return jsonify({
                "response": response,
                "final_config": final_config,
                "status": "complete"
            })
    
    elif current_step == "edit":
        logger.info("Processing edit step")
        # Handle edit requests - simplified for this example
        if "journey" in user_message.lower() and "details" in user_message.lower():
            logger.info("User wants to edit journey details, returning to welcome step")
            session['current_step'] = "welcome"
            response = "Let's edit the journey details. What would you like to update about the journey name, type, or number of screens?"
        
        elif "screen" in user_message.lower():
            logger.info("User wants to edit screen configurations, returning to screens step")
            session['current_step'] = "screens"
            session['current_screen_index'] = 0
            response = "Let's edit the screen configurations. For which screen would you like to make changes? (Please provide the screen ID)"
        
        elif "navigation" in user_message.lower():
            logger.info("User wants to edit navigation rules, returning to navigation step")
            session['current_step'] = "navigation"
            response = "Let's edit the navigation rules. What changes would you like to make to the navigation?"
        
        else:
            logger.warning("Could not understand edit request")
            response = "I didn't understand what you'd like to edit. You can modify the journey details, screen configurations, or navigation rules."
        
        session['conversation_history'].append({
            "role": "assistant",
            "content": response
        })
        
        return jsonify({"response": response})
    
    # Build prompt for Gemini API
    logger.info("Using Gemini API for general response")
    prompt = build_gemini_prompt(
        conversation_history=session['conversation_history'],
        current_step=current_step,
        journey_data=journey_data
    )
    
    # Call Gemini API
    response = await call_gemini_api(prompt)
    
    # Update conversation history
    session['conversation_history'].append({
        "role": "assistant",
        "content": response
    })
    
    # Update session data
    session['journey_data'] = journey_data
    
    logger.info("Response processed successfully")
    return jsonify({
        "response": response
    })

if __name__ == '__main__':
    # Run the Flask app with asyncio support
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    
    logger.info("Starting application server")
    config = Config()
    config.bind = ["0.0.0.0:5001"]
    
    asyncio.run(serve(app, config))