import streamlit as st

st.title("Steraflow Model Demo")

st.markdown("""
    :red-background[This demo contains sensitive information so please do not share it with anyone.]
""")


st.markdown("### Introduction to Steraflow Time-Aware RAG Model")
st.markdown("""
    The Steraflow model implements **Time-Aware Retrieval Augmented Generation (RAG)** to analyze 
    workforce productivity data. Our system processes and vectorizes temporal data to provide 
    detailed insights into associate performance and time utilization.
""")

st.markdown("### Data Processing & Analysis Capabilities")
st.markdown("""
    Our model specifically focuses on three key areas:
    
    1. **Associate Productivity Metrics**
    - Hourly productivity rates broken down by job type
    - Performance comparisons across different tasks
    - Efficiency tracking over time
    
    2. **Time Utilization Analysis**
    - Daily time accounting for each associate
    - Identification of gaps in time tracking
    - Breakdown of productive vs. unaccounted time
    
    3. **Trend Analysis**
    - Historical productivity patterns
    - Performance change indicators
    - Seasonal or temporal variations in efficiency
""")

st.markdown("### How It Works")
st.markdown("""
    The system processes your workforce data through our specialized vectorization pipeline, 
    enabling temporal-aware analysis that maintains chronological context while identifying 
    patterns and anomalies in productivity metrics.
""")

st.markdown("### Side note")
st.markdown("""
    We are currently running this with our own limited funds as **college students** so please 
    be patient with the latency and if we run out of queries, please let us know. 
""")
