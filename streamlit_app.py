import streamlit as st
import pandas as pd
from pid_processor import process_pid_drawing
from narrative_processor import process_control_narrative
from utilities import convert_df_to_csv, validate_file_size
import tempfile
import os



st.set_page_config(
    page_title="P&ID and Control Narrative Analyzer",
    page_icon="🔧",
    layout="wide"
)


def main():
    
    URL = "https://www.teacherstore.org/wp-content/uploads/2024/03/000-ESCO-Group-Logo-Standard.png"
    st.image(URL, width = 300)
    
    st.title("P&ID and Control Narrative Analyzer")

    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["P&ID Analysis", "Control Narrative Processing"])

    with tab1:
        st.header("P&ID Drawing Analysis")
        st.info("Upload a P&ID drawing (PDF or image) to detect equipment symbols and labels.")

        uploaded_file = st.file_uploader(
            "Upload P&ID Drawing",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload a P&ID drawing for analysis"
        )

        if uploaded_file:
            try:
                # Validate file size
                validate_file_size(uploaded_file)

                # Show processing message
                with st.spinner("Processing P&ID drawing..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        temp_path = tmp_file.name

                    try:
                        # Process the drawing
                        equipment_list = process_pid_drawing(temp_path)

                        if equipment_list:
                            # Convert results to DataFrame
                            df = pd.DataFrame(equipment_list)

                            # Display results
                            st.success("Analysis completed successfully!")
                            st.subheader("Detected Equipment")
                            st.dataframe(df)

                            # Download button
                            csv = convert_df_to_csv(df)
                            st.download_button(
                                "Download Equipment List",
                                csv,
                                "equipment_list.csv",
                                "text/csv",
                                key='download-csv'
                            )
                        else:
                            st.warning("No equipment symbols were detected in the drawing.")

                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
                    finally:
                        # Cleanup
                        try:
                            os.unlink(temp_path)
                        except:
                            pass

            except ValueError as e:
                st.error(str(e))

    with tab2:
        st.header("Control Narrative Processing")
        st.info("Enter a control narrative to generate ladder logic pseudocode.")

        narrative = st.text_area(
            "Enter Control Narrative",
            height=200,
            help="Enter the control narrative text to generate pseudocode"
        )

        if st.button("Generate Pseudocode"):
            if narrative:
                with st.spinner("Processing control narrative..."):
                    try:
                        pseudocode = process_control_narrative(narrative)
                        st.success("Pseudocode generated successfully!")
                        st.subheader("Generated Pseudocode")
                        st.code(pseudocode, language='python')

                        # Download button for pseudocode
                        st.download_button(
                            "Download Pseudocode",
                            pseudocode,
                            "pseudocode.txt",
                            "text/plain",
                            key='download-pseudocode'
                        )
                    except Exception as e:
                        st.error(f"Error processing narrative: {str(e)}")
            else:
                st.warning("Please enter a control narrative")

if __name__ == "__main__":
    main()
