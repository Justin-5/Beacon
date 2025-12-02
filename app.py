import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_shadcn_ui import card, metric_card
from src.workflow import run_volunteer_agent_flow
import json
import re

# Page Config
st.set_page_config(
    page_title="Beacon - AI Volunteer Guide",
    page_icon="🕯️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Teal and Dark Blue Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(40px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes glow {
        0%, 100% {
            box-shadow: 0 0 20px rgba(20, 184, 166, 0.3);
        }
        50% {
            box-shadow: 0 0 40px rgba(20, 184, 166, 0.6);
        }
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0c4a6e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(20, 184, 166, 0.2);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Hero Section */
    .hero-container {
        background: linear-gradient(135deg, #0c4a6e 0%, #14b8a6 100%);
        padding: 4rem 3rem;
        border-radius: 24px;
        text-align: center;
        margin: 2rem 0 3rem 0;
        box-shadow: 0 20px 60px rgba(20, 184, 166, 0.3);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 1s ease-out;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: glow 4s ease-in-out infinite;
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 5rem;
        font-weight: 800;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        letter-spacing: -2px;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.8rem;
        font-weight: 300;
        color: rgba(255,255,255,0.95);
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-cta {
        display: inline-block;
        background: white;
        color: #0c4a6e;
        padding: 1rem 3rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 600;
        text-decoration: none;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
        cursor: pointer;
    }
    
    .hero-cta:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.3);
    }
    
    /* Stats Section */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(12, 74, 110, 0.1) 100%);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        backdrop-filter: blur(10px);
        animation: fadeInUp 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        border-color: rgba(20, 184, 166, 0.6);
        box-shadow: 0 12px 32px rgba(20, 184, 166, 0.2);
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 800;
        color: #14b8a6;
        font-family: 'Poppins', sans-serif;
    }
    
    .stat-label {
        font-size: 1rem;
        color: rgba(255,255,255,0.8);
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Search Section */
    .search-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(20, 184, 166, 0.2);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        animation: fadeInUp 1s ease-out;
    }
    
    .search-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 2px solid rgba(20, 184, 166, 0.3);
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        font-size: 1.1rem;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #14b8a6;
        box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.2);
        background: rgba(255, 255, 255, 0.15);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #14b8a6 0%, #0c4a6e 100%);
        color: white;
        font-family: 'Poppins', sans-serif;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 1rem 3rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 8px 24px rgba(20, 184, 166, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(20, 184, 166, 0.5);
    }
    
    /* Result Cards */
    .result-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        animation: slideIn 0.6s ease-out;
    }
    
    .result-card:hover {
        transform: translateX(10px);
        border-color: #14b8a6;
        box-shadow: 0 8px 32px rgba(20, 184, 166, 0.3);
    }
    
    .result-card h3 {
        color: #14b8a6;
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .result-card p {
        color: rgba(255, 255, 255, 0.9);
        line-height: 1.8;
        font-size: 1rem;
    }
    
    /* About Section */
    .about-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(20, 184, 166, 0.2);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        animation: fadeInUp 1s ease-out;
    }
    
    .about-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1.5rem;
    }
    
    .about-text {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 1.5rem;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .feature-item {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(12, 74, 110, 0.1) 100%);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-5px);
        border-color: #14b8a6;
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: #14b8a6;
        margin-bottom: 0.8rem;
    }
    
    .feature-desc {
        color: rgba(255, 255, 255, 0.8);
        line-height: 1.6;
    }
    
    /* Status Messages */
    .stSuccess {
        background: rgba(20, 184, 166, 0.1);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-radius: 12px;
        color: #14b8a6;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 12px;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: white;
        font-family: 'Poppins', sans-serif;
    }
    
    p {
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(20, 184, 166, 0.1);
        border-radius: 12px;
        color: white;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(20, 184, 166, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #14b8a6; font-family: Poppins;'>🕯️ Beacon</h1>",
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7); margin-bottom: 2rem;'>Navigate Your Journey</p>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["Home", "Search", "About"],
        icons=["house-fill", "search", "info-circle-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#14b8a6", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "5px",
                "padding": "12px",
                "border-radius": "12px",
                "color": "rgba(255,255,255,0.8)",
                "font-family": "Poppins",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #14b8a6 0%, #0c4a6e 100%)",
                "color": "white",
                "font-weight": "600",
            },
        }
    )

