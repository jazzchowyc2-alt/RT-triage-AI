import streamlit as st
from openai import OpenAI

# 1. Setup the web page (Must be the first command)
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑", layout="centered")

# 2. Navigation Sidebar
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to:", ["💬 Triage Assistant", "📖 What to Expect"])
    st.markdown("---")

# ==========================================
# PAGE 1: THE TRIAGE ASSISTANT (Your existing code)
# ==========================================
if page == "💬 Triage Assistant":
    st.title("🚑 「幫緊你幫緊你」Symptom Translator")
    st.caption("你講白話，AI 幫你轉做專業 Clinical Notes (CTCAE Grading).")

    api_key = st.secrets["OPENROUTER_API_KEY"]

    with st.sidebar:
        st.header("📋 Patient File")
        treatment_site = st.selectbox(
            "Select Radiotherapy Site:", 
            ["Not selected", "Head & Neck (e.g., NPC)", "Breast", "Thorax (Lung/Esophagus)", "Pelvis (Prostate/Rectum/Gynae)", "Other"]
        )

    system_prompt = """You are a compassionate radiation oncology triage assistant in a Hong Kong hospital.
    You MUST output your response EXACTLY following this template. Do not skip any sections. 

    CRITICAL RULES:
    1. RED FLAG SAFETY: If the symptom is severe or life-threatening (e.g., heavy bleeding, fever >38.5°C, severe chest pain, unable to swallow, severe skin ulceration), you MUST explicitly instruct the patient to go to the A&E (急症室) or contact the oncology ward immediately.
    2. ANATOMICAL LOGIC: If the symptom is anatomically impossible for the selected Treatment Site, you MUST state clearly that this symptom is likely unrelated to their radiotherapy, but they should still seek medical attention.
    3. CANTONESE TONE: Speak in highly natural, empathetic Hong Kong Cantonese.

    ### 🗣️ 姑娘/師兄話你知 (Message to Patient)
    [Write in natural Hong Kong Cantonese. Warmly validate their discomfort. State clearly if the symptom matches their treatment site or if it requires emergency A&E attention.]

    ### ✅ 可以咁做 (Do's)
    - [Cantonese: Actionable tip 1]
    - [Cantonese: Actionable tip 2]

    ### ❌ 盡量避免 (Don'ts)
    - [Cantonese: Actionable tip 1]
    - [Cantonese: Actionable tip 2]

    ### 📋 Clinical Note & CTCAE Grading
    **Clinical Note:** [Write exactly 1 brief English sentence summarizing the patient's symptom and ASSIGNING a single estimated CTCAE grade.]
    """

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": system_prompt}]

    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_input := st.chat_input("How are you feeling today? (e.g., '我肚屙得好犀利呀')"):
        if treatment_site == "Not selected":
            st.warning("⚠️ Please select your Treatment Site in the sidebar before messaging us.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            strict_reminder = f"""Patient's symptom: {user_input}\nPatient's Treatment Site: {treatment_site}\n[SYSTEM REMINDER: Check anatomical logic and output strict template.]"""
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

# ==========================================
# PAGE 2: WHAT TO EXPECT (The "Apple" Page)
# ==========================================
elif page == "📖 What to Expect":
    # Custom CSS to mimic Apple's clean, centered typography
    st.markdown("""
        <style>
        .apple-title { text-align: center; font-size: 3.5rem; font-weight: 700; margin-bottom: 0px; padding-bottom: 0px; letter-spacing: -0.05rem;}
        .apple-subtitle { text-align: center; font-size: 1.5rem; color: #86868b; font-weight: 400; margin-top: 5px; margin-bottom: 50px;}
        .section-header { font-size: 2rem; font-weight: 600; margin-bottom: 10px; }
        .section-text { font-size: 1.1rem; color: #555555; line-height: 1.6; }
        </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown('<p class="apple-title">Radiotherapy. Demystified.</p>', unsafe_allow_html=True)
    st.markdown('<p class="apple-subtitle">Profound precision. Designed for your healing.</p>', unsafe_allow_html=True)
    
    st.image("https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=2000", caption="The Journey Ahead", use_container_width=True)
    st.write("---")

    # Section 1: Simulation (Text Left, Image Right)
    col1, col2 = st.columns([1.2, 1], gap="large")
    with col1:
        st.markdown('<p class="section-header">1. The Blueprint (Simulation)</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-text">Before treatment begins, we create a flawless map of your anatomy. Depending on your specific needs, we utilize advanced simulators—such as Photon-Counting CT (PCCT), MR, or PET/CT—to capture high-resolution, multi-dimensional imagery.</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-text">You will lie still while a custom immobilization device (like a thermoplastic mask) is gently molded to your body. This ensures millimeter-perfect accuracy every single day.</p>', unsafe_allow_html=True)
    with col2:
        # Placeholder for a sleek CT scanner image
        st.image("https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=800", use_container_width=True)

    st.write("\n\n<br><br>", unsafe_allow_html=True)

    # Section 2: Planning (Image Left, Text Right)
    col3, col4 = st.columns([1, 1.2], gap="large")
    with col3:
         # Placeholder for a computer/planning image
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=800", use_container_width=True)
    with col4:
        st.markdown('<p class="section-header">2. The Invisible Math (Planning)</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-text">Behind the scenes, clinical oncologists and dosimetrists construct a highly customized algorithm. We calculate the exact trajectory of the radiation beams to maximize impact on the target area while strictly protecting surrounding healthy tissues.</p>', unsafe_allow_html=True)

    st.write("\n\n<br><br>", unsafe_allow_html=True)

    # Section 3: Treatment (Text Left, Image Right)
    col5, col6 = st.columns([1.2, 1], gap="large")
    with col5:
        st.markdown('<p class="section-header">3. The Routine (Daily Treatment)</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-text">When you enter the Linear Accelerator (Linac) room, the therapists will align you precisely to your setup marks. The actual treatment takes only a few minutes.</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-text"><b>It is completely invisible and painless.</b> You will hear a loud buzzing sound as the machine rotates around you. While the staff leaves the room during delivery, they monitor you closely via cameras and can hear you at all times.</p>', unsafe_allow_html=True)
    with col6:
        st.image("https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=800", use_container_width=True)
