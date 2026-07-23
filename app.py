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
    # Injecting massive custom CSS to override Streamlit's default layout
    st.markdown("""
        <style>
        /* Remove Streamlit's default padding to allow edge-to-edge images */
        .block-container {
            padding: 0rem !important;
            max-width: 100% !important;
        }
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* The Parallax Magic */
        .parallax {
            /* Create the fixed scrolling effect */
            background-attachment: fixed;
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
            
            /* Make each section take the full screen height */
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }

        /* Dark overlay so the white text is readable */
        .overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1;
        }

        /* Apple-style typography */
        .content {
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
            padding: 20px;
            max-width: 900px;
        }
        .apple-title { font-size: 5rem; font-weight: 700; letter-spacing: -0.1rem; line-height: 1.1; margin-bottom: 20px;}
        .apple-subtitle { font-size: 2rem; font-weight: 500; color: #f5f5f7; margin-bottom: 30px;}
        .apple-body { font-size: 1.2rem; font-weight: 300; line-height: 1.6; color: #d2d2d7;}
        </style>
    """, unsafe_allow_html=True)

    # HERO SECTION
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay" style="background: rgba(0,0,0,0.7);"></div>
            <div class="content">
                <div class="apple-title">Radiotherapy.</div>
                <div class="apple-title" style="color: #0071e3;">Demystified.</div>
                <div class="apple-subtitle">Profound precision. Designed for your healing.</div>
                <div class="apple-body">Scroll down to explore your journey.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # SIMULATION SECTION
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">1. The Blueprint</div>
                <div class="apple-title" style="font-size: 3.5rem;">Mapping the unseen.</div>
                <div class="apple-body">Before treatment begins, we create a flawless map of your anatomy using advanced simulators like PCCT, MR, or PET/CT. You will lie still while a custom immobilization device is gently molded to your body. This ensures millimeter-perfect accuracy.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # PLANNING SECTION
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">2. The Algorithm</div>
                <div class="apple-title" style="font-size: 3.5rem;">Invisible math.</div>
                <div class="apple-body">Behind the scenes, clinical oncologists and dosimetrists construct a highly customized plan. We calculate the exact trajectory of the radiation beams to maximize impact on the target area while strictly protecting surrounding healthy tissues.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # TREATMENT SECTION
    st.markdown("""
        <div class="parallax" style="background-image: url('https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&q=80&w=2000');">
            <div class="overlay"></div>
            <div class="content">
                <div class="apple-subtitle">3. The Delivery</div>
                <div class="apple-title" style="font-size: 3.5rem;">Painless. Precise.</div>
                <div class="apple-body">Inside the Linear Accelerator (Linac) room, therapists align you to your exact setup marks. The actual treatment takes only minutes, is completely invisible, and causes no pain. You will hear a buzzing sound, and we monitor you closely via cameras at all times.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
