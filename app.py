import streamlit as st
import re
import os
import random
from dotenv import load_dotenv
from google import genai 
from google.genai import types


# --- Magical Bestiary Data ---
PETS = [
    {"min_xp": 0, "name": "Ash Pebble", "emoji": "🪨🔥", "desc": "A dormant stone that pulses with faint heat. Keep solving to wake it!"},
    {"min_xp": 150, "name": "Flame Chick", "emoji": "🐣🔥", "desc": "A tiny bird of embers. Its chirps sound like crackling wood!"},
    {"min_xp": 400, "name": "Spark Drake", "emoji": "🦎⚡", "desc": "A swift, grounded dragon that feeds on mathematical energy."},
    {"min_xp": 800, "name": "Cloud-Breaker Wyvern", "emoji": "🐲☁️", "desc": "It has taken to the skies! Its wings create thunderous applause for your logic."},
    {"min_xp": 1000, "name": "Archmage's Grand Mythos", "emoji": "🐉🌋", "desc": "The ultimate guardian. Its breath can forge new stars from old equations."},
]

def get_current_pet(xp):
    active_pet = PETS[0]
    for pet in PETS:
        if xp >= pet["min_xp"]:
            active_pet = pet
    return active_pet

# --- 1. Load Environment Variables ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def save_game():      #load and save functions
    with open("wizard_save.txt", "w") as f:
        f.write(str(st.session_state.xp))
    st.toast("✨ Progress saved to your spellbook!", icon="💾")

def load_game():
    if os.path.exists("wizard_save.txt"):
        with open("wizard_save.txt", "r") as f:
            saved_xp = f.read()
            if saved_xp.isdigit():
                st.session_state.xp = int(saved_xp)

# --- 2. Page Setup ---
st.set_page_config(page_title="AMPLIFY", page_icon="📘", layout="centered")

# --- 3. Initialize Session States ---
#a.Define the defaults first
state_defaults = {
    "xp": 0, 
    "current_pet_name": "Ash Pebble",
    "stardust": 0,
    "dragon_scales": 0,
    "struggles": {"Real": 0, "Complex": 0, "Equal": 0},
    "show_attempt": None, 
    "discriminant_checked": False, 
    "root_type_checked": False, 
    "roots_solved": False, 
    "d_rewarded": False, 
    "type_rewarded": False, 
    "roots_rewarded": False, 
    "saved_root_type": ""   
}

#b.Initialize everything in one loop
for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# c. Now try to LOAD the XP from the file
# This ONLY runs if we are at the very start of the session
if "loaded" not in st.session_state:
    load_game()
    st.session_state.loaded = True # Prevents it from re-loading every time you click a button

# --- 4. AI Hint Function (With Diagnostic Loop) ---
def get_ai_hint(user_question, context_info):
    if not API_KEY: return "⚠️ API Key missing"
    try:
        client = genai.Client(api_key=API_KEY, http_options=types.HttpOptions(api_version='v1'))
        
        # We combine the personality and the question into one string
        # This avoids the "System Instruction" error entirely
        full_prompt = (
            "SYSTEM: You are AMPLIFY, a witty study wizard. Use LaTeX ($) for math. "
            "If the student is correct, you MUST say 'YES MASTER'. Never give final answers.\n\n"
            f"USER QUESTION: {user_question}\n"
            f"STUDENT ATTEMPT: {context_info}"
        )

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        return f"🧙‍♂️ Wizard Error: {str(e)}"

# --- 5. XP & Level Logic ---
def get_wizard_stats(xp):
    if xp < 100: return "Novice Apprentice 🧙‍♂️", 100
    if xp < 300: return "Mystic Mage 🔮", 300
    if xp < 600: return "Sorcerer Supreme 🔥", 600
    return "Grand Archmage ✨", 1000

def reset_wizard():
    for key in ["show_attempt", "discriminant_checked", "root_type_checked", "roots_solved", 
                "d_rewarded", "type_rewarded", "roots_rewarded", "saved_root_type"]:
        st.session_state[key] = state_defaults[key]
    st.rerun()

