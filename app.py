import streamlit as st
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑")
st.title("🚑 「幫緊你幫緊你」Symptom Translator")
st.caption("你講白話，AI 幫你轉做專業 Clinical Notes (CTCAE Grading).")

# 2. Securely load the API Key from Streamlit Secrets (Invisible to users!)
api_key = st.secrets["OPENROUTER_API_KEY"]

# 3. Setup the sidebar for Patient Info ONLY
with st.sidebar:
    st.header("📋 Patient File")
    treatment_site = st.selectbox(
        "Select Radiotherapy Site:", 
        ["Not selected", "Head & Neck (e.g., NPC)", "Breast", "Thorax (Lung/Esophagus)", "Pelvis (Prostate/Rectum/Gynae)", "Other"]
    )

# 4. The Clinical Prompt
system_prompt = """You are a compassionate radiation oncology triage assistant in a Hong Kong hospital.
You MUST output your response EXACTLY following this template. Do not skip any sections. 

### 🗣️ 姑娘/師兄話你知 (Message to Patient)
[Write in Cantonese/Chinglish. Warmly validate their discomfort. 
CLINICAL LOGIC CHECK: Look at their Treatment Site. If the symptom is anatomically impossible to be caused by RT to that site (like diarrhea for an NPC patient), gently explain that it is likely a separate issue but they should still take care.]

### ✅ 可以咁做 (Do's)
- [Cantonese: Actionable tip 1]
- [Cantonese: Actionable tip 2]

### ❌ 盡量避免 (Don'ts)
- [Cantonese: Actionable tip 1]
- [Cantonese: Actionable tip 2]

### 📋 CTCAE Severity Reference (For RT Only)
| Grade | Clinical Description |
|---|---|
| [Insert Grade Number] | [Insert exact CTCAE description] |

**Clinical Note:** [Write 1 brief English sentence summarizing the symptom and estimating the current CTCAE grade for the Radiation Therapist.]
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. Handle user input
if user_input := st.chat_input("How are you feeling today? (e.g., '我肚屙得好犀利呀')"):
    if treatment_site == "Not selected":
        st.warning("⚠️ Please select your Treatment Site in the sidebar before messaging us. You may choose it by pressing the >> at left upper corner.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        strict_reminder = f"""Patient's symptom: {user_input}
        Patient's Treatment Site: {treatment_site}
        
        [SYSTEM REMINDER: You MUST use the exact template. You MUST check if the symptom makes anatomical sense for the {treatment_site} treatment site. If it does NOT make sense, point it out in the 🗣️ section in Cantonese.]"""
        
        api_messages = st.session_state.messages[:-1] + [{"role": "user", "content": strict_reminder}]
        
        with st.chat_message("assistant"):
           response = client.chat.completions.create(
                model="google/gemini-2.0-flash-lite-preview-02-05:free", 
                messages=api_messages,
                temperature=0.2
            )
            bot_reply = response.choices[0].message.content
            st.markdown(bot_reply)
        
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
