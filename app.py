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
# PAGE 2: WHAT TO EXPECT (Cinematic Parallax)
# ==========================================
elif page == "📖 What to Expect":
    st.markdown("""
        <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header {visibility: hidden;} footer {visibility: hidden;}

        .parallax {
            background-attachment: fixed; background-position: center;
            background-repeat: no-repeat; background-size: cover;
            min-height: 100vh; display: flex; align-items: center;
            justify-content: center; position: relative; padding: 50px 20px;
        }
        .overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75); z-index: 1;
        }
        .content {
            position: relative; z-index: 2; text-align: center; color: white; max-width: 1000px;
        }
        .apple-title { font-size: 4.5rem; font-weight: 700; letter-spacing: -0.05rem; line-height: 1.1; margin-bottom: 20px; text-shadow: 2px 2px 10px rgba(0,0,0,0.8);}
        .apple-subtitle { font-size: 1.8rem; font-weight: 500; color: #0071e3; margin-bottom: 20px; text-shadow: 1px 1px 5px rgba(0,0,0,0.8);}
        .apple-body { font-size: 1.2rem; font-weight: 300; line-height: 1.6; color: #e5e5ea; text-shadow: 1px 1px 5px rgba(0,0,0,0.8); margin-bottom: 30px;}
        
        .grid-container {
            display: grid; grid-template-columns: 1fr 1fr; gap: 40px; text-align: left; margin-top: 30px;
        }
        @media (max-width: 768px) {
            .grid-container { grid-template-columns: 1fr; }
            .apple-title { font-size: 3rem; }
        }
        .grid-box {
            background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px);
        }
        .grid-title { font-size: 1.5rem; font-weight: 600; color: #fff; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # 1. HERO SECTION
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay" style="background: rgba(0,0,0,0.6);"></div>
            <div class="content">
                <div class="apple-title">Radiotherapy. Demystified.</div>
                <div class="apple-subtitle">Profound precision. Designed for your healing.</div>
                <div class="apple-body">Scroll down to explore the technology and workflow behind your treatment.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. SIMULATION & IMMOBILIZATION
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 1: The Blueprint</div>
                <div class="apple-title">Locked in. Comfortably.</div>
                <div class="apple-body">Before treatment, we map your anatomy using advanced PCCT, MR, or PET/CT simulators. To ensure millimeter-perfect accuracy every single day, we use custom immobilization devices tailored to your specific treatment site:</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">👤 Head & Neck</div>
                        <div class="apple-body" style="margin-bottom:0;">A warm, mesh-like <b>Thermoplastic Mask</b> is gently molded over your face and shoulders. It hardens in minutes, keeping you perfectly still—crucial for treating areas near critical structures.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🫁 Breast & Thorax</div>
                        <div class="apple-body" style="margin-bottom:0;">You will rest on an angled <b>Breast Board</b> or Wing Board with your arms raised comfortably above your head, exposing the chest and protecting your lungs.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🧍 Pelvis & Prostate</div>
                        <div class="apple-body" style="margin-bottom:0;">A <b>Vac-Lok Cushion</b> (a vacuum-sealed beanbag) molds exactly to your lower body, ensuring absolute stability for your legs and pelvis.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 3. THE MACHINES (LINAC vs TOMO)
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 2: The Arsenal</div>
                <div class="apple-title">The right tool for the exact target.</div>
                <div class="apple-body">Depending on your treatment plan, our clinical team will select the most advanced delivery system available to target the tumor while sparing healthy tissue.</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">🎯 Linear Accelerator (Linac)</div>
                        <div class="apple-body" style="margin-bottom:0;"><b>The Workhorse.</b> The Linac is an open, rotating arm that moves seamlessly around you. It uses advanced techniques like VMAT to sculpt radiation beams to the 3D shape of the tumor in just a few minutes. Fast, highly versatile, and used for the majority of treatments.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🌀 TomoTherapy</div>
                        <div class="apple-body" style="margin-bottom:0;"><b>The Spiral Specialist.</b> Designed to look like a CT scanner, TomoTherapy delivers radiation slice-by-slice in a continuous 360-degree spiral. It provides unmatched conformal dose distribution, making it exceptionally powerful for complex, large, or hard-to-reach tumors.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
