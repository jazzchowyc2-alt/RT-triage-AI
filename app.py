import streamlit as st
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑", layout="centered")

# 2. Navigation Sidebar
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to:", ["💬 Triage Assistant", "📖 What to Expect"])
    st.markdown("---")

# ==========================================
# PAGE 1: THE TRIAGE ASSISTANT
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
# PAGE 2: WHAT TO EXPECT (Native Streamlit Layout)
# ==========================================
elif page == "📖 What to Expect":
    
    # Clean, native typography sizing
    st.markdown("""
        <style>
        .title-text { font-size: 3.5rem; font-weight: 700; text-align: center; margin-bottom: 0; line-height: 1.2; }
        .subtitle-text { font-size: 1.5rem; font-weight: 500; text-align: center; color: #0071e3; margin-bottom: 40px; }
        .section-header { font-size: 2.5rem; font-weight: 600; margin-top: 50px; margin-bottom: 10px; }
        .body-text { font-size: 1.1rem; line-height: 1.6; color: #d2d2d7; margin-bottom: 20px;}
        </style>
    """, unsafe_allow_html=True)

    # --- HERO SECTION ---
    st.markdown('<p class="title-text">Radiotherapy.<br>Demystified.</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle-text">Profound precision. Designed for your healing.</p>', unsafe_allow_html=True)
    
    # Hero Image
    st.image("image/Radiotherapist.png", use_container_width=True)
    st.divider()

    # --- STEP 1: SIMULATION ---
    st.markdown('<p class="section-header">Step 1: The Blueprint</p>', unsafe_allow_html=True)
    st.markdown('<p class="body-text">Before treatment, we map your anatomy using advanced simulators. To ensure millimeter-perfect accuracy, we use custom immobilization devices tailored to you.</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("👤 Head & Neck")
        st.write("A warm, mesh-like Thermoplastic Mask is molded over your face and shoulders. It hardens in minutes, keeping you perfectly still.")
    with col2:
        st.subheader("🫁 Breast & Thorax")
        st.write("You will rest on a customized Breast/Wing Board with your arms safely positioned above your head, exposing the treatment area.")
    with col3:
        st.subheader("🧍 Pelvis")
        st.write("A Vac-Lok Cushion (a vacuum beanbag) molds exactly to your lower body, ensuring absolute stability for your legs and pelvis.")

    # Simulation Image
    st.image("image/Simulation.png", caption="Radiation Therapy Simulation & Setup", use_container_width=True)
    st.divider()

    # --- STEP 2: PLANNING ---
    st.markdown('<p class="section-header">Step 2: The Algorithm</p>', unsafe_allow_html=True)
    st.markdown('<p class="body-text">Behind the scenes, your clinical oncologists and dosimetrists construct a highly customized 3D plan.</p>', unsafe_allow_html=True)
    
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("🎯 Contouring")
        st.write("Doctors meticulously draw exact boundaries on your scans, separating the target tumor volume from the critical organs nearby.")
    with col5:
        st.subheader("📐 Dosimetry")
        st.write("Using supercomputers, we calculate the exact angles, intensity, and shape of the radiation beams to maximize tumor destruction while shielding healthy tissue.")

    # Planning Image
    st.image("image/Planning.png", caption="Treatment Planning System", use_container_width=True)
    st.divider()

    # --- STEP 3: VERIFICATION ---
    st.markdown('<p class="section-header">Step 3: Verification</p>', unsafe_allow_html=True)
    st.markdown('<p class="body-text">Before the treatment beam even turns on, we perform a vital safety check right inside the treatment room using Image-Guided Precision.</p>', unsafe_allow_html=True)
    
    # Verification/CBCT Image
    st.image("image/CBCT.png", caption="Daily Image Guidance", use_container_width=True)
    st.divider()

    # --- STEP 4: TREATMENT ---
    st.markdown('<p class="section-header">Step 4: The Treatment</p>', unsafe_allow_html=True)
    st.markdown('<p class="body-text">You will not feel, see, or smell the radiation. It is completely painless. Depending on your specific plan, we use one of our advanced delivery systems:</p>', unsafe_allow_html=True)
    
    col6, col7 = st.columns(2)
    with col6:
        st.subheader("🚀 Linear Accelerator (Linac)")
        st.write("The open, rotating arm moves seamlessly around you. Using VMAT technology, it sculpts radiation beams to the 3D shape of the tumor in just a few minutes.")
    with col7:
        st.subheader("🌀 TomoTherapy")
        st.write("Delivering radiation slice-by-slice in a continuous 360-degree spiral. It provides unmatched conformal dose distribution for complex treatment areas.")

    # Treatment Machine Image
    st.image("image/tomo.png", caption="Advanced Delivery Systems", use_container_width=True)
