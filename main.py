import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st


load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

system_instruction = '''

Who are you:
    Immerse yourself as Hitesh Choudhary a teacher by profession. You teach coding to various level of students, right from beginners to folks who are already writing great softwares. You have been teaching on for more than 10 years now and it is your passion to teach people coding. It's a great feeling when you teach someone and they get a job or build something on their own.
    In past, You have worked with many companies and on various roles such as Cyber Security related roles, iOS developer, Tech consultant, Backend Developer, Content Creator, CTO and these days, You are at full time Founder and teacher at Chai Aur Code. You have done my fair share of startup too, your last Startup was LearnCodeOnline where we served 350,000+ user with various courses.

More about yourself:
    Hitesh Choudhary has established himself as a significant figure in online programming education through his comprehensive approach to content creation, community building, and platform development. His Chai aur Code initiative demonstrates the effectiveness of combining accessible teaching methodologies with practical, project-based learning experiences. The platform's growth from a single YouTube channel to a multi-platform educational ecosystem reflects both market demand and Choudhary's strategic vision for democratizing programming education.

    Follow the steps in sequence that is "analyse", "think", "output", "validate" and finally "result".

    Rules:
    1. Follow the strict JSON output as per schema 
    2. Always perform one step at a time and wait for the next input.
    3. Carefully analyse the user query and give full answer at last.

    Output Format:
    {{ "step": "string", "content": "string" }}


Examples:

1.Hello Sir, How are you ?
Ans: I am fine, thankyou. How about you? 

2.
Student: Sir, I think i am slow in coding.
Hitesh: Don't compare focus on understanding the basics of coding and work hard.

3.
Student: Sir, DSA or development? i am confused.
Hitesh: Good question, DSA and Development both are good. Keep balanced in your study.

4.
Student: Sir, I see YouTube in it your videos.
Hitesh: You see, only seeing videos on youtube will not work, you need to practice it.


'''


messages = [
    {'role': 'user', 'parts': [system_instruction]},
]

chat = model.start_chat(history=messages)


def get_gemini_response(prompt):
    thinking = []

    query = prompt
    messages.append({'role': 'user', 'parts': query})

    while True:

        response = chat.send_message(query)
        raw_text = response.text.strip()

        if raw_text.startswith('```json') and raw_text.endswith('```'):
            json_str = raw_text[len('```json'): -3].strip()
        else:
            json_str = raw_text

        try:
            parsed_json = json.loads(json_str)
            messages.append({'role': 'model', 'parts': parsed_json['content']})

            if parsed_json.get('step') != 'result':
                thinking.append(f"{parsed_json.get("content")}")
                # print(f"{parsed_json.get("content")}")
                continue

            result = parsed_json.get("content")
            return thinking, result
            # break

        except json.JSONDecoderError as e:
            print('Failed to pars JSON:', e)
            return 'Failed to parse JSON'



# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'pending_prompt' not in st.session_state:
    st.session_state.pending_prompt = None

if 'thinking_steps' not in st.session_state:
    st.session_state.thinking_steps = []

# Layout with two columns: Chat (left), Thinking steps (right)
col_chat, col_thinking = st.columns([4, 1])


# Chat area
with col_chat:
    # Show chat messages
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            c1, c2 = st.columns([1, 9])
            with c1:
                st.image("images/user.png", width=64)
            with c2:
                st.markdown(f'<div class="message-bubble user-bubble">{msg["parts"]}</div>', unsafe_allow_html=True)
        else:
            c1, c2 = st.columns([9, 1])
            with c1:
                st.markdown(f'<div class="message-bubble bot-bubble">{msg["parts"]}</div>', unsafe_allow_html=True)
            with c2:
                st.image("images/hitesh.png", width=64)

    # Input box for new prompt
    prompt = st.chat_input("Ask anything to sir...")

    if prompt:
        st.session_state.messages.append({'role': 'user', 'parts': prompt})
        st.session_state.pending_prompt = prompt
        st.session_state.thinking_steps = []  # Clear previous thinking steps
        st.rerun()

    # Show typing indicator and get response
    if st.session_state.pending_prompt:
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<div class="message-bubble bot-bubble">hitesh is typing<span class="dots"></span></div>',
            unsafe_allow_html=True
        )

        # Call backend to get thinking steps and final answer
        thinking, response = get_gemini_response(st.session_state.pending_prompt)

        typing_placeholder.empty()  # Remove typing indicator

        # Save thinking steps and final response
        st.session_state.thinking_steps = thinking
        st.session_state.messages.append({'role': 'model', 'parts': response})
        st.session_state.pending_prompt = None
        st.rerun()

# Thinking steps area
with col_thinking:
    st.markdown("### Model's Thought Process")
    if st.session_state.thinking_steps:
        for step in st.session_state.thinking_steps:
            st.markdown(f"- {step}")
    else:
        st.markdown("_Thinking steps will appear here..._")
