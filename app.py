import streamlit as st
import base64
import os
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑", layout="centered")

# --- HELPER FUNCTION FOR CINEMATIC IMAGES ---
@st.cache_data
def get_base64_of_bin_file(bin_file):
    """Reads a local image and converts it to base64 so CSS can use it as a background."""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        # Failsafe just in case the image hasn't loaded yet
        return ""

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
# PAGE 2: WHAT TO EXPECT (Cinematic Scroll)
# ==========================================
elif page == "📖 What to Expect":
    
    # Pre-load the images into base64 format for CSS
    img_hero = get_base64_of_bin_file("image/Radiotherapist.png")
    img_sim = get_base64_of_bin_file("image/Simulation.png")
    img_plan = get_base64_of_bin_file("image/Planning.png")
    img_treat = get_base64_of_bin_file("image/tomo.png")

    # Injecting massive custom CSS to override Streamlit's default layout
    # Notice the background-image URLs are dynamically injecting your local photos
    st.markdown(f"""
        <style>
        /* Force edge-to-edge layout */
        .block-container {{
            padding: 0rem !important;
            max-width: 100% !important;
        }}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}

        /* The Parallax Magic */
        .parallax-hero {{ background-image: url("data:image/png;base64,{img_hero}"); }}
        .parallax-sim {{ background-image: url("data:image/png;base64,{img_sim}"); }}
        .parallax-plan {{ background-image: url("data:image/png;base64,{img_plan}"); }}
        .parallax-treat {{ background-image: url("data:image/png;base64,{img_treat}"); }}

        .parallax-section {{
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            padding: 40px 20px;
        }}

        /* Dark overlay for readability */
        .overlay {{
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            z-index: 1;
        }}

        /* Apple-style typography */
        .content {{
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
            padding: 20px;
            max-width: 1000px;
        }}
        .apple-title {{ font-size: 4.5rem; font-weight: 700; letter-spacing: -0.05rem; line-height: 1.1; margin-bottom: 20px; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
        .apple-subtitle {{ font-size: 1.8rem; font-weight: 600; color: #0071e3; margin-bottom: 20px; text-shadow: 1px 1px 5px rgba(0,0,0,0.8); }}
        .apple-body {{ font-size: 1.25rem; font-weight: 300; line-height: 1.6; color: #f5f5f7; text-shadow: 1px 1px 5px rgba(0,0,0,0.8); margin-bottom: 30px; }}
        
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; text-align: left; margin-top: 40px; }}
        .grid-box {{ background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); }}
        .grid-title {{ font-size: 1.4rem; font-weight: 600; color: #fff; margin-bottom: 15px; }}
        .grid-text {{ font-size: 1.1rem; color: #d2d2d7; line-height: 1.5; }}
        
        @media (max-width: 768px) {{ .apple-title {{ font-size: 3rem; }} }}
        </style>
    """, unsafe_allow_html=True)

    # HERO SECTION
    st.markdown("""
        <div class="parallax-section parallax-hero">
            <div class="overlay" style="background: rgba(0,0,0,0.5);"></div>
            <div class="content">
                <div class="apple-title">Radiotherapy.<br>Demystified.</div>
                <div class="apple-subtitle">Profound precision. Designed for your healing.</div>
                <div class="apple-body">Scroll down to explore your journey.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # SIMULATION SECTION
    st.markdown("""
        <div class="parallax-section parallax-sim">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 1: The Blueprint</div>
                <div class="apple-title">Locked in. Comfortably.</div>
                <div class="apple-body">Before treatment begins, we map your anatomy using advanced simulators. To ensure millimeter-perfect accuracy, we use custom immobilization devices.</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">👤 Head & Neck</div>
                        <div class="grid-text">A warm, mesh-like <b>Thermoplastic Mask</b> is molded over your face and shoulders. It hardens in minutes, keeping you perfectly still.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🫁 Breast & Thorax</div>
                        <div class="grid-text">You will rest on a <b>Breast/Wing Board</b> with arms raised above your head, exposing the chest and stabilizing the lungs.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🧍 Pelvis & Prostate</div>
                        <div class="grid-text">A <b>Vac-Lok Cushion</b> (a vacuum beanbag) molds exactly to your lower body, ensuring absolute stability for your legs and pelvis.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # PLANNING SECTION
    st.markdown("""
        <div class="parallax-section parallax-plan">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 2: The Algorithm</div>
                <div class="apple-title">Invisible math. Maximum impact.</div>
                <div class="apple-body">Behind the scenes, clinical oncologists and dosimetrists construct a highly customized 3D plan using powerful computers.</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">🎯 Contouring</div>
                        <div class="grid-text">Doctors meticulously draw exact boundaries on your scans, separating the target tumor volume from critical healthy organs nearby.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">📐 Dosimetry</div>
                        <div class="grid-text">We calculate the exact angles, intensity, and shape of the radiation beams to maximize tumor destruction while shielding healthy tissue.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # TREATMENT SECTION
    st.markdown("""
        <div class="parallax-section parallax-treat">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 3: The Treatment</div>
                <div class="apple-title">Painless. Precise.</div>
                <div class="apple-body">You will not feel, see, or smell the radiation. Depending on your plan, we use one of our advanced delivery systems:</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">🚀 Linear Accelerator (Linac)</div>
                        <div class="grid-text"><b>The Workhorse.</b> The open, rotating arm moves seamlessly around you. It sculpts radiation beams to the 3D shape of the tumor in just a few minutes.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🌀 TomoTherapy</div>
                        <div class="grid-text"><b>The Spiral Specialist.</b> Delivering radiation slice-by-slice in a continuous 360-degree spiral. Unmatched precision for complex treatment areas.</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
