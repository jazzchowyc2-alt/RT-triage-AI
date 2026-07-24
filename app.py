import streamlit as st
import time
from openai import OpenAI

# 1. Setup the web page
st.set_page_config(page_title="幫緊你幫緊你 AI Triage", page_icon="🚑", layout="centered")

# --- HELPER FUNCTION ---
def render_html(html_string):
    """Strips leading whitespace so Streamlit doesn't turn it into a code block."""
    cleaned_html = "\n".join([line.strip() for line in html_string.split("\n")])
    st.markdown(cleaned_html, unsafe_allow_html=True)

# 2. Navigation Sidebar (Only for Page Navigation now)
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

    # --- NEW UI: MAIN PAGE PATIENT SETUP ---
    st.markdown("### 📋 Step 1: Your Treatment Profile")
    st.info("Please fill this out before messaging the assistant.")
    
    col1, col2 = st.columns(2)
    with col1:
        treatment_site = st.selectbox(
            "Select Radiotherapy Site:", 
            ["Not selected", "Head & Neck (e.g., NPC)", "Breast", "Thorax (Lung/Esophagus)", "Pelvis (Prostate/Rectum/Gynae)", "Other"]
        )
    with col2:
        current_fraction = st.slider("Which fraction are you on today?", 1, 35, 1)

    # --- EXPANDED SMART CHECKLISTS & BLADDER LOGIC ---
    if treatment_site != "Not selected":
        st.markdown("### ✅ Step 2: Today's Pre-Treatment Checklist")
        
        # 1. Pelvis Logic (Dynamic Bladder Protocol)
        if treatment_site == "Pelvis (Prostate/Rectum/Gynae)":
            bladder_protocol = st.radio(
                "What is your doctor's specific bladder instruction?", 
                ["I need a FULL bladder", "I need an EMPTY bladder", "I am not sure"]
            )
            
            if bladder_protocol == "I need a FULL bladder":
                st.checkbox("💧 I emptied my bladder exactly 1 hour ago, and immediately drank my prescribed amount of water (e.g., 500ml).")
                st.checkbox("⏳ I have NOT urinated since drinking the water.")
            elif bladder_protocol == "I need an EMPTY bladder":
                st.checkbox("🚽 I have emptied my bladder right before arriving at the waiting room.")
            else:
                st.warning("⚠️ Please confirm your bladder protocol with your radiotherapist before your session.")
                
            st.checkbox("💩 I have emptied my rectum (bowel movement) today or used my prescribed micro-enema.")
            st.checkbox("🥦 I have avoided gas-producing foods (e.g., beans, cabbage, dairy) in the last 24 hours.")

        # 2. Breast Logic
        elif treatment_site == "Breast":
            st.checkbox("🧴 I have washed my chest but NOT applied any deodorant, lotion, or prescribed creams yet (apply only after treatment).")
            st.checkbox("🎽 I am wearing a loose, comfortable button-down shirt or zip-up top.")
            st.checkbox("🫁 I have practiced my Deep Inspiration Breath Hold (DIBH) exercises today.")

       # 3. Thorax Logic
        elif treatment_site == "Thorax (Lung/Esophagus)":
            st.checkbox("🧴 I have not applied any lotions or creams to my chest or back.")
            st.checkbox("🫁 I have practiced my breathing exercises for respiratory gating.")
            st.checkbox("💊 I have taken my prescribed antacids or pain medication 30 minutes ago (if experiencing heartburn or swallowing discomfort).")

        # 4. Head & Neck Logic
        elif treatment_site == "Head & Neck (e.g., NPC)":
            st.checkbox("🪥 I have completed my daily mouthwash and gentle brushing routine.")
            st.checkbox("💍 I have removed all metal items (dentures, hearing aids, necklaces, earrings).")
            st.checkbox("💊 I have taken my prescribed pain medication 30 minutes ago (if swallowing is painful).")
            st.checkbox("🥤 I have completed my swallowing exercises or PEG tube feeding preparation.")
            
        # 5. Generic/Other Logic
        else:
            st.checkbox("💳 I have my hospital ID, HKID, and appointment slip ready.")
            st.checkbox("👕 I am wearing loose, comfortable clothing with no metal zippers in the treatment area.")

        st.divider()

        # --- AI CHATBOT SECTION ---
        st.markdown("### 💬 Step 3: Chat with the Assistant")
        
        system_prompt = f"""You are a compassionate radiation oncology triage assistant in a Hong Kong hospital.
        The patient is currently on Fraction {current_fraction} of their radiotherapy for {treatment_site}. 
        Adjust your clinical expectations based on this timeline (e.g., acute radiation dermatitis is unlikely at Fraction 1, but highly likely at Fraction 20).
        
        You MUST output your response EXACTLY following this template. Do not skip any sections. 

        CRITICAL RULES:
        1. RED FLAG SAFETY: If the symptom is severe or life-threatening (e.g., heavy bleeding, fever >38.5°C, severe chest pain, unable to swallow), explicitly instruct the patient to go to the A&E (急症室).
        2. ANATOMICAL LOGIC: If the symptom is anatomically impossible for the Treatment Site, state clearly that this is likely unrelated to radiotherapy, but they should seek medical attention.
        3. CANTONESE TONE: Speak in highly natural, empathetic Hong Kong Cantonese.

        ### 🗣️ 姑娘/師兄話你知 (Message to Patient)
        [Write in natural Hong Kong Cantonese. Warmly validate their discomfort. Factor in their current fraction number.]

        ### ✅ 可以咁做 (Do's)
        - [Cantonese: Actionable tip 1]
        - [Cantonese: Actionable tip 2]

        ### ❌ 盡量避免 (Don'ts)
        - [Cantonese: Actionable tip 1]
        - [Cantonese: Actionable tip 2]

        ### 📋 Clinical Note & CTCAE Grading
        **Clinical Note:** [Write exactly 1 brief English sentence summarizing the patient's symptom and ASSIGNING a single estimated CTCAE grade.]
        """

        # Initialize or dynamically update the system prompt based on user selections
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "system", "content": system_prompt}]
        else:
            st.session_state.messages[0] = {"role": "system", "content": system_prompt}

        # Display chat history
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if user_input := st.chat_input("How are you feeling today? (e.g., '我條頸啲皮膚好痛呀')"):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
            strict_reminder = f"""Patient's symptom: {user_input}\nPatient's Treatment Site: {treatment_site}\nFraction: {current_fraction}\n[SYSTEM REMINDER: Output strict template.]"""
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
# PAGE 2: WHAT TO EXPECT 
# ==========================================
elif page == "📖 What to Expect":
    
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

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: white;">Interactive Patient Tools</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("🫁 **DIBH Practice Timer**")
        st.write("For breast and thoracic patients: Practice holding your breath to help us protect your heart during treatment.")
        if st.button("Start 20-Second Breath Hold"):
            progress_text = "Inhale deeply and HOLD..."
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.2)
                my_bar.progress(percent_complete + 1, text=progress_text)
            st.success("Breathe normally! Great job.")

    with col2:
        st.info("🎧 **Sensory Desensitization**")
        st.write("Familiarize yourself with the sounds of the treatment room to reduce anxiety before you arrive.")
        st.audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg", format="audio/ogg")
        st.caption("Example: Linear Accelerator Beam-On Tone")

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
