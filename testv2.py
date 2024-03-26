import streamlit as st
import anthropic
import os
import boto3

# Set AWS credentials and region
os.environ["AWS_ACCESS_KEY_ID"] = "ADD"
os.environ["AWS_SECRET_ACCESS_KEY"] = "ADD"
os.environ["REGION_NAME"] = "ADD"

# Setup AWS session for S3
boto3.setup_default_session(aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                            region_name=os.getenv('REGION_NAME'))

# Initialize S3 client
s3 = boto3.client('s3')

# Define your bucket name
bucket_name = 'partnerletters2'

hf_file_names = ['CCV Q4 2023.txt', 'Cedar Creek Partners Q4 2023.txt', 'Greenlight Capital Q4 2023.txt',
                 'Immersion Investment Partners Q4 2023.txt', 'OKeefe Stevens Q4 2023.txt']
past_thesis_files = ['Algoma_Steel_Write_Up.txt', 'Aston Martin Write Up.txt', 'Tesla Write Up.txt']
earnings_call_files = ['Aston Martin Q4 2023 Earnings Call.txt', 'Wingstop Q4 2023 Earnings Call.txt', 'Atlas Energy Solutions Q4 2023 Earnings Call.txt']
thesis_inspiration_files = ['Thesis_Ryan.txt', 'Thesis_Wybe.txt']

def generate_response(prompt, system_prompt, model="claude-3-haiku-20240307"):
    # Initialize the Anthropic client
    client = anthropic.Anthropic(api_key="ADD")

    # Send the prompt to Claude API
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        temperature=0.2,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    # Display the response
    raw_text = message.content
    answer = raw_text[0].text
    st.write(answer)

