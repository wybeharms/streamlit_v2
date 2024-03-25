import streamlit as st
import anthropic
import os
import boto3

# Set AWS credentials and region
os.environ["AWS_ACCESS_KEY_ID"] = "AWS_ACCESS_KEY_ID"
os.environ["AWS_SECRET_ACCESS_KEY"] = "AWS_SECRET_ACCESS_KEY"
os.environ["REGION_NAME"] = "REGION_NAME"

# Setup AWS session for S3
boto3.setup_default_session(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                            region_name=os.getenv('REGION_NAME'))

# Initialize S3 client
s3 = boto3.client('s3')

# Define your bucket name
bucket_name = 'partnerletters2'

# Fetch file names from the bucket (assuming this is dynamic in the real scenario)
file_names = ['CCV Q4 2023.txt', 'Cedar Creek Partners Q4 2023.txt','Greenlight Capital Q4 2023.txt',\
              'Immersion Investment Partners Q4 2023.txt','OKeefe Stevens Q4 2023.txt', 'Algoma_Steel_Write_Up.txt']

st.title('CCM AI Tools Test')

# List of options for the drop-down menu
options = ['Idea Gen', 'Research', 'Monitor']
selected_option = st.selectbox('What can AI help you with today?', options)

if selected_option == 'Idea Gen':
    options_1 = ['Partner Letters', 'Podcasts']
    source = st.selectbox('Choose source', options_1)

    if source == 'Partner Letters':
        selected_files = st.multiselect('Select which funds:', file_names)

        options_2 = ['Equity Names', 'Macro Themes', 'Sector View', 'Customized Idea Gen']
        content = st.selectbox('Choose what content you want to extract', options_2)

        # Fetch and combine the content of the selected files
        document_contents = []
        for selected_file in selected_files:
            file_obj = s3.get_object(Bucket=bucket_name, Key=selected_file)
            document_content = file_obj['Body'].read().decode('utf-8')
            document_contents.append(document_content)
        combined_document_content = "\n".join(document_contents)
        additional_document = "Algoma_Steel_Write_Up.txt"

        # Initialize the Anthropic client
        client = anthropic.Anthropic(api_key="API_KEY")

        if content == 'Equity Names':
            equity_type = st.selectbox('Select equity type', ['long', 'short'])

            if equity_type == 'Long':
                prompt_message = "Name all the companies mentioned in the document that were pitched a 'long' ideas. Include all the companies \
                    that are discussed in detail, regardless of whether the fund exited the position or if it was a poor performer, as long as \
                        the initial thesis was that the stock would appreciate. Please return your answer in a list format with each line starting \
                            with the Company Name, the stock ticker, a High-Level Thesis Summary, and the Fund Name that pitched it. Make sure you \
                                capture the core investment thesis and explain why a certain stock is cheap. Include at least 3 sentences for the thesis \
                                    summary. If multiple partner letters were uploaded, it is important that you return all the companies discussed in the \
                                        document and at least one company name for each hedge fund."
            elif equity_type == 'Short':
                prompt_message = "Name all the companies mentioned in the document that were pitched as 'short' ideas. Please return your answer in a \
                    list format with each line starting with the Company Name, the stock ticker, a High-Level Thesis Summary, and the Fund Name that \
                        pitched it. Make sure you capture the core investment thesis and explain why a certain stock is expensive. Include at least 3 \
                            sentences for the thesis summary. If no short ideas were pitched, please return 'The selected hedge funds did not pitch any \
                                short ideas for the given quarter.'. It is normal for a partner letter to focus more on long ideas than short ideas, so \
                                    please be very specific when returning your answer."
        
        elif content == 'Macro Themes':
            # Macro Themes prompt
            prompt_message = "What are the 3 most relevant macro economic themes discussed in the partner letters? Please break them down into clear categories \
                such as interest rates, inflation, forex, unemployment etc... If the partner letter of multiple funds are uploaded, explain how the view of \
                    each fund is different from the other. Also explain which funds have a similar view. Lastly, explained how the funds positioned themselves to \
                        capitalize on these macro trends."
        elif content == 'Sector View':
            sector = st.selectbox('Select sector', ['Energy', 'Raw Materials', 'Technology', 'Consumer Discretionary', 'Industrial', 'Other'])
            # Sector View prompt
            prompt_message = f"What view do the hedge funds have of the {sector} sector? Please share the investment thesis for the given sector. \
                It's very important that you analyze the risks associated to investing in these companies. Also, please share which equity names the \
                    funds believe are best positioned to benefit (or not) from the investment thesis on the particular sector."
        
        elif content == 'Customized Idea Gen':
            # Customized Idea Gen prompt
            prompt_message = f"I have uploaded my own investment write-up in addition to the partner letters. I will ask you a question about it. \
            I would like you to first read my investment thesis to understand the high-level thesis of the company and then answer the question. \
                This is the question: Which investment thesis discussed in the partner letters aligns most with my own investment thesis? It does \
                    not necessarily need to be the same industry it just needs to have a similar investment strategy. Please return only one investment \
                        thesis. It is important to share which fund discussed the company, a brief overview of the company, and how the overarching thesis \
                            is like mine. This is my investment thesis: {additional_document}"

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
                            "text": prompt_message
                        }
                    ]
                }
            ]
        )

        # Display the response
        raw_text = message.content
        answer = raw_text[0].text
        st.write(answer)
