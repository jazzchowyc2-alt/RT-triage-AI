import streamlit as st
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑", layout="centered")

# --- HELPER FUNCTION ---
def render_html(html_string):
    """Strips leading whitespace so Streamlit doesn't turn it into a code block."""
    cleaned_html = "\n".join([line.strip() for line in html_string.split("\n")])
    st.markdown(cleaned_html, unsafe_allow_html=True)

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
    
    # 1. STATIC CSS (Base Layout)
    static_css = """
        <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header {visibility: hidden;} footer {visibility: hidden;}

        .parallax-section {
            background-attachment: fixed; background-position: center; background-repeat: no-repeat;
            background-size: cover; min-height: 100vh; display: flex; align-items: center;
            justify-content: center; position: relative; padding: 40px 20px;
        }

        .overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.75); z-index: 1; }
        .content { position: relative; z-index: 2; text-align: center; color: white; padding: 20px; max-width: 1100px; }
        
        .apple-title { font-size: 4.5rem; font-weight: 700; letter-spacing: -0.05rem; line-height: 1.1; margin-bottom: 20px; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }
        .apple-subtitle { font-size: 1.8rem; font-weight: 600; color: #0071e3; margin-bottom: 20px; text-shadow: 1px 1px 5px rgba(0,0,0,0.8); }
        .apple-body { font-size: 1.25rem; font-weight: 300; line-height: 1.6; color: #f5f5f7; text-shadow: 1px 1px 5px rgba(0,0,0,0.8); margin-bottom: 30px; }
        
        .grid-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; text-align: left; margin-top: 40px; }
        .grid-box { background: rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.2); transition: transform 0.3s ease; }
        .grid-box:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.15); }
        .grid-title { font-size: 1.4rem; font-weight: 600; color: #fff; margin-bottom: 15px; }
        .grid-text { font-size: 1.1rem; color: #d2d2d7; line-height: 1.5; }
        
        @media (max-width: 768px) { .apple-title { font-size: 3rem; } }
        </style>
    """
    render_html(static_css)

    # 2. DYNAMIC CSS (Using Raw GitHub URLs for Instant Loading - Bypassing Base64 completely)
    dynamic_css = """
        <style>
        .parallax-hero { background-image: url("https://raw.githubusercontent.com/jazzchowyc2-alt/RT-triage-AI/main/image/Radiotherapist.png"); }
        .parallax-sim { background-image: url("https://raw.githubusercontent.com/jazzchowyc2-alt/RT-triage-AI/main/image/Simulation.png"); }
        .parallax-plan { background-image: url("https://raw.githubusercontent.com/jazzchowyc2-alt/RT-triage-AI/main/image/Planning.png"); }
        .parallax-cbct { background-image: url("https://raw.githubusercontent.com/jazzchowyc2-alt/RT-triage-AI/main/image/CBCT.png"); }
        .parallax-treat { background-image: url("https://raw.githubusercontent.com/jazzchowyc2-alt/RT-triage-AI/main/image/tomo.png"); }
        </style>
    """
    render_html(dynamic_css)

    # HERO SECTION
    hero_section = """
        <div class="parallax-section parallax-hero">
            <div class="overlay" style="background: rgba(0,0,0,0.5);"></div>
            <div class="content">
                <div class="apple-title">Radiotherapy.<br>Demystified.</div>
                <div class="apple-subtitle">Profound precision. Designed for your healing.</div>
                <div class="apple-body">The journey to recovery involves complex physics and advanced clinical care. Scroll down to explore the complete workflow behind your treatment.</div>
            </div>
        </div>
    """
    render_html(hero_section)

    # STEP 1: SIMULATION SECTION
    sim_section = """
        <div class="parallax-section parallax-sim">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 1: The Blueprint</div>
                <div class="apple-title">Locked in. Comfortably.</div>
                <div class="apple-body">Before treatment begins, your clinical journey starts with a specialized CT or MR Simulation. We map your internal anatomy and create custom immobilization devices to ensure millimeter-perfect reproducibility every single day.</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">👤 Head & Neck Immobilization</div>
                        <div class="grid-text">For head and neck targets, a warm, thermoplastic material is molded securely over your face and shoulders. It hardens into a rigid mask within minutes, acting as an essential 3-point or 5-point fixation system to protect critical structures like your brainstem and optic nerves.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🫁 Thorax & Respiratory Gating</div>
                        <div class="grid-text">For breast or lung treatments, you may rest on a custom Breast/Wing Board. Since tumors in the chest move when you breathe, we often use <b>4D-CT tracking</b> to monitor your respiratory cycle, allowing the radiation beam to turn on only when the tumor is in the exact right position.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🧍 Pelvis & Patient Preparation</div>
                        <div class="grid-text">A <b>Vac-Lok Cushion</b> molds perfectly to your legs for lower body stability. For targets like the prostate or cervix, you will be given strict daily protocols—such as drinking specific amounts of water to fill your bladder—which physically pushes healthy intestines safely out of the radiation field.</div>
                    </div>
                </div>
            </div>
        </div>
    """
    render_html(sim_section)

    # STEP 2: PLANNING SECTION
    plan_section = """
        <div class="parallax-section parallax-plan">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 2: The Algorithm</div>
                <div class="apple-title">Invisible math. Maximum impact.</div>
                <div class="apple-body">During the 1 to 2 weeks before your first treatment, our multidisciplinary team of Clinical Oncologists, Medical Physicists, and Dosimetrists are hard at work constructing your personalized 3D treatment plan.</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">🎯 Target Delineation</div>
                        <div class="grid-text">Using your simulation scans, your Clinical Oncologist meticulously draws boundaries slice-by-slice. They map the exact Gross Tumor Volume (GTV) and microscopic spread, while carefully contouring the nearby healthy Organs at Risk (OARs) to ensure they are spared.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">📐 Dosimetry & Optimization</div>
                        <div class="grid-text">Using powerful supercomputers, our planning software calculates millions of variables. It optimizes the exact angles, intensity, and shape of the radiation beams to maximize tumor destruction while minimizing the dose to surrounding healthy tissue.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🛡️ Phantom Quality Assurance</div>
                        <div class="grid-text">Before you ever step foot in the treatment room, we run a "dry run." Your finalized plan is delivered to a highly sensitive testing phantom to physically verify that the machine is delivering the exact radiation dose the computer prescribed.</div>
                    </div>
                </div>
            </div>
        </div>
    """
    render_html(plan_section)
    
    # STEP 3: VERIFICATION SECTION (New CBCT Section)
    cbct_section = """
        <div class="parallax-section parallax-cbct">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 3: The Verification</div>
                <div class="apple-title">Image-Guided Radiotherapy (IGRT).</div>
                <div class="apple-body">Precision is everything. Internal organs shift naturally from day to day. Before the treatment beam even turns on, your Radiation Therapists perform a vital daily safety check inside the room.</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">📷 Cone Beam CT (CBCT)</div>
                        <div class="grid-text">While you are lying in the exact treatment position, the machine rotates around you to take a quick, live 3D X-ray. We overlay this live image directly on top of your original Step 1 Blueprint to check for any internal movement.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🕹️ 6D Robotic Couch Adjustments</div>
                        <div class="grid-text">If your anatomy has shifted even slightly, our highly advanced robotic treatment couch will automatically shift by fractions of a millimeter—adjusting pitch, roll, and yaw—to ensure the tumor is perfectly aligned with the machine's crosshairs.</div>
                    </div>
                </div>
            </div>
        </div>
    """
    render_html(cbct_section)

    # STEP 4: TREATMENT SECTION
    treat_section = """
        <div class="parallax-section parallax-treat">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">Step 4: The Delivery</div>
                <div class="apple-title">Painless. Fast. Precise.</div>
                <div class="apple-body">You will not feel, see, or smell the radiation. The entire appointment takes about 15 minutes, but the actual radiation is delivered in just 2 to 3 minutes. Depending on your clinical needs, we utilize advanced delivery systems:</div>
                
                <div class="grid-container">
                    <div class="grid-box">
                        <div class="grid-title">🚀 Linear Accelerator (VMAT)</div>
                        <div class="grid-text"><b>The Workhorse.</b> The open, rotating arm moves seamlessly around you. Using Volumetric Modulated Arc Therapy (VMAT), the machine continuously shapes and alters the intensity of the radiation beam as it moves, painting the dose perfectly to the 3D shape of the tumor.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🌀 TomoTherapy</div>
                        <div class="grid-text"><b>The Spiral Specialist.</b> Operating much like a standard CT scanner, TomoTherapy delivers radiation slice-by-slice in a continuous 360-degree spiral. It provides unmatched conformal dose distribution, making it exceptionally powerful for complex or elongated treatment areas.</div>
                    </div>
                    <div class="grid-box">
                        <div class="grid-title">🎥 Constant Care</div>
                        <div class="grid-text">Although the radiotherapists must leave the heavy lead-lined room during the beam delivery, you are never alone. We monitor you continuously through multiple high-definition CCTV cameras and a two-way intercom system.</div>
                    </div>
                </div>
            </div>
        </div>
    """
    render_html(treat_section)
