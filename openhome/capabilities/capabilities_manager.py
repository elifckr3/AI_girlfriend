import json
import importlib.util
import threading  # Import threading to use Event
from openhome.utility import load_json

def check_and_perform_action(message, personality):
    """
    Dynamically checks the user's message against capabilities defined in capabilities.json,
    executes the matching capability, and decides if the main thread should pause. Adds debug
    prints for visibility and handles the resume_event for pausing logic.

    Args:
        message (str): The user's message.
        personality (dict): The current personality context.

    Returns:
        dict: Feedback from the executed capability including messages, control instructions, and the resume_event object.
    """
    
    capabilities = load_json('openhome/capabilities/capabilities.json')
    print("Loaded capabilities from JSON.")
    
    for capability in capabilities:
        if any(trigger.lower() in message.lower() for trigger in capability['Triggers']):
            print(f"Trigger found for capability: {capability['Command']}")
            
            module_path = capability['Library']
            module_name = module_path.replace('/', '.').rstrip('.py')
            
            try:
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"Module loaded: {module_name}")
                
                # Create the resume_event object here
                resume_event = threading.Event()
                
                # Pass the resume_event along with message and personality to the capability's main function
                feedback = module.main(message, personality, resume_event)
                print(f"Executed {capability['Command']}, Library: {module_path}")
                
                # Return feedback including the resume_event for handling pausing logic
                return {
                    "feedback": feedback,
                    "pauseMain": capability['PauseMain'],
                    "command": capability['Command'],
                    "resumeEvent": resume_event  # Include the resume_event in the return value
                }
            except Exception as e:
                print(f"Failed to load or execute module {module_name}. Error: {e}")
                return {"feedback": f"Error executing capability: {e}", "pauseMain": False, "command": None}
    
    print("No capability triggered.")
    return {"feedback": None, "pauseMain": False, "command": None}