#Import Libraries
import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
import json
import time
import re

#Fill null value to avoid error on parameter 'sciences' of function 'generate_matrix_baseline'
if "options_sciences" not in st.session_state:
    st.session_state.options_sciences = "None"
#Fill null value to avoid error on parameter 'industry' of function 'generate_matrix_baseline'
if "options_industries" not in st.session_state:
    st.session_state.options_industries = "None"
#Fill null value to avoid error on solution's text
if "solutions" not in st.session_state:
    st.session_state.solutions = "None"

#Clean Gemini API Text to create a better UX Writing.
def clean_text(text):
    # Remove special caracters to User could read more easly.
    text = re.sub(r'[^a-zA-Z0-9\s://.;-]', '', text)
    text = text.strip()
    return text

#Generate a table to serve like a 'reasoning' to Gemini. Suggestions of solutions would be based on that.
def generate_matrix_baseline(
        num_col=3, 
        num_rows=3, 
        problem='None', 
        sciences="None", 
        industry="None"
        ):
    
    genai.configure(api_key='AIzaSyDiQBWIfHTto65mCYu0EUxPhlBlfVxBp-I')

    # Using `response_mime_type` with `response_schema` requires a Gemini 1.5 Pro model
    model = genai.GenerativeModel(
      'gemini-1.5-pro'
    )

    prompt = f"""
    Generate {num_col} Critical Functions and {num_rows} Features for each Critical Function of {problem} on {industry}.
    Adapt features of {sciences}. Maximum 3 words.
    Using this Python Dictionary schema:
      {{
        "Crtical Function 01": [List of Features 01],
        "Crtical Function 02": [List of Features 02],
        "Crtical Function 03": [List of Features 03],
        "Crtical Function 04": [List of Features 04],
        "Crtical Function 05": [List of Features 05]
      }}
      Important: the output needs to be in Python Dictionary format. Rename Critical Function with suggestions. Maximum 3 words per description.
    """

    response_prep_01 = model.generate_content(prompt)
    response_prep_02 = response_prep_01.text.strip().replace("\n", "").replace("python", "").replace("```", "")
    st.session_state['table'] = response_prep_02

#Use 'st.session_state['table']' to generate suggestion of solution.
def generate_solutions_baseline(problem="None"):
    genai.configure(api_key='AIzaSyDiQBWIfHTto65mCYu0EUxPhlBlfVxBp-I')

    # Using `response_mime_type` with `response_schema` requires a Gemini 1.5 Pro model
    model = genai.GenerativeModel(
      'gemini-1.5-pro'
    )

    prompt = f"""
    Generate 1 suggestion of solution with data bellow.
    {st.session_state['table']}

    Important: you need to apply morphological analysis. Follow template bellow with maximum 50 words.

    Template of output:
    Problem: {problem}
    Solution: [Title]
    How it works: [explain your morphological analysis. Minimum 300 words to Maximum 700 words]
    References: [Get 3 references from Web to explain how it works. Maximum 10 words. Remove any link]
    - Reference 01:
    - Reference 02:
    - Reference 03:
    """

    response_prep_01 = model.generate_content(prompt)
    response_prep_02 = response_prep_01.text.strip().replace("\n", "").replace("python", "").replace("```", "")
    df_response = response_prep_02
    st.session_state['solutions'] = df_response

with st.sidebar:    
    #Branding Awarenness
    st.header("Franklin.AI")
    #More technical areas to create robust solutions.
    st.session_state.options_science = st.multiselect(
    "Give me your research areas to adapt your product",
    ["Agricultural Technology (AgTech)", "Blockchain Technology", "Biotechnology", 
     "Biomedical Engineering", "Cybersecurity", "Climate Change and Sustainability", 
     "Genomics and Bioinformatics", "Nanotechnology", "Artificial Intelligence and Machine Learning", 
     "Quantum Computing", "Renewable Energy", "Environmental Science", 
     "Astrophysics and Space Exploration", "Materials Science", 
     "Neuroscience", "Robotics", "Pharmaceutical Sciences", "Human-Computer Interaction", 
     "Smart Cities and Urban Planning", "Energy Storage Technologies"]
    )

    st.session_state.options_industries = st.multiselect(
    "What industry is related to your product?",
    ["E-commerce", "Education Technology (EdTech)", "Tourism and Hospitality", "Fintech", "Supply Chain Management", 
     "Supply Chain Management", "Healthcare Management", "Marketing Technology (MarTech)", 
     "Human Resources Tech (HRTech)", "Real Estate Technology (PropTech)", 
     "Agriculture", "Food Tech", "Entertainment and Media", "Cybersecurity", "Insurance Technology (InsurTech)",
     "Gaming and eSports", "Waste Management", 'Fitness and Wellness']
    )

    def first_matrix():
        #Step 01: generate strutured reasoning.
        generate_matrix_baseline(
            num_col=5, 
            num_rows=5, 
            problem=st.session_state.input,
            sciences=st.session_state.options_science, 
            industry=st.session_state.options_industries
            )
        #Step 02: generate a text with more meaningful solutions
        generate_solutions_baseline(problem=st.session_state.input)

    input = st.text_input('What is the main problem to solve?', 
                          key='input', placeholder='eg. Segmentation of Leads to receive Credit')
    
    button_generate = st.button("Generate new solution", type="primary", on_click=first_matrix)

with st.container(border=True):
    solutions = st.session_state.solutions
    if "None" in st.session_state.solutions:
        st.header("Empowering innovation teams with rapid idea generation for breakthrough solutions.", divider=True)
        st.subheader("Instructions:")
        st.text("you need to fill:")
        st.text("1: research areas related to the product.")
        st.text("2: industry is related to your product.")
        st.text("3: context (theme/problem/constraints) to generate great suggestions.")

    if "None" != st.session_state.solutions:

        header = clean_text(solutions.split('Problem:')[1].split("How it works:")[0].split("Solution:")[0])

        subheader = clean_text(solutions.split('Problem:')[1].split("How it works:")[0].split("Solution:")[1])

        st.header("Problem: " + header, divider=True)
        st.subheader("Solution: " + subheader, divider=True)

        text = clean_text(solutions.split('Problem:')[1].split("How it works:")[1].split("- Reference 01:")[0].replace("References:", ""))
        st.write(text)

        st.text("Search References:")

        references = [i.strip() for i in clean_text(solutions.split('- Reference 01:')[1]).split('- ') if i!=""]

        st.write(references[0])
        st.write(references[1].replace("Reference 02:", ""))
        st.write(references[2].replace("Reference 03:", ""))
