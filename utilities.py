import pandas as pd
import io
import streamlit as st

def convert_df_to_csv(df):
    """Convert DataFrame to CSV string."""
    return df.to_csv(index=False).encode('utf-8')

def validate_file_size(file):
    """Validate uploaded file size (max 10MB)."""
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file.size > MAX_FILE_SIZE:
        raise ValueError("File size exceeds 10MB limit")
    return True

def format_pseudocode(code):
    """Format pseudocode with proper indentation and structure."""
    lines = code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        line = line.strip()
        if line.startswith('END') or line.startswith('}'):
            indent_level -= 1
        formatted_lines.append('    ' * indent_level + line)
        if line.endswith('THEN') or line.endswith('{'):
            indent_level += 1
    
    return '\n'.join(formatted_lines)


def add_logo():
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"] {
                    background-image: url(https://www.bing.com/images/search?view=detailV2&ccid=UeTDyWDk&id=07E35B005863C276BBE231B1DAF356652AF0689A&thid=OIP.UeTDyWDkhhDFzlXY5b0EQQHaBf&mediaurl=https%3A%2F%2Ftheescogroup.com%2Fwp-content%2Fuploads%2F2020%2F07%2F1331x1331-1.jpg&cdnurl=https%3A%2F%2Fth.bing.com%2Fth%2Fid%2FR.51e4c3c960e48610c5ce55d8e5bd0441%3Frik%3DmmjwKmVW89qxMQ%26pid%3DImgRaw%26r%3D0&exph=269&expw=1331&q=esco+group+logo&simid=607996632284477065&FORM=IRPRST&ck=759BF402C47B52323D02CC644AC4BE99&selectedIndex=9&itb=0&cw=1721&ch=835&ajaxhist=0&ajaxserp=0);
                    background-repeat: no-repeat;
                    padding-top: 120px;
                    background-position: 20px 20px;
                }

                [data-testid="stSidebar"]::before {
                    content: "My Company Name";
                    margin-left: 20px;
                    margin-top: 20px;
                    font-size: 30px;
                    position: relative;
                    top: 100px;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )