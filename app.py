import streamlit as st
from src.workflow import run_volunteer_agent_flow

# Page Config
st.set_page_config(
    page_title="Beacon - AI Volunteer Guide",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for volunteering theme
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 300;
        margin-bottom: 0.5rem;
    }
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 0.75rem 3rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    .result-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🕯️ Beacon</div>
        <div class="hero-subtitle">Your AI-Powered Guide to Making a Difference</div>
        <p style="font-size: 1.1rem; margin-top: 1rem; opacity: 0.9;">
            Discover meaningful volunteer opportunities tailored to your interests and location
        </p>
    </div>
""", unsafe_allow_html=True)

# Feature Cards
st.markdown("### ✨ Why Choose Beacon?")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Smart Matching</div>
            <p>AI-powered search finds opportunities that match your passion and availability</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Instant Results</div>
            <p>Get curated volunteer opportunities in seconds, not hours of searching</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🌍</div>
            <div class="feature-title">Local Impact</div>
            <p>Find opportunities in your community and make a real difference nearby</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Search Section
st.markdown("### 🔍 Find Your Perfect Volunteer Opportunity")

# Create a more prominent search area
search_col1, search_col2 = st.columns([4, 1])

with search_col1:
    user_request = st.text_input(
        "What kind of volunteering are you looking for?",
        placeholder="e.g., Animal welfare in Mumbai this weekend, Teaching children in Bangalore, Environmental cleanup...",
        label_visibility="collapsed"
    )

with search_col2:
    search_button = st.button("🔎 Search", use_container_width=True)

# Examples section
with st.expander("💡 Need inspiration? Try these examples"):
    example_col1, example_col2 = st.columns(2)
    with example_col1:
        st.markdown("""
        - 🐾 Animal welfare in Mumbai this weekend
        - 📚 Teaching underprivileged children in Delhi
        - 🌳 Environmental conservation in Bangalore
        """)
    with example_col2:
        st.markdown("""
        - 🏥 Healthcare volunteering in Chennai
        - 🍲 Food distribution programs near me
        - 👴 Elder care services in Pune
        """)

# Button to trigger the agent
if search_button:
    if user_request:
        # Streamlit has a status container that is perfect for your sequential agents
        with st.status("🕯️ Beacon is illuminating opportunities...", expanded=True) as status:
            st.write("🤖 Analyzing your request and preferences...")
            st.write("🔍 Searching for relevant opportunities...")

            # Run the workflow
            final_response = run_volunteer_agent_flow(user_request)

            st.write("✅ Found matching opportunities!")
            status.update(label="✨ Search Complete!",
                          state="complete", expanded=False)

        # Display Result in a styled container
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.markdown("### 🎉 Here's What We Found For You:")
        st.markdown(final_response)
        st.markdown('</div>', unsafe_allow_html=True)

        # Call to action
        st.success(
            "💚 Ready to make a difference? Reach out to these organizations and start your volunteering journey!")
    else:
        st.warning("⚠️ Please enter what you're looking for to get started!")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**🤝 About Beacon**")
    st.markdown(
        "Connecting volunteers with opportunities to create positive change")

with footer_col2:
    st.markdown("**💡 How It Works**")
    st.markdown("AI analyzes your request and finds the best matches instantly")

with footer_col3:
    st.markdown("**🌟 Make an Impact**")
    st.markdown("Every volunteer hour creates ripples of positive change")
