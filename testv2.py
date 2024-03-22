import streamlit as st
import anthropic
import os
import boto3

# Set AWS credentials and region
os.environ["AWS_ACCESS_KEY_ID"] = "ADD_ACCESS"
os.environ["AWS_SECRET_ACCESS_KEY"] = "ADD_KEY"
os.environ["REGION_NAME"] = "ADD_REGION"

# Setup AWS session for S3
boto3.setup_default_session(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                            region_name=os.getenv('REGION_NAME'))

# Initialize S3 client
s3 = boto3.client('s3')

# Define your bucket name and fetch file names from the bucket
bucket_name = 'partnerletters2'
file_names = ['CCV Q4 2024 Partner Letter.txt', 'Greenlight Capital Q4 2024 Partner Letter.txt']

st.title('CCM AI Tools Test')

# List of options for the drop-down menu
options = ['Idea Gen', 'Research', 'Monitor']
options_1 = ['Partner Letters', 'Podcasts']
options_2 = ['Equity Names', 'Macro View', 'Sector View', 'Performance']

# Creating the drop-down menu and storing the selected option
selected_option = st.selectbox('What can AI help you with today?', options)
source = st.selectbox('Choose source', options_1)
selected_files = st.multiselect('Select which funds:', file_names)
content = st.selectbox('Choose what content you want to extract', options_2)

button = st.button('Submit')
if button and selected_files:
    document_contents = []
    for selected_file in selected_files:
        # Fetch each selected document from S3
        file_obj = s3.get_object(Bucket=bucket_name, Key=selected_file)
        document_content = file_obj['Body'].read().decode('utf-8')
        document_contents.append(document_content)

    combined_document_content = "\n".join(document_contents)
    
    # Initialize the Anthropic client
    client = anthropic.Anthropic(
        api_key="ADD_KEY"
    )

    # Send the combined document contents along with the prompt to Claude API
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1000,
        temperature=0.2,
        system=f"You are an excellent investment analyst. I have attached a pdf containing partner letters of different hedge funds\
              for you to reference for your task. I will ask you a question about it. I would like you to first read the entire document \
                and find equity positions mentioned in the document that are most relevant to the question. Each hedge fund writes a \
                    partner letter every quarter where they discuss certain topics like their performance for the quarter, their views on \
                        the macro economy, and an explanation of why they added a certain equity position to the fund. Please note that each \
                            partner letter is written differently. Here is the document content for analysis:\n{combined_document_content}",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Name all the companies mentioned in the document. Include all the companies that are discussed in detail, \
                            regardless of whether the fund exited the position or if it was a poor performer. Please return your answer in a \
                                list format with each line starting with the Company Name, a High-Level Thesis Summary, and the Fund Name. Make \
                                    sure you capture the core investment thesis and explain why a certain stock is cheap or expensive. Include at \
                                        least 3 sentences for the thesis summary. It is also important that you return all the companies discussed \
                                            in the document and at least one company name for each hedge fund."
                    }
                ]
            }
        ]
    )

    # Display the response
    raw_text = message.content
    answer = raw_text[0].text
    st.write(answer)
