import streamlit as st
import json
# import streamlit.components.v1 as components # No longer needed
from st_copy_to_clipboard import st_copy_to_clipboard # Import the component

# Page config MUST be the first Streamlit command
st.set_page_config(layout="wide") # Use wide layout for better readability

# Load the data from the JSON file
try:
    # Ensure the path to the JSON file is correct.
    # If app.py is in the root of your project, and the JSON file is also in the root,
    # then '_cache_editor_linkedin_output.json' is correct.
    # If app.py is in a subdirectory, you might need to adjust the path, e.g., '../_cache_editor_linkedin_output.json'
    with open('_cache_editor_linkedin_output.json', 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    st.error("Error: '_cache_editor_linkedin_output.json' not found. Please ensure the file exists and the path is correct relative to 'app.py'.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error: Could not decode JSON from '_cache_editor_linkedin_output.json'. Please check the file format.")
    st.stop()

st.title("LinkedIn Post Suggestions Dashboard")
st.markdown("Displaying topics and generated LinkedIn posts from `_cache_editor_linkedin_output.json`")

if not data:
    st.warning("No data found in the JSON file.")
else:
    # Using columns for a more structured layout
    num_columns = 2 # You can adjust the number of columns
    cols = st.columns(num_columns)
    
    for i, item in enumerate(data):
        col_index = i % num_columns
        with cols[col_index]:
            st.subheader(f"Topic {i+1}: {item.get('topic', 'No Topic Title')}")
            
            with st.expander("View LinkedIn Post", expanded=False): # Make posts collapsible
                post_text_to_display = item.get('linkedin_post', 'No post content available.')
                st.markdown(post_text_to_display)

                post_text_for_copy = item.get('linkedin_post', '') 
                # Use the st_copy_to_clipboard component
                # Providing a unique key is good practice for components in a loop
                st_copy_to_clipboard(post_text_for_copy, key=f"copy_btn_{i}") 

            st.markdown("---") # Visual separator for each item within a column 