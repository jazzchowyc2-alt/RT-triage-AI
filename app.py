import streamlit as st
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑")
st.title("🚑 「幫緊你幫緊你」Symptom Translator")
st.caption("你講白話，AI 幫你轉做專業 Clinical Notes (CTCAE Grading).")

# 2. Securely load the API Key from Streamlit Secrets
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

CRITICAL RULES:
1. RED FLAG SAFETY: If the symptom is severe or life-threatening (e.g., heavy bleeding, fever >38.5°C, severe chest pain, unable to swallow, severe skin ulceration), you MUST explicitly instruct the patient to go to the A&E (急症室) or contact the oncology ward immediately.
2. ANATOMICAL LOGIC: If the symptom is anatomically impossible for the selected Treatment Site (e.g., coughing blood for Pelvic RT, or diarrhea for Head & Neck RT), you MUST state clearly that this symptom is likely unrelated to their radiotherapy, but they should still seek medical attention.
3. CANTONESE TONE: Speak in highly natural, empathetic Hong Kong Cantonese (e.g., "明白你依家好辛苦...", "唔好太擔心..."). Avoid awkward, grammatically incorrect, or robotic translations.

### 🗣️ 姑娘/師兄話你知 (Message to Patient)
[Write in natural Hong Kong Cantonese. Warmly validate their discomfort. State clearly if the symptom matches their treatment site or if it requires emergency A&E attention.]

### ✅ 可以咁做 (Do's)
- [Cantonese: Actionable tip 1]
- [Cantonese: Actionable tip 2]

### ❌ 盡量避免 (Don'ts)
- [Cantonese: Actionable tip 1]
- [Cantonese: Actionable tip 2]

### 📋 Clinical Note & CTCAE Grading
**Clinical Note:** [Write exactly 1 brief English sentence summarizing the patient's symptom and ASSIGNING a single estimated CTCAE grade based on the latest criteria (e.g., "Patient reports severe throat pain and inability to swallow solids; estimated as Grade 3 dysphagia/mucositis.").]
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
            try:
                response = client.chat.completions.create(
                    model="openrouter/free", 
                    messages=api_messages,
                    temperature=0.2 
                )
                bot_reply = response.choices[0].message.content
                st.markdown(bot_reply)
                
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            except Exception as e:
                st.error(f"⚠️ API Error: {e}")
