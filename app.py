import streamlit as st
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑")
st.title("🚑 「幫緊你幫緊你」Symptom Translator")
st.caption("你講白話，AI 幫你轉做專業 Clinical Notes (CTCAE Grading).")

# 2. Setup the sidebar for the API Key
with st.sidebar:
    st.header("App Setup")
    api_key = st.text_input("Enter your OpenRouter API Key:", type="password")
    st.markdown("Get your free API key at [openrouter.ai](https://openrouter.ai/)")


# 3. The Clinical Prompt (Strict Template Edition)
system_prompt = """You are a compassionate radiation oncology triage assistant in a Hong Kong hospital.
You MUST output your response EXACTLY following this template. Do not skip any sections. 

### 🗣️ 姑娘/師兄話你知 (Message to Patient)
[Write in Cantonese/Chinglish. Warmly validate their discomfort. 
IMPORTANT: If they haven't mentioned their radiation treatment site (e.g., breast, pelvis, head & neck), ask them here. If the symptom doesn't logically match the site, gently explain that it might be a separate illness.]

### ✅ 可以咁做 (Do's)
- [Cantonese: Actionable tip 1]
- [Cantonese: Actionable tip 2]

### ❌ 盡量避免 (Don'ts)
- [Cantonese: Actionable tip 1]
- [Cantonese: Actionable tip 2]

### 📋 CTCAE Severity Reference (For RT Only)
| Grade | Clinical Description |
|---|---|
| 1 | Mild symptoms; intervention not indicated |
| 2 | Moderate symptoms; medical intervention indicated |
| 3 | Severe symptoms; tube feeding, TPN, or hospitalization indicated |
| 4 | Life-threatening consequences |

**Clinical Note:** [Write 1 brief English sentence summarizing the symptom and estimating the current CTCAE grade for the Radiation Therapist.]
"""

# 4. Memory Setup
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# 5. Display existing conversation
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 6. Handle user input
if user_input := st.chat_input("How are you feeling today? (e.g., 'My mouth is so dry...')"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar first!")
    else:
        # 1. Save and show the normal user message on the screen
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Connect to OpenRouter API
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # 2. SECRET INJECTION: We secretly attach the template rules to the user's prompt 
        # so it's the very last thing the AI reads before generating a response.
        strict_reminder = f"""{user_input}
        
        [SYSTEM REMINDER: You MUST use the exact template:
        1. 🗣️ 姑娘/師兄話你知 (Cantonese empathy + ask about treatment site if missing)
        2. ✅ 可以咁做 (Cantonese Do's)
        3. ❌ 盡量避免 (Cantonese Don'ts)
        4. 📋 CTCAE Severity Reference (English Table + Clinical Note)]"""
        
        # Create a temporary message list just for the AI's eyes
        api_messages = st.session_state.messages[:-1] + [{"role": "user", "content": strict_reminder}]
        
        with st.chat_message("assistant"):
            # Using a specific model known for excellent Chinese and formatting
            response = client.chat.completions.create(
                model="openrouter/free", 
                messages=api_messages,
                temperature=0.2 # Lowered temperature to force stricter formatting
            )
            bot_reply = response.choices[0].message.content
            st.markdown(bot_reply)
        
        # 3. Save AI reply to history
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})