# --- 6. STYLING (Corrected) ---
st.markdown("""
<style>
    /* MOVE THIS INSIDE THE STYLE TAGS */
    .mythic-text {
        color: #FFD700 !important;
        text-shadow: 0px 0px 10px rgba(255, 215, 0, 0.8), 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: bold;
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { text-shadow: 0px 0px 5px #FFD700; }
        to { text-shadow: 0px 0px 20px #FFA500; }
    }

    /* 2. General App Styling */
    body, .stApp { background: linear-gradient(135deg, #fdf6f0, #e0f7fa); color: #1a1a1a; }

    .stNumberInput label, .stTextArea label, .stSelectbox label, .stTextInput label {
    color: #4B0082 !important; /* Deep Purple text */
    font-weight: bold !important;
    font-size: 18px !important;
    background: rgba(255, 255, 255, 0.9); /* More solid white background */
    padding: 5px 15px;
    border-radius: 10px;
    border: 1px solid #4B0082;
    }

   .main-title { 
    font-size:46px; 
    font-weight:bold; 
    color:#F8F9FA; /* Changed to a visible color */
    text-align:center; 
    }
    
    .stButton>button { 
        border-radius:20px; padding:12px 30px; font-size:16px; font-weight:bold; 
        background: linear-gradient(45deg, #ffb6c1, #fad0c4) !important; 
        color:#4B0082 !important; border:none;
    }
    .stButton>button:hover { transform: scale(1.05); background: linear-gradient(45deg, #a18cd1, #fbc2eb) !important; color:white !important; }

    .card { background: linear-gradient(135deg, #ffe6f0, #fff5e6); padding:20px; border-radius:20px; box-shadow:3px 3px 12px #d3d3d3; margin-bottom:25px; color: #1a1a1a; }
    .warning-box { background: #ffff99 !important; padding:15px; border-radius:15px; color: #000000 !important; font-weight: bold; border: 1px solid #e6e600; }
    .success-msg { background-color: #d4edda; color: #155724; padding: 15px; border-radius: 15px; font-weight: bold; margin-bottom: 10px; }
    .xp-banner { text-align: center; font-weight: bold; color: #4B0082; font-size: 18px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 7. UI Header ---
# --- XP Header & Progress ---
level_name, max_xp = get_wizard_stats(st.session_state.xp)
st.markdown(f'<div class="xp-banner">{level_name} | XP: {st.session_state.xp}/{max_xp}</div>', unsafe_allow_html=True)
st.progress(min(st.session_state.xp / max_xp, 1.0))

# --- EVOLUTION LOGIC ---
# Initialize the tracker if it doesn't exist
if "current_pet_name" not in st.session_state:
    st.session_state.current_pet_name = get_current_pet(st.session_state.xp)["name"]

# Check current pet
active_pet = get_current_pet(st.session_state.xp)

# Trigger Evolution Celebration
if active_pet["name"] != st.session_state.current_pet_name:
    st.balloons()
    st.success(f"✨ WOW! Your magic has caused an EVOLUTION! Your companion is now a **{active_pet['name']}**!")
    st.session_state.current_pet_name = active_pet["name"]
    # We save the game here too so the evolution sticks!
    if 'save_game' in globals():
        save_game()

# --- SIDEBAR COMPANION DISPLAY (Final Optimized Version) ---
active_pet = get_current_pet(st.session_state.xp)
is_mythic = active_pet["min_xp"] >= 1000

p_name = active_pet['name']
p_emoji = active_pet['emoji']
p_desc = active_pet['desc']
p_color = "#B8860B" if is_mythic else "#4B0082"

# 1. The Companion Card & Vault (Combined into one clean visual unit)
st.sidebar.markdown(f"""
<div style="background-color: white !important; padding: 20px; border-radius: 20px 20px 0 0; border: 4px solid #4B0082; text-align: center; color: black !important; border-bottom: none;">
    <div style="font-size: 70px; margin: 0;">{p_emoji}</div>
    <h3 style="margin: 10px 0; font-family: Arial, sans-serif;">
        <span style="color: {p_color} !important;">{p_name}</span>
    </h3>
    <p style="margin: 0; font-style: italic; color: #2F4F4F !important; font-size: 14px;">"{p_desc}"</p>
</div>
<div style="padding: 10px; background: #f8f9fa; border-radius: 0 0 20px 20px; border: 4px solid #4B0082; text-align: center; color: #4B0082;">
    <small>🎒 <b>WIZARD'S VAULT</b></small><br>
    <span style="font-size: 14px;">🌟 Stardust: {st.session_state.stardust} | 🛡️ Scales: {st.session_state.dragon_scales}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #4B0082; text-align: center;'>📈 Mastery Heatmap</h3>", unsafe_allow_html=True)

# 2. The Heatmap Bars (Single loop, no duplicates)
for skill, count in st.session_state.struggles.items():
    mastery = max(100 - (count * 20), 10) 
    color = "#28a745" if mastery > 70 else ("#fd7e14" if mastery > 40 else "#dc3545")
    
    st.sidebar.markdown(f"""
        <div style="font-size: 14px; margin-bottom: 2px; color: #4B0082; font-weight: bold;">{skill} Roots</div>
        <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 12px; margin-bottom: 10px;">
            <div style="width: {mastery}%; background-color: {color}; height: 12px; border-radius: 10px; transition: width 0.5s;"></div>
        </div>
    """, unsafe_allow_html=True)

# 3. Wizard's Wisdom & Teaser
if any(v > 2 for v in st.session_state.struggles.values()):
    st.sidebar.info("🧙‍♂️ Wizard's Advice: You've had some trouble with specific root types. Review the discriminant rules!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏆 Daily Quest")
st.sidebar.info("✨ **The Pythagorean Trial**\n\nUnlocks in Phase 2! Solve daily quests to earn **200 XP** and rare Phoenix Feathers.")

# ---8. Quadratic Module (Polished & Final) ---
def quadratic_module():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Quadratic Equation Helper 🧮")
    col1, col2, col3 = st.columns(3)
    
    # These labels are now visible thanks to our CSS!
    a = col1.number_input("Value of a", value=1.0, key="a_in")
    b = col2.number_input("Value of b", value=0.0, key="b_in")
    c = col3.number_input("Value of c", value=0.0, key="c_in")

    if a == 0:
        st.error("⚠️ 'a' cannot be 0.")
        return

    eq_str = f"{a}x² + {b}x + {c} = 0"
    D_actual = b**2 - 4*a*c

    # STEP 1: Discriminant
    st.markdown("### Step 1: Discriminant")
    user_D = st.number_input("What is the Discriminant (D)?", value=0.0, key="D_in")
    if st.button("Check Discriminant"):
        if abs(user_D - D_actual) < 0.001:
            if not st.session_state.d_rewarded:
                st.session_state.xp += 50
                st.session_state.d_rewarded = True
            st.session_state.discriminant_checked = True
            st.rerun()
        else:
            with st.spinner("Asking Wizard..."):
                hint = get_ai_hint(eq_str, f"Student thought D={user_D}, actual is {D_actual}.")
                st.markdown(f'<div class="warning-box">🧙‍♂️ {hint}</div>', unsafe_allow_html=True)

    # STEP 2: Nature of Roots
    if st.session_state.discriminant_checked:
        st.markdown('<div class="success-msg">✅ Correct D! +50 XP Earned</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Step 2: Nature of Roots")
        root_map = {"Two real and distinct roots": D_actual > 0, "One real root": D_actual == 0, "Complex roots": D_actual < 0}
        selected = st.selectbox("Select the type of roots:", list(root_map.keys()))
        if st.button("Check Nature"):
            if root_map[selected]:
                if not st.session_state.type_rewarded:
                    st.session_state.xp += 30
                    st.session_state.type_rewarded = True
                st.session_state.saved_root_type = selected
                st.session_state.root_type_checked = True
                st.rerun()
            else:
                key = "Real" if D_actual > 0 else ("Complex" if D_actual < 0 else "Equal")
                st.session_state.struggles[key] += 1
                st.markdown('<div class="warning-box">⚠️ That nature doesn\'t match D! The Wizard has noted this weakness.</div>', unsafe_allow_html=True)
            
    # STEP 3: Solve the Roots
    if st.session_state.root_type_checked:
        st.markdown(f'<div class="success-msg">🎉 Correct! Roots are {st.session_state.saved_root_type}. +30 XP</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("### Step 3: Solve the Roots")
        
        if D_actual < 0:
            st.info("💡 Hint: Since D is negative, the roots will have 'i' (imaginary).")
            
        r1_user = st.text_input("Root 1 (e.g., 2 or -1.5 + 2i)", key="r1_user")
        r2_user = st.text_input("Root 2 (e.g., 2 or -1.5 - 2i)", key="r2_user")
        
        if st.button("Master the Equation"):
            with st.spinner("Wizard is verifying your final answer..."):
                # The AI now checks if the roots are correct based on the actual values
                check = get_ai_hint(eq_str, f"Student says roots are {r1_user} and {r2_user}. If they are correct, say 'YES MASTER'. If not, give a hint.")
                
                if "YES MASTER" in check.upper():
                    if not st.session_state.roots_rewarded:
                        st.session_state.xp += 100
                        st.session_state.roots_rewarded = True
                        # --- NEW: LOOT DROP (Added right here!) ---
                        roll = random.random()
                        if roll < 0.3:
                            st.session_state.stardust += 1
                            st.toast("✨ You found 1x Stardust in the equation's remains!", icon="🌟")
                        elif roll < 0.5:
                            st.session_state.dragon_scales += 1
                            st.toast("🔥 Your pet found a Dragon Scale!", icon="🛡️")
                        # ------------------------------------------
                        save_game() # <--- AUTO-SAVE HERE!
                        st.balloons()
                    st.success("🎯 LEGENDARY! You have mastered this equation. +100 XP")
                else:
                    st.markdown(f'<div class="warning-box">🧙‍♂️ {check}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 9. Main App Execution ---
st.markdown('<div class="card">', unsafe_allow_html=True)
question = st.text_area("Paste your question here:", height=100, key="main_q")
st.markdown('</div>', unsafe_allow_html=True)

if question:
    # Check if the question is quadratic
    if re.search(r"(x\^2|x²|quadratic)", question.lower()):
        quadratic_module()
    else:
        # Standard Hint Logic
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Need a Hint? 💡")
        c1, c2 = st.columns(2)
        if c1.button("Yes", key="h_yes"): st.session_state.show_attempt = True
        if c2.button("No", key="h_no"): st.session_state.show_attempt = False

        if st.session_state.show_attempt:
            attempt = st.text_area("Your Attempt:", key="att_box")
            if st.button("Analyze My Attempt"):
                if attempt:
                    with st.spinner("Wizard is thinking..."):
                        hint = get_ai_hint(question, attempt)
                        st.markdown(f'<div class="hint-box">🧙‍♂️ {hint}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
if st.button("Clear All / New Question 🧹"):
    reset_wizard()