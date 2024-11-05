import streamlit as st
import pandas as pd
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import openai
import numpy as np
import uuid
from streamlit_gsheets import GSheetsConnection


# Initialize Google Sheets connection and read data
conn = st.connection("spreadsheet", type=GSheetsConnection)
df = conn.read()


# OpenAI API key for GPT model access
openai_api_key = OPENAI_API_KEY


# Main function to process user prompts and route to appropriate response handler
def get_ai_response(prompt):
    # Define available tools/functions that can be called by the AI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "csv_based_response",
                "description": "Call this function if the user wants macro information such as top/bottom performers.",
            }
        },
        {
            "type": "function",
            "function": {
                "name": "qdrant_based_response",
                "description": "Call this function for associate specific questions, if the prompt includes a name.",
            }
        }
    ]

    # Set up the conversation messages for the AI
    messages = [
    {"role": "system", "content": "You examine what information the user is asking for and choose an appropriate supplied tool to help the user."},
    {"role": "user", "content": f"{prompt}"}
    ]

    # Initialize OpenAI client and get response
    client = openai.OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    # Determine which function to call based on AI's response
    if response.choices[0].finish_reason == 'tool_calls':
        function_call = response.choices[0].message.tool_calls[0].function.name
    else:
        # Default to qdrant_based_response if no specific tool is called
        function_call = "qdrant_based_response"

    # Execute the appropriate function based on AI's decision
    if function_call == "csv_based_response":
        return csv_based_response()
    else:
        # Initialize the required components for qdrant_based_response
        QDRANT_API_KEY = "0-Hp0S1W3blQGjvYJ9G8UhSCJS6QlUiXn_lNldP1hG5CsaIL-YBuyQ"
        client = QdrantClient(
            url="https://403f8d12-d7bf-4407-84af-f8bf1b714623.us-east4-0.gcp.cloud.qdrant.io", 
            api_key=QDRANT_API_KEY,
        )
        model = SentenceTransformer('paraphrase-mpnet-base-v2')
        return qdrant_based_response(client=client, model=model, query_name=prompt)

# Function to handle macro-level data analysis from CSV
def csv_based_response():
    # Read data from Google Sheets
    conn = st.connection("spreadsheet", type=GSheetsConnection)
    df = conn.read()

    # Convert DataFrame to string representation for OpenAI
    df_str = df.to_string()

    # Create OpenAI client
    client = openai.OpenAI(api_key=openai_api_key)
    
    # Query OpenAI to analyze the data
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a data analyst examining employee performance data. Provide insights and analysis based on the data provided. For the summary at the end, just provide a key points recap."
            },
            {
                "role": "user", 
                "content": f"Here is the employee performance data:\n\n{df_str}\n\nPlease analyze this data and provide key insights."
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )

    return response.choices[0].message.content

# Function to handle individual associate queries using Qdrant
def qdrant_based_response(client, model, query_name):
    # Add OpenAI client initialization
    openai_client = openai.OpenAI(api_key=openai_api_key)
    
    COLLECTION_NAMES = ["sampled_data_weekly", "monthly_stats", "individual_summaries"]
    
    # Use the passed query_name instead of expecting user input
    query_vector = model.encode(query_name).tolist()
    
    # Perform vector searches across all collections
    all_retrieved_data = []
    for collection_name in COLLECTION_NAMES:
        search_results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,  # The vector to search for
            limit=5,  # Number of closest matches to return
        )
    
        # Display the search results for this collection
        print(f"\nResults from {collection_name}:")
        for result in search_results:
            print(f"Found match: {result.payload['data']} with ID {result.id} and distance {result.score}")
        
        # Add results from this collection to overall results
        all_retrieved_data.extend([result.payload['data'] for result in search_results])
    
    # Prepare the combined data for ChatGPT
    context = "\n\n".join(all_retrieved_data)
    
    
    # Query ChatGPT for productivity breakdown
    productivity_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are a data analyst specializing in workforce analytics. Focus on analyzing productivity metrics across different job types and activities."
            },
            {
                "role": "user",
                "content": f"""Here is employee performance data:\n{context}\n\nPlease analyze and provide insights on productivity per hour breakdown by different job types/activities. Include specific numbers and percentages where possible. Only use the data from the associated employee that the user asked about unless specified otherwise."""
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    # Query ChatGPT for time utilization analysis
    time_response = openai_client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {
                "role": "system",
                "content": "You are a data analyst specializing in workforce analytics. Focus on analyzing daily time utilization patterns."
            },
            {
                "role": "user",
                "content": f"""Here is employee performance data:\n{context}\n\nPlease analyze and provide insights on daily time utilization:
    - Average hours worked vs standard workday
    - Unaccounted time periods  
    - Start/end time patterns
    
    Include specific numbers and percentages where possible.Only use the data from the associated employee that the user asked about unless specified otherwise."""
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    # Query ChatGPT for productivity trends
    trends_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a data analyst specializing in workforce analytics. Focus on analyzing productivity trends over time."
            },
            {
                "role": "user",
                "content": f"""Here is employee performance data:\n{context}\n\nPlease analyze and provide insights on productivity trends:
    - Month-over-month changes
    - Any seasonal patterns
    - Notable improvements or declines
    
    Include specific numbers and percentages where possible.Only use the data from the associated employee that the user asked about unless specified otherwise."""
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    # Query ChatGPT for key performance metrics
    metrics_response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a data analyst specializing in workforce analytics. Focus on analyzing key performance metrics."
            },
            {
                "role": "user",
                "content": f"""Here is employee performance data:\n{context}\n\nPlease analyze and provide insights on key performance metrics:
    - Quantity of work completed
    - Task duration patterns  
    - Activity diversity
    
    Include specific numbers and percentages where possible.Only use the data from the associated employee that the user asked about unless specified otherwise."""
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    # Instead of printing, combine all analyses into a single response
    final_response = f"""
### Productivity Analysis
{productivity_response.choices[0].message.content}

### Time Utilization Analysis
{time_response.choices[0].message.content}

### Trends Analysis
{trends_response.choices[0].message.content}

### Metrics Analysis
{metrics_response.choices[0].message.content}
"""
    return final_response


# Test the functionality if run directly
if __name__ == "__main__":
    prompt = "Top 50 performers"
    get_ai_response(prompt)




if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know about employee performance?"):
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display assistant response in chat
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Get AI response using existing function
        response = get_ai_response(prompt)
        
        # Display the response
        response_placeholder.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})



    

