import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑", layout="wide")

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
    
    # We use st.components.v1.html to create a true HTML/CSS environment. 
    # High-quality Unsplash medical tech URLs are used because they bypass Streamlit blocking.
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #000; }
        .parallax {
            background-attachment: fixed; background-position: center;
            background-repeat: no-repeat; background-size: cover;
            min-height: 100vh; display: flex; align-items: center;
            justify-content: center; position: relative; padding: 60px 20px;
        }
        .overlay {
            position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75); z-index: 1;
        }
        .content {
            position: relative; z-index: 2; text-align: center; color: white; max-width: 1000px; width: 100%;
        }
        .apple-title { font-size: 4.5rem; font-weight: 700; letter-spacing: -0.05rem; line-height: 1.1; margin-bottom: 20px; text-shadow: 2px 2px 10px rgba(0,0,0,0.8);}
        .apple-subtitle { font-size: 1.5rem; font-weight: 600; color: #2997ff; margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.1rem;}
        .apple-body { font-size: 1.25rem; font-weight: 300; line-height: 1.6; color: #f5f5f7; text-shadow: 1px 1px 5px rgba(0,0,0,0.8); margin-bottom: 30px;}
        
        .grid-container {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; text-align: left; margin-top: 40px;
        }
        .grid-box {
            background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .grid-title { font-size: 1.4rem; font-weight: 600; color: #fff; margin-bottom: 15px; }
        .grid-text { font-size: 1.1rem; color: #d2d2d7; line-height: 1.5; }
        
        @media (max-width: 768px) {
            .apple-title { font-size: 3rem; }
        }
    </style>
    </head>
    <body>

    <!-- HERO SECTION -->
    <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&q=80&w=2000');">
        <div class="overlay" style="background: rgba(0,0,0,0.5);"></div>
        <div class="content">
            <div class="apple-title">Radiotherapy. Demystified.</div>
            <div class="apple-subtitle">Profound precision. Designed for your healing.</div>
            <div class="apple-body">Scroll down to explore the complete clinical workflow behind your treatment journey.</div>
        </div>
    </div>

    <!-- STEP 1: SIMULATION -->
    <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=2000');">
        <div class="overlay"></div>
        <div class="content">
            <div class="apple-subtitle">Step 1: The Blueprint</div>
            <div class="apple-title">Locked in. Comfortably.</div>
            <div class="apple-body">Before treatment, we map your anatomy using advanced PCCT, MR, or PET/CT simulators. To ensure millimeter-perfect accuracy, we use custom immobilization devices tailored to you:</div>
            
            <div class="grid-container">
                <div class="grid-box">
                    <div class="grid-title">👤 Head & Neck</div>
                    <div class="grid-text">A warm, mesh-like <b>Thermoplastic Mask</b> is molded over your face and shoulders. It hardens in minutes, keeping you perfectly still to protect critical nearby structures.</div>
                </div>
                <div class="grid-box">
                    <div class="grid-title">🫁 Breast & Thorax</div>
                    <div class="grid-text">You will rest on a customized <b>Breast/Wing Board</b> with your arms safely positioned above your head, exposing the treatment area while stabilizing your lungs.</div>
                </div>
                <div class="grid-box">
                    <div class="grid-title">🧍 Pelvis & Prostate</div>
                    <div class="grid-text">A <b>Vac-Lok Cushion</b> (a medical-grade vacuum beanbag) molds exactly to your lower body, ensuring absolute stability for your legs and pelvis every single day.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- STEP 2: PLANNING -->
    <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2000');">
        <div class="overlay"></div>
        <div class="content">
            <div class="apple-subtitle">Step 2: The Algorithm</div>
            <div class="apple-title">Invisible math. Maximum impact.</div>
            <div class="apple-body">Behind the scenes, your clinical oncologists and dosimetrists construct a highly customized 3D plan.</div>
            
            <div class="grid-container">
                <div class="grid-box">
                    <div class="grid-title">🎯 Contouring</div>
                    <div class="grid-text">Doctors meticulously draw exact boundaries on your scans, separating the target tumor volume from the critical Organs at Risk (OARs) nearby.</div>
                </div>
                <div class="grid-box">
                    <div class="grid-title">📐 Dosimetry</div>
                    <div class="grid-text">Using powerful supercomputers, we calculate the exact angles, intensity, and shape of the radiation beams to maximize tumor destruction while shielding healthy tissue.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- STEP 3: VERIFICATION -->
    <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&q=80&w=2000');">
        <div class="overlay"></div>
        <div class="content">
            <div class="apple-subtitle">Step 3: The Verification</div>
            <div class="apple-title">Image-Guided Precision.</div>
            <div class="apple-body">Before the treatment beam even turns on, we perform a vital safety check right inside the treatment room.</div>
            
            <div class="grid-container">
                <div class="grid-box">
                    <div class="grid-title">📷 Daily CBCT Scans</div>
                    <div class="grid-text">We take a quick 3D X-ray (Cone Beam CT) while you are lying on the bed. The radiation therapists compare this live image against your original Step 1 Blueprint.</div>
                </div>
                <div class="grid-box">
                    <div class="grid-title">📏 Micro-Adjustments</div>
                    <div class="grid-text">Internal organs shift naturally. The robotic bed will shift by fractions of a millimeter to ensure the tumor is perfectly aligned with the machine's crosshairs.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- STEP 4: THE TREATMENT -->
    <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=2000');">
        <div class="overlay"></div>
        <div class="content">
            <div class="apple-subtitle">Step 4: The Treatment</div>
            <div class="apple-title">The right tool for the target.</div>
            <div class="apple-body">You will not feel, see, or smell the radiation. It is completely painless. Depending on your specific plan, we use one of our advanced delivery systems:</div>
            
            <div class="grid-container">
                <div class="grid-box">
                    <div class="grid-title">🚀 Linear Accelerator (Linac)</div>
                    <div class="grid-text"><b>The Workhorse.</b> The open, rotating arm moves seamlessly around you. Using VMAT technology, it sculpts radiation beams to the 3D shape of the tumor in just a few minutes. Fast and highly versatile.</div>
                </div>
                <div class="grid-box">
                    <div class="grid-title">🌀 TomoTherapy</div>
                    <div class="grid-text"><b>The Spiral Specialist.</b> Delivering radiation slice-by-slice in a continuous 360-degree spiral. It provides unmatched conformal dose distribution, making it exceptionally powerful for complex or large treatment areas.</div>
                </div>
            </div>
        </div>
    </div>

    </body>
    </html>
    """
    
    # Render the full HTML code in a scrolling iframe
    components.html(html_code, height=3500, scrolling=True)
