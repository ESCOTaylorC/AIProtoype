from openai import OpenAI
import openai
import os

secretapi = os.getenv('OPENAI_FREEAPI')

openai.apikey = secretapi

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
                    "content": """Convert control narratives to ladder logic pseudocode.
                                Follow these rules:
                                1. Use clear IF-THEN statements
                                2. Include timer and counter logic where appropriate
                                3. Use standard PLC programming conventions
                                4. Structure the code with proper indentation
                                5. Include comments for clarity

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