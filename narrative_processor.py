from openai import OpenAI
import openai
import os

secretapi1 = os.getenv('OPENAI_FREEAPI')

openai.apikey = secretapi1

def process_control_narrative(narrative_text):
    """Process control narrative and generate pseudocode."""
    if not narrative_text or not narrative_text.strip():
        raise ValueError("Control narrative text cannot be empty")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Updated to use the free tier model
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert on industrial and manufacturing process control. 
                    Your purpose is to aid automation engineers in programming using ladder logic.
                    If an engineer uploads a control narrative, your job is to extract information 
                    from the narrative relevant to coding and produce all the relevant information 
                    in the form of ladder logic pseudocode. 
                    Follow pseudocode standards, use If/Then statements, and make results concise. 
                    Make sure information is taken directly from the extracted text from the control narrative.                   
                    
                    Step 1: User uploads the text of a control narrative
                    Step 2:  Analyze the text uploaded by the user for statements that contain equipment, conditions and actions.
                    Step 3: Present the user with concise pseudocode using structured text with comparison and if/then statements.

                    Example text: The floor A motor will turn on when the floor B high-level bindicator is activated. 
                    Action: Floor A motor turns on
                    Equipment: floor A motor, Floor B high-level bindicator
                    Conditions: floor B bindicator is activated

                    Example pseudocode conversion: 
                    If FloorBBindicator = 1, 
                    Then set FloorAMotorOutputCommand = 1
                    Else set FloorAMotorOutputCommand = 0

                                Format the output as proper ladder logic pseudocode."""
                },
                {
                    "role": "user",
                    "content": f"Convert this control narrative to ladder logic pseudocode:\n\n{narrative_text}"
                }
            ]
        )

        pseudocode = response.choices[0].message.content

        # Format the pseudocode using the utility function
        from utilities import format_pseudocode
        formatted_pseudocode = format_pseudocode(pseudocode)

        # Add header comments
        final_pseudocode = f"""// Generated Ladder Logic Pseudocode
// Based on Control Narrative

{formatted_pseudocode}
"""
        return final_pseudocode

    except Exception as e:
        raise Exception(f"Error processing control narrative: {str(e)}")