# HOME PAGE
if selected == "Home":
    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">🕯️ Beacon</h1>
            <p class="hero-subtitle">AI-Powered Volunteer Guide</p>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; max-width: 700px; margin: 0 auto 1rem auto; position: relative; z-index: 1;">
                Illuminate your path to making a difference. Discover meaningful volunteer opportunities 
                tailored to your passion, location, and availability.
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; margin-top: 1.5rem; position: relative; z-index: 1;">
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px);">
                    ✨ RAG-Powered
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px);">
                    🎯 JSON Mode
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px);">
                    🤖 Multi-Agent AI
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.9rem; backdrop-filter: blur(10px);">
                    🔍 Web Scraping
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Stats Section
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">3</div>
                <div class="stat-label">AI Agents</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">2000</div>
                <div class="stat-label">Chars Scraped/Page</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">100%</div>
                <div class="stat-label">Valid JSON Output</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">5</div>
                <div class="stat-label">Results Per Search</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Technical Features Section
    st.markdown("<h2 style='text-align: center; color: white; font-size: 2.5rem; margin: 3rem 0 1rem 0;'>🚀 Powered by Advanced AI Technology</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 1.1rem; margin-bottom: 2rem;'>Enterprise-grade features that make Beacon stand out</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">📚</div>
                <div class="feature-title">RAG (Retrieval-Augmented Generation)</div>
                <div class="feature-desc">
                    Unlike basic search tools that only read snippets, Beacon uses web scraping with BeautifulSoup 
                    to fetch and analyze the <strong>full content</strong> of each website (up to 2000 characters). 
                    This allows our AI to verify real details like specific dates, requirements, and contact information.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Robust JSON Mode with Pydantic</div>
                <div class="feature-desc">
                    Beacon uses Gemini's native JSON mode with Pydantic schemas to guarantee <strong>100% valid, 
                    structured output</strong> every time. No more parsing errors or broken responses—just clean, 
                    reliable data that powers consistent results.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # User Benefits Section
    st.markdown("<h2 style='text-align: center; color: white; font-size: 2.5rem; margin: 3rem 0 2rem 0;'>Why Choose Beacon?</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Smart Matching</div>
                <div class="feature-desc">
                    Our AI analyzes your preferences and finds opportunities that perfectly match 
                    your interests, skills, and availability.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">⚡</div>
                <div class="feature-title">Instant Results</div>
                <div class="feature-desc">
                    Get curated volunteer opportunities in seconds. No more endless scrolling 
                    through irrelevant listings.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🌍</div>
                <div class="feature-title">Local Impact</div>
                <div class="feature-desc">
                    Find opportunities in your community and make a real difference where it 
                    matters most to you.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Call to Action
    st.markdown("<h2 style='text-align: center; color: white; font-size: 2rem; margin: 3rem 0 1rem 0;'>Ready to Make a Difference?</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 1.2rem; margin-bottom: 2rem;'>Start your volunteering journey today</p>", unsafe_allow_html=True)

# SEARCH PAGE
elif selected == "Search":
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="search-title">🔍 Find Your Perfect Opportunity</h1>',
                unsafe_allow_html=True)

    # Search Input
    user_request = st.text_input(
        "What kind of volunteering are you looking for?",
        placeholder="e.g., Animal welfare in Mumbai this weekend, Teaching children in Bangalore...",
        label_visibility="collapsed",
        key="search_input"
    )

    # Search Button
    search_button = st.button("🚀 Search Opportunities",
                              use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Technical Info
    with st.expander("🔬 How Beacon's AI Works"):
        st.markdown("""
        **Behind the scenes, Beacon uses cutting-edge AI technology:**
        
        1. **Research Agent** converts your request into optimized search queries
        2. **Web Scraper** fetches full page content (up to 2000 chars) from each result
        3. **Filter Agent** uses RAG to read actual website content and validate opportunities
        4. **JSON Mode** with Pydantic ensures 100% structured, error-free output
        5. **Format Agent** presents results in a clear, actionable format
        
        This is not just a search tool—it's an intelligent system that understands context!
        """)

    # Examples
    with st.expander("💡 Need inspiration? Try these examples"):
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            st.markdown("""
            - 🐾 Animal welfare in Mumbai this weekend
            - 📚 Teaching underprivileged children in Delhi
            - 🌳 Environmental conservation in Bangalore
            - 🏥 Healthcare volunteering in Chennai
            """)
        with ex_col2:
            st.markdown("""
            - 🍲 Food distribution programs near me
            - 👴 Elder care services in Pune
            - 🎨 Arts and culture programs in Kolkata
            - 🏗️ Community building projects in Hyderabad
            """)

    # Process Search
    if search_button:
        if user_request:
            with st.status("🕯️ Beacon is illuminating opportunities...", expanded=True) as status:
                st.write(
                    "🤖 **Agent 1: Research Agent** - Analyzing your request and generating optimal search queries...")
                st.write(
                    "🌐 **Web Scraping** - Fetching full page content from volunteer websites (RAG in action)...")
                st.write(
                    "🔍 **Agent 2: Filter Agent** - Reading full website content and validating opportunities with JSON mode...")

                # Run the workflow
                final_response = run_volunteer_agent_flow(user_request)

                st.write(
                    "✨ **Agent 3: Format Agent** - Presenting results in a clear, actionable format...")
                st.write(
                    "✅ **Complete!** Found matching opportunities with verified details")
                status.update(label="✨ Search Complete - All Agents Executed!",
                              state="complete", expanded=False)

            # Display Results
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<h2 style='color: #14b8a6; font-size: 2rem; margin-bottom: 1.5rem;'>🎉 Here's What We Found</h2>", unsafe_allow_html=True)

            # Parse and display results in cards
            # Try to split the response into sections
            sections = final_response.split('\n\n')

            for i, section in enumerate(sections):
                if section.strip():
                    st.markdown(f"""
                        <div class="result-card">
                            {section}
                        </div>
                    """, unsafe_allow_html=True)

            # Success message
            st.success(
                "💚 Ready to make a difference? Reach out to these organizations and start your volunteering journey!")

        else:
            st.warning(
                "⚠️ Please enter what you're looking for to get started!")

# ABOUT PAGE
elif selected == "About":
    st.markdown('<div class="about-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="about-title">About Beacon</h1>',
                unsafe_allow_html=True)

    st.markdown("""
        <p class="about-text">
            <strong>Beacon</strong> is your AI-powered guide to discovering meaningful volunteer opportunities. 
            Like a lighthouse guiding ships to shore, we illuminate the path to making a positive impact 
            in your community.
        </p>
        
        <p class="about-text">
            Our mission is to connect passionate individuals with causes that matter. Using advanced AI 
            technology, we analyze thousands of volunteer opportunities to find the perfect match for 
            your interests, skills, and availability.
        </p>
        
        <h2 style="color: #14b8a6; font-size: 2rem; margin: 2rem 0 1rem 0;">How It Works</h2>
    """, unsafe_allow_html=True)

    # Process Steps
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">1️⃣</div>
                <div class="feature-title">Tell Us What You Want</div>
                <div class="feature-desc">
                    Share your interests, location, and availability. Be as specific or general as you like.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">2️⃣</div>
                <div class="feature-title">AI Does the Work</div>
                <div class="feature-desc">
                    Our AI agents research, filter, and curate opportunities that match your criteria.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">3️⃣</div>
                <div class="feature-title">Start Making Impact</div>
                <div class="feature-desc">
                    Get personalized recommendations and connect with organizations ready for your help.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <h2 style="color: #14b8a6; font-size: 2rem; margin: 3rem 0 1rem 0;">🏗️ Technical Architecture</h2>
        <p class="about-text">
            Beacon uses a <strong>multi-agent AI system</strong> powered by Google's Gemini 2.5 Flash. 
            Our three-stage pipeline ensures you get the most relevant and up-to-date volunteer opportunities:
        </p>
    """, unsafe_allow_html=True)

    tech_col1, tech_col2, tech_col3 = st.columns(3)

    with tech_col1:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Agent 1: Research Agent</div>
                <div class="feature-desc">
                    Analyzes your natural language request and generates optimized Google Custom Search queries 
                    to find the most relevant volunteer websites.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with tech_col2:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🔍</div>
                <div class="feature-title">Agent 2: Filter Agent (RAG)</div>
                <div class="feature-desc">
                    Uses <strong>web scraping</strong> to read full page content (not just snippets), then validates 
                    opportunities using <strong>Pydantic models</strong> and <strong>JSON mode</strong> for 100% reliable output.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with tech_col3:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">✨</div>
                <div class="feature-title">Agent 3: Format Agent</div>
                <div class="feature-desc">
                    Transforms structured data into a friendly, easy-to-read response with all the details 
                    you need to take action.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Resume-Worthy Features
    st.markdown("""
        <h2 style="color: #14b8a6; font-size: 2rem; margin: 3rem 0 1rem 0;">💼 Resume-Worthy Features</h2>
        <p class="about-text">
            Beacon showcases advanced software engineering and AI integration skills:
        </p>
    """, unsafe_allow_html=True)

    feat_col1, feat_col2 = st.columns(2)

    with feat_col1:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">📚</div>
                <div class="feature-title">RAG Implementation</div>
                <div class="feature-desc">
                    <strong>Retrieval-Augmented Generation</strong> using BeautifulSoup for web scraping. 
                    Fetches up to 2000 characters of actual page content, enabling the AI to verify specific 
                    details like dates, requirements, and contact info—not just generic snippets.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with feat_col2:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Robust JSON Mode</div>
                <div class="feature-desc">
                    Uses <strong>Gemini's native JSON mode</strong> with <strong>Pydantic schemas</strong> 
                    (VolunteerOpportunity, OpportunityList) to guarantee structured, type-safe output. 
                    Eliminates parsing errors and ensures 100% valid responses.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tech_feat_col1, tech_feat_col2 = st.columns(2)

    with tech_feat_col1:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🔧</div>
                <div class="feature-title">Production-Ready Code</div>
                <div class="feature-desc">
                    Modular architecture with separate files for models, agents, tools, and workflow. 
                    Proper error handling, relative imports, and deployment configuration for cloud hosting.
                </div>
            </div>
        """, unsafe_allow_html=True)

    with tech_feat_col2:
        st.markdown("""
            <div class="feature-item">
                <div class="feature-icon">🎨</div>
                <div class="feature-title">Modern UI/UX</div>
                <div class="feature-desc">
                    Built with Streamlit featuring custom CSS, animations, glassmorphism effects, 
                    and responsive design. Professional dashboard with sidebar navigation and status indicators.
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <h2 style="color: #14b8a6; font-size: 2rem; margin: 3rem 0 1rem 0;">Join the Movement</h2>
        <p class="about-text">
            Every volunteer hour creates ripples of positive change. Whether you have a few hours 
            or a few days, your contribution matters. Let Beacon guide you to opportunities where 
            you can make the biggest impact.
        </p>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**🕯️ Beacon**")
    st.markdown("Illuminating paths to positive change")
    st.markdown("*RAG-powered volunteer discovery*")

with footer_col2:
    st.markdown("**🔗 Quick Links**")
    st.markdown("Home • Search • About")
    st.markdown("*Multi-agent AI system*")

with footer_col3:
    st.markdown("**💡 Tech Stack**")
    st.markdown("Gemini 2.5 • Pydantic • BeautifulSoup")
    st.markdown("*Streamlit • Google Custom Search*")