def main():
    st.title('CCM AI Tools Test')

    # List of options for the drop-down menu
    options = ['Idea Gen', 'Research', 'Monitor']
    selected_option = st.selectbox('What can AI help you with today?', options)

    if selected_option == 'Idea Gen':
        options_1 = ['Partner Letters', 'Podcasts']
        source = st.selectbox('Choose source', options_1)

        if source == 'Partner Letters':
            selected_files = st.multiselect('Select which funds:', hf_file_names)

            options_2 = ['Equity Names', 'Macro Themes', 'Sector View', 'Customized Idea Gen']
            content = st.selectbox('Choose what content you want to extract', options_2)

            equity_type = None
            if content == 'Equity Names':
                equity_type = st.selectbox('Select equity type', ['Long', 'Short'])

            sector = None
            if content == 'Sector View':
                sector = st.selectbox('Select sector', ['Energy', 'Raw Materials', 'Technology', 'Consumer Discretionary', 'Industrial', 'Other'])

            if content == 'Customized Idea Gen':
                selected_past_thesis_file = st.selectbox('Select past thesis:', past_thesis_files)

            submit_button = st.button('Submit')

            if submit_button:
                # Fetch and combine the content of the selected files
                document_contents = []
                for selected_file in selected_files:
                    file_obj = s3.get_object(Bucket=bucket_name, Key=selected_file)
                    document_content = file_obj['Body'].read().decode('utf-8')
                    document_contents.append(document_content)
                combined_document_content = "\n".join(document_contents)

                if content == 'Equity Names' and equity_type:
                    prompt_message = f"Name all the companies mentioned in the document that were pitched as {equity_type} ideas. For short ideas, please be very specific. \
                        If no short ideas were pitched, please return 'The selected hedge funds did not pitch any short ideas for the given quarter.'. \
                        It is normal for a partner letter to focus more on long ideas than short ideas, so please be very specific when returning your answer. \
                        Please return your answer in a table format with 4 columns: Company Name, Ticker, High-Level Thesis Summary, and Fund Name. \
                        Make sure you capture the core investment thesis and explain why a certain stock is cheap or expensive. \
                        Include at least 3 sentences for the thesis summary. If multiple partner letters were uploaded, it is important that you \
                        return all the companies discussed in the document and at least one company name for each hedge fund."

                elif content == 'Macro Themes':
                    prompt_message = "What are the 3 most relevant macro economic themes discussed in the partner letters? Please break them down into clear categories \
                        such as interest rates, inflation, forex, unemployment etc... If the partner letter of multiple funds are uploaded, explain how the view of \
                        each fund is different from the other. Also explain which funds have a similar view. Lastly, explained how the funds positioned themselves to \
                        capitalize on these macro trends."

                elif content == 'Sector View' and sector:
                    prompt_message = f"What view do the hedge funds have of the {sector} sector? Please share the investment thesis for the given sector. \
                        It's very important that you analyze the risks associated to investing in these companies. Also, please share which equity names the \
                        funds believe are best positioned to benefit (or not) from the investment thesis on the particular sector."

                elif content == 'Customized Idea Gen':
                    prompt_message = "I have uploaded my own investment write-up in addition to the partner letters. I will ask you a question about it. \
                        I would like you to first read my investment thesis to understand the high-level thesis of the company and then answer the question. \
                        This is the question: Which investment thesis discussed in the partner letters aligns most with my own investment thesis? It does \
                        not necessarily need to be the same industry it just needs to have a similar investment strategy. Please return only one investment \
                        thesis. It is important to share which fund discussed the company, a brief overview of the company, and how the overarching thesis \
                        is like mine. This is my investment thesis: {selected_past_thesis_file}"

                system_prompt = f"You are an excellent investment analyst. I have attached a pdf containing partner letters of different hedge funds\
                for you to reference for your task. I will ask you a question about it. I would like you to first read the entire document \
                    and find equity positions mentioned in the document that are most relevant to the question. Each hedge fund writes a \
                        partner letter every quarter where they discuss certain topics like their performance for the quarter, their views on \
                            the macro economy, and an explanation of why they added a certain equity position to the fund. Please note that each \
                                partner letter is written differently. Here is the document content for analysis:\n{combined_document_content}"

                generate_response(prompt_message, system_prompt)

    elif selected_option == 'Research':
        research_options = ['Generate 1-page Write Up With Transcript', 'Research Company Without Transcript']
        research_type = st.selectbox('Select research type:', research_options)

        if research_type == 'Research Company Without Transcript':
            company = st.text_input('Enter company name:')
            ticker = st.text_input('Enter stock ticker:')

            research_submit_button = st.button('Submit Research')

            if research_submit_button:
                system_prompt = f"You are an excellent investment analyst. I will ask you a question about {company} ({ticker}), a publicly-listed company. \
                    Please return a high-level overview of the company like you work at a top notch hedge fund as an analyst"

                prompt_message = "What is the history of the company and in what industry does it operate? First give me a high-level explanation of the industry dynamics. \
                    It is important that you include an analysis of competitive forces using Porter's Five Forces framework when analyzing the industry dynamics and trends. \
                    What are key drivers to keep track of for this industry? Next give an overview of the company's products/services and the company's business model. \
                    Explain who the customers and suppliers are, and how the company distributes its product. Next, I would like you to do a very high-level analysis of \
                    the company's revenue model by doing back-of-envelope calculations. It is particularly important to keep the analysis simple and big picture. First do \
                    a top-down approach by estimating the market size and market share. Then also do a bottom-up analysis by estimating the unit economics. It does not \
                    matter whether your guess is correct, I care about how you reason your answer. Is the company growing quickly or does it just blob along? Lastly, I \
                    would like you to analyze the cost structure. Are the costs mostly fixed or variable? How does this translate into margins?"

                generate_response(prompt_message, system_prompt)

        elif research_type == 'Generate 1-page Write Up With Transcript':
            selected_earnings_call = st.selectbox('Select earnings call:', earnings_call_files)
            selected_thesis_inspiration = st.selectbox('Choose thesis inspiration:', thesis_inspiration_files)

            research_submit_button = st.button('Submit Research')

            if research_submit_button:
                # Fetch the content of the selected files
                earnings_call_content = s3.get_object(Bucket=bucket_name, Key=selected_earnings_call)['Body'].read().decode('utf-8')
                thesis_inspiration_content = s3.get_object(Bucket=bucket_name, Key=selected_thesis_inspiration)['Body'].read().decode('utf-8')

                system_prompt = "I have attached a file that contains multiple past one-page investment theses. I would like you to write an investment thesis in the same tone and formate as my previous write ups. \
                        Next, use the earnings transcript to understand the company that you are analyzing. Use the transcript to analyze the main topics discussed and take note of factual data mentioned in the transcript.\
                            It is important to read the whole document before you complete your task."

                prompt_message = "Write a 500-word investment thesis for the company discussed in the earnings transcript in the style of the past investment theses I have provided you. \
                    Return only the final investment thesis. Start with the name of the company you are analyzing at the top, then proceed with the investment thesis.\
                        Make sure you capture the high-level investment thesis and communicate it in a clear manner."

                combined_document_content = f"{earnings_call_content}\n{thesis_inspiration_content}"

                generate_response(prompt_message, system_prompt + f"\n\nHere is the document content for analysis:\n{combined_document_content}", model="claude-3-sonnet-20240229")

    elif selected_option == 'Monitor':
        selected_earnings_call = st.selectbox('Select earnings call:', earnings_call_files)

        monitor_submit_button = st.button('Submit Monitor')

        if monitor_submit_button:
            # Fetch the content of the selected file
            earnings_call_content = s3.get_object(Bucket=bucket_name, Key=selected_earnings_call)['Body'].read().decode('utf-8')

            system_prompt = "I uploaded an earnings transcript of a company. You will need it to complete your task. In the document, there are multiple speakers, \
                either these are company employees or analysts. Every time they talk, they are identified by their name and position. The earnings transcript follows \
                    a format where management first discusses the companys achievements, followed by a Q&A session with analysts. I have also attached a template for \
                        you that I would like you to use for your answer in the </template></template> XML tags. <template> [Company Name] Earnings Call Notes\
                            Valuation: \
                                - Market Cap:\
                                - Net Debt:\
                                - Enterprise Value:\
                                - Revenue: [What was quarterly revenue? What was revenue for the last twelve months?]\
                                - Free Cash Flow: [What was FCF for the quarter and year? Is FCF normalized?]\
                                - EV/Revenue: [Divide Enterprise Value by Revenue]\
                                - EBIT Margin: [What is the operating margin in the quarter? Is the normalized?]\
                                - Payback Time: [Divide EV/Revenue by EBIT margin]\
                            Overview\
                                - Industry: [What industry does it operate in? If there are multiple, name each industry. What are the industry dynamics? Is it generally a profitable sector or not? What is the industry outlook?]\
                                - Peers: [How does the company compare to its peers? How well is the company positioned financially and competitively heading into the year? What are the barriers to entry? What is the industry competition like?]\
                                - KPIs: [Name the 3 most important KPIs that track the companys performance]\
                            Financials:\
                                - Revenue: [What are the drivers of revenue? Demand, capacity, average selling price, the price of a commodity?]\
                                - Margins [What are key drivers? How did costs evolve? Does the company have operational leverage? Does the company expect margin expansion?]\
                                - Balance Sheet: [Is the balance sheet healthy? How much debt does the company have? Any concerns regarding liquidity or debt?]\
                                - Net Working Capital: [Are inventories normalized?]\
                                - Free Cash Flow: [What was FCF for the year? How much FCF does the company expect in the next 3 years? Is the company in a free cash flow generating cycle or in a capex cycle? Be specific in your answer. Are there headwinds or tailwinds? Is free cash flow currently normalized?]\
                                - Cash position: [What did the company do with its cash? Invest? Return to shareholders?]\
                            Strategic Highlights:\
                                - Demand [What is demand for the company's products or services?]\
                                - Supply [Were there any constraints or setbacks?]\
                                - New Products\
                                - Secular Trends: [What are positive drivers for the company?]\
                                - Additional operational/strategic comments\
                            Risks:\
                                - Risks: [What are the key risks for the company in the near future? Are they exposed to suppliers? Is there a risk of demand crunch? Is the company entering a new business and is there execution risk?]\
                            Additional Notes:\
                                - Capital allocation.\
                                - Management changes.\
                            Questions from Analysts:\
                                - Highlight the most important analyst questions. \
                                - What are the main concerns for analysts?\
                            </template>"

            prompt_message = "Please answer the questions in the brackets in the template. In other words: fill in the blanks. Use at least 5 sentences for each section. It is important that you \
                differentiate between the overall market trends discussed and company-specific metrics. Also, for each financial metric, include managements forecast. \
                    Make sure that you identify the most important KPIs that explain the companys performance. Lastly, make sure to give context when sharing absolute \
                        numbers. For example, when you share the total capex spend, share what percentage of revenue it is. "

            generate_response(prompt_message, system_prompt + f"\n\nHere is the earnings transcript:\n{earnings_call_content}", model="claude-3-sonnet-20240229")

if __name__ == '__main__':
    main()
