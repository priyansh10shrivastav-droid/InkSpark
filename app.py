"""InkSpark - Turn a topic into a structured blog post in seconds.

An elegant, editorial AI writing web app with minimal publishing aesthetics.
"""

from datetime import datetime
import os
import re
import traceback
from typing import Optional

from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

from prompts import build_prompt

MODEL_NAME = "gemini-2.5-flash"

# Page configuration
st.set_page_config(
    page_title="InkSpark",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if api_key:
    genai.configure(api_key=api_key)

# Default sample drafts
DEFAULT_DRAFTS = [
    {
        "id": "draft-1",
        "title": "Benefits of Reading Books",
        "date": "Nov 20",
        "word_count": 500,
        "tone": "Friendly",
        "content": """# The Joy of Everyday Reading: Why Books Still Matter

## Introduction
In our screen-filled lives, sitting down with a printed book can feel like stepping into a sanctuary. Reading is not just about absorbing information; it is a quiet conversation with another mind across time and space.

Whether you read fiction, history, or personal essays, carving out even twenty minutes a day to read can reshape how you think, focus, and feel in ways no algorithm can replicate.

## A Sanctuary for Your Attention
Modern apps are designed to scatter our attention across rapid notifications and endless feeds. In contrast, a book asks for sustained, singular attention that allows the nervous system to settle.

When you immerse yourself in a chapter, your mind enters a state of deep concentration. Over time, this strengthens your working memory and restores your ability to contemplate complex ideas without distraction.

## Empathy and Worldview Expansion
Novels allow us to inhabit lives vastly different from our own. We experience struggles, cultures, and emotional landscapes we might never encounter in our daily routines.

Psychologists have consistently observed that reading fiction fosters emotional intelligence and perspective-taking. By seeing the world through diverse protagonists, we cultivate greater patience with the people around us.

## Mental Agility and Restful Sleep
Reading before bed is one of the most reliable sleep rituals available. Unlike the blue light emitted by phones and laptops, a physical page signals to your circadian rhythm that the day is drawing to a close.

Furthermore, reading consistently builds vocabulary and complex reasoning skills, keeping your intellect sharp across all stages of life.

## Conclusion
You do not need to finish a book a week to reap the rewards of reading. Start with ten pages tonight, choose a genre that genuinely delights you, and watch how a quiet reading habit enriches your daily perspective.""",
    },
    {
        "id": "draft-2",
        "title": "How to Stay Productive in College",
        "date": "Nov 18",
        "word_count": 700,
        "tone": "Motivational",
        "content": """# Conquering College: Practical Strategies for Peak Productivity

## Introduction
College offers unprecedented freedom, but with that freedom comes the challenge of managing coursework, social commitments, and personal well-being. Without a clear system, days easily slip away in procrastination and stress.

True academic productivity is not about pulling all-nighters or drinking endless coffee. It is about designing deliberate daily rhythms that let you excel in your classes while leaving ample room to enjoy your university years.

## Master the Art of Time Blocking
To-do lists often deceive us because they list tasks without allocating the time required to finish them. Time blocking solves this by assigning specific appointments on your calendar for studying, reading, and drafting assignments.

Treat these study blocks with the same non-negotiable respect you give to scheduled lecture times. When study hours are pre-committed, you eliminate the cognitive fatigue of wondering what to work on next.

## Harness the Power of the 90-Minute Sprint
Human focus operates in natural cycles. Rather than attempting a grueling four-hour library marathon, break your day into intense 90-minute study sprints followed by 15-minute restorative breaks.

During each sprint, silence notifications, close irrelevant browser tabs, and tackle your most intellectually demanding task. You will accomplish more in two focused sprints than in an entire afternoon of distracted multitasking.

## Protect Your Physical Foundation
Your brain is a physical organ that requires quality sleep, regular movement, and nourishing meals to perform at its peak. Sacrificing sleep for extra study hours yields rapidly diminishing returns in retention and test performance.

Protect seven to eight hours of sleep every night, take brief walking breaks between study sessions, and keep a water bottle at your desk. High cognitive stamina begins with physical vitality.

## Conclusion
Productivity is a muscle developed through consistent, small habits rather than sudden bursts of panic before finals. Implement one system this week, refine it as you go, and step into every semester with confidence and calm control.""",
    },
    {
        "id": "draft-3",
        "title": "Introduction to AI",
        "date": "Nov 16",
        "word_count": 300,
        "tone": "Educational",
        "content": """# Demystifying Artificial Intelligence: A Beginner's Primer

## Introduction
Artificial Intelligence (AI) has moved from speculative science fiction into the core of everyday technology. From predictive text and photo enhancement to automated translations, intelligent systems quietly assist billions of people each day.

At its essence, modern AI is not magic; it is the discipline of creating software systems capable of recognizing patterns, learning from data, and making informed decisions.

## How Modern Systems Learn
Traditional computer programs rely on strict, hand-written rules: if condition A happens, execute action B. In contrast, modern Machine Learning allows algorithms to learn rules directly from vast datasets.

By analyzing millions of examples, a neural network adjusts its internal parameters until it can accurately recognize spoken words, identify objects in photographs, or synthesize coherent text.

## Everyday Applications Shaping Tomorrow
Today AI powers voice assistants, optimizes supply chains, accelerates scientific discovery, and assists medical professionals in diagnosing imaging scans with unprecedented precision.

As these tools continue to evolve, understanding their foundational principles empowers us to use them thoughtfully and responsibly in our academic, professional, and creative endeavors.

## Conclusion
Artificial intelligence is a powerful collaborator, augmenting human ingenuity rather than replacing our innate creativity. By familiarizing ourselves with its core concepts today, we become active participants in shaping how technology serves humanity tomorrow.""",
    },
]

# Initialize session state with safe defaults
if "post" not in st.session_state:
    st.session_state["post"] = None
if "post_topic" not in st.session_state:
    st.session_state["post_topic"] = ""
if "post_tone" not in st.session_state:
    st.session_state["post_tone"] = "Friendly"
if "post_word_count" not in st.session_state:
    st.session_state["post_word_count"] = 500
if "recent_drafts" not in st.session_state:
    st.session_state["recent_drafts"] = list(DEFAULT_DRAFTS)
if "nav_view" not in st.session_state:
    st.session_state["nav_view"] = "New Article"
if "topic_input_val" not in st.session_state:
    st.session_state["topic_input_val"] = ""


def apply_editorial_styles() -> None:
    """Inject minimal editorial publishing CSS with high-contrast charcoal text."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;0,6..72,700;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        /* Color Palette & Base */
        :root {
            --bg-ivory: #FAF7F2;
            --sidebar-bg: #F4EFE6;
            --card-bg: #FDFBF7;
            --border-beige: #E6DFD3;
            --border-input: #DCD4C5;
            --charcoal-dark: #201C18;
            --charcoal-text: #282420;
            --charcoal-muted: #6E675D;
            --charcoal-subtle: #8A8377;
            --button-dark: #221F1B;
            --button-hover: #38332D;
            --pill-active: #E6DFD3;
        }

        /* App Background & Global Typography */
        .stApp {
            background-color: var(--bg-ivory) !important;
            color: var(--charcoal-dark) !important;
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Enforce charcoal text on all base elements */
        .stApp p, .stApp span, .stApp div, .stApp label, .stApp li {
            color: var(--charcoal-dark) !important;
        }

        /* Hide Streamlit header/footer */
        #MainMenu, footer, header {
            visibility: hidden;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--border-beige) !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.8rem;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }
        [data-testid="stSidebar"] h1 {
            display: none !important;
        }

        /* Sidebar Brand */
        .brand-header {
            display: flex;
            align-items: center;
            gap: 12px;
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.85rem;
            font-weight: 700;
            color: var(--charcoal-dark) !important;
            letter-spacing: -0.5px;
            margin-bottom: 2rem;
            padding-left: 0.2rem;
        }
        .brand-header svg {
            stroke: var(--charcoal-dark);
        }

        /* Sidebar Navigation Options - Complete hide of radio circles */
        [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child,
        [data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child,
        [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child,
        [data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            position: absolute !important;
        }

        [data-testid="stSidebar"] [data-baseweb="radio"],
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            width: 100% !important;
            padding: 10px 14px !important;
            border-radius: 10px !important;
            margin-bottom: 5px !important;
            cursor: pointer !important;
            background-color: transparent !important;
            transition: all 0.15s ease !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"]:hover,
        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background-color: #ECE5DA !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked),
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background-color: var(--pill-active) !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] *,
        [data-testid="stSidebar"] [data-testid="stRadio"] label * {
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) *,
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * {
            font-weight: 600 !important;
        }

        /* Mountain Art Illustration */
        .mountain-art-container {
            margin-top: 3.5rem;
            padding-top: 1rem;
            opacity: 0.7;
            text-align: center;
        }

        /* Typography - Editorial Style */
        .kicker {
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2.2px;
            color: var(--charcoal-subtle) !important;
            margin-bottom: 0.5rem;
        }
        .editorial-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 2.6rem;
            font-weight: 700;
            color: var(--charcoal-dark) !important;
            line-height: 1.18;
            letter-spacing: -0.8px;
            margin-top: 0;
            margin-bottom: 0.55rem;
        }
        .editorial-subtitle {
            font-size: 1.05rem;
            color: var(--charcoal-muted) !important;
            margin-bottom: 1.75rem;
            line-height: 1.5;
        }

        /* Labels */
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] span,
        [data-testid="stWidgetLabel"] label {
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }

        /* Text Input & Text Area - High Contrast */
        .stTextInput input,
        .stTextArea textarea {
            background-color: #FFFFFF !important;
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
            border: 1px solid var(--border-input) !important;
            border-radius: 12px !important;
            font-size: 1.02rem !important;
            padding: 14px 16px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .stTextInput input {
            min-height: 52px !important;
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            border-color: var(--charcoal-dark) !important;
            box-shadow: 0 0 0 1px var(--charcoal-dark) !important;
        }
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder {
            color: #8C8476 !important;
            -webkit-text-fill-color: #8C8476 !important;
            opacity: 1 !important;
        }

        /* Selectbox - High Contrast */
        div[data-baseweb="select"] {
            background-color: #FFFFFF !important;
            border: 1px solid var(--border-input) !important;
            border-radius: 12px !important;
        }
        div[data-baseweb="select"] * {
            background-color: #FFFFFF !important;
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
            font-size: 0.95rem !important;
        }
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {
            background-color: #FFFFFF !important;
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
        }

        /* Slider Controls */
        div[data-testid="stSlider"] div[data-testid="stTickBar"] span {
            color: var(--charcoal-muted) !important;
        }

        /* Primary Button */
        div[data-testid="stButton"] button[kind="primary"] {
            background-color: var(--button-dark) !important;
            color: #FAF7F2 !important;
            -webkit-text-fill-color: #FAF7F2 !important;
            border: 1px solid var(--button-dark) !important;
            border-radius: 28px !important;
            padding: 12px 32px !important;
            font-size: 1.02rem !important;
            font-weight: 600 !important;
            box-shadow: 0 3px 12px rgba(32, 28, 24, 0.12) !important;
            transition: all 0.18s ease-in-out !important;
        }
        div[data-testid="stButton"] button[kind="primary"] * {
            color: #FAF7F2 !important;
            -webkit-text-fill-color: #FAF7F2 !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background-color: var(--button-hover) !important;
            border-color: var(--button-hover) !important;
            transform: translateY(-1px);
        }

        /* Secondary Buttons & Download Button */
        div[data-testid="stButton"] button[kind="secondary"],
        .stDownloadButton button {
            background-color: #FFFFFF !important;
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
            border: 1px solid var(--border-input) !important;
            border-radius: 22px !important;
            padding: 8px 18px !important;
            font-size: 0.92rem !important;
            font-weight: 500 !important;
            transition: all 0.15s ease-in-out !important;
        }
        div[data-testid="stButton"] button[kind="secondary"] *,
        .stDownloadButton button * {
            color: var(--charcoal-dark) !important;
            -webkit-text-fill-color: var(--charcoal-dark) !important;
        }
        div[data-testid="stButton"] button[kind="secondary"]:hover,
        .stDownloadButton button:hover {
            background-color: #F7F3EA !important;
            border-color: var(--charcoal-dark) !important;
        }

        /* Side Cards (Tips & Drafts) using bordered containers */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            background-color: var(--card-bg) !important;
            border: 1px solid var(--border-beige) !important;
            border-radius: 16px !important;
            padding: 20px 22px !important;
            box-shadow: 0 2px 8px rgba(40, 36, 32, 0.02) !important;
            margin-bottom: 1.25rem !important;
        }
        .side-card-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--charcoal-dark) !important;
            margin-bottom: 14px;
        }
        .side-card-list {
            list-style: none;
            padding-left: 0;
            margin-bottom: 0;
        }
        .side-card-list li {
            position: relative;
            padding-left: 18px;
            font-size: 0.93rem;
            color: var(--charcoal-text) !important;
            line-height: 1.55;
            margin-bottom: 10px;
        }
        .side-card-list li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: var(--charcoal-subtle);
            font-size: 1.2rem;
            line-height: 1;
        }

        /* Draft card box */
        .draft-box {
            background-color: #FFFFFF;
            border: 1px solid var(--border-beige);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 8px;
        }
        .draft-title-text {
            font-weight: 600;
            font-size: 0.93rem;
            color: var(--charcoal-dark) !important;
            margin-bottom: 2px;
        }
        .draft-meta-text {
            font-size: 0.81rem;
            color: var(--charcoal-muted) !important;
        }

        /* Article Reader Paper Card */
        .article-paper {
            background-color: #FFFFFF;
            border: 1px solid var(--border-beige);
            border-radius: 18px;
            padding: 38px 44px;
            margin-top: 1.8rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 18px rgba(40, 36, 32, 0.03);
            line-height: 1.75;
        }
        .article-paper h1 {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 2.3rem;
            font-weight: 700;
            color: var(--charcoal-dark) !important;
            margin-top: 0;
            margin-bottom: 1rem;
            line-height: 1.22;
        }
        .article-paper h2 {
            font-family: 'Newsreader', Georgia, serif;
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--charcoal-dark) !important;
            margin-top: 2rem;
            margin-bottom: 0.75rem;
            border-bottom: 1px solid #EFE8DC;
            padding-bottom: 0.4rem;
        }
        .article-paper p {
            font-size: 1.05rem;
            color: var(--charcoal-text) !important;
            margin-bottom: 1.25rem;
            line-height: 1.75;
        }
        .article-meta-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 16px;
            background-color: #F4EFE6;
            color: var(--charcoal-muted) !important;
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def slugify(text: str) -> str:
    """Create a URL/filename-safe slug from text.

    Converts to lowercase, replaces spaces with hyphens,
    and preserves only letters, numbers, and hyphens.

    Args:
        text: Input string to slugify.

    Returns:
        A sanitized slug string.
    """
    cleaned = text.lower().strip()
    cleaned = re.sub(r"\s+", "-", cleaned)
    cleaned = re.sub(r"[^a-z0-9\-]", "", cleaned)
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")
    return cleaned or "blog-post"


def generate_post(topic: str, tone: str, word_count: int) -> str:
    """Call the Gemini API to generate a structured blog post.

    Args:
        topic: The topic for the blog post.
        tone: The tone of the post.
        word_count: Target approximate word count.

    Returns:
        The generated blog post as Markdown text.

    Raises:
        ValueError: If the response is empty or blocked.
        Exception: On API failure or connection error.
    """
    prompt = build_prompt(topic=topic, tone=tone, word_count=word_count)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
    except Exception as exc:
        # Graceful fallback if the specific model identifier is retired for new keys
        exc_str = str(exc).lower()
        if "no longer available" in exc_str or "not found" in exc_str:
            model = genai.GenerativeModel("gemini-3.5-flash")
            response = model.generate_content(prompt)
        else:
            raise

    try:
        content = response.text
    except Exception as exc:
        raise ValueError("empty_or_blocked") from exc

    if not content or not content.strip():
        raise ValueError("empty_or_blocked")

    return content.strip()


def run_generation(topic: str, tone: str, word_count: int) -> Optional[str]:
    """Execute post generation with user feedback and error handling.

    Args:
        topic: The topic of the blog post.
        tone: The selected writing tone.
        word_count: Target word count.

    Returns:
        The generated post string if successful, None otherwise.
    """
    try:
        with st.spinner("Writing your blog post..."):
            return generate_post(topic, tone, word_count)
    except ValueError as exc:
        if str(exc) == "empty_or_blocked":
            st.error("The model returned no text. Try a different topic or tone.")
        else:
            st.error("Something went wrong. Check the terminal for details.")
            traceback.print_exc()
    except Exception as exc:
        err_msg = str(exc).lower()
        if "quota" in err_msg or "429" in err_msg:
            st.error("Rate limit reached. Wait a minute and try again.")
        elif (
            "api key" in err_msg
            or "api_key" in err_msg
            or "401" in err_msg
            or "403" in err_msg
        ):
            st.error("The API key looks invalid. Check your .env file.")
        else:
            st.error("Something went wrong. Check the terminal for details.")
            traceback.print_exc()
    return None


# Apply custom styling
apply_editorial_styles()

# Sidebar: Branding and Navigation
with st.sidebar:
    st.markdown(
        """
        <div class="brand-header">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#201C18" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20.24 12.24a6 6 0 0 0-8.49-8.49L5 10.5V19h8.5z"/>
                <line x1="16" y1="8" x2="2" y2="22"/>
                <line x1="17.5" y1="15" x2="9" y2="15"/>
            </svg>
            <span>InkSpark</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("InkSpark")

    nav_options = ["New Article", "History", "My Drafts", "About"]

    selected_nav = st.radio(
        label="Navigation",
        options=nav_options,
        index=nav_options.index(st.session_state["nav_view"]),
        label_visibility="collapsed",
    )
    st.session_state["nav_view"] = selected_nav

    # Mountain landscape illustration at bottom of sidebar
    st.markdown(
        """
        <div class="mountain-art-container">
            <svg viewBox="0 0 280 110" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; max-width: 240px; opacity: 0.65;">
                <path d="M0,110 L0,90 Q40,65 80,78 T170,55 T230,72 T280,60 L280,110 Z" fill="#D8CFBF"/>
                <path d="M0,110 L0,98 Q50,82 100,92 T190,75 T250,88 T280,78 L280,110 Z" fill="#BEB4A2"/>
                <path d="M0,110 L0,105 Q60,94 120,102 T210,90 T265,98 T280,92 L280,110 Z" fill="#9C917E"/>
            </svg>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Check API Key Banner
if not api_key:
    st.error("API key not found. Create a .env file with GEMINI_API_KEY=your_key")


# Render based on navigation view
if st.session_state["nav_view"] == "New Article":
    # Two-column layout: Main Editor + Right Reference Cards
    col_main, col_right = st.columns([2.2, 1.0], gap="large")

    with col_main:
        st.markdown('<div class="kicker">INKSPARK</div>', unsafe_allow_html=True)
        st.markdown(
            '<h1 class="editorial-title">What are we writing today?</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="editorial-subtitle">Turn your ideas into well-structured blog posts with AI.</div>',
            unsafe_allow_html=True,
        )

        # Topic Input (Input 1: Topic)
        topic_input = st.text_input(
            "Topic",
            value=st.session_state.get("topic_input_val", ""),
            placeholder="e.g. How to start learning Python",
            max_chars=200,
            help="Enter the subject or question for your article.",
        )

        # Sub-row with Tone (Input 2) and Word Count (Input 3)
        col_tone, col_words = st.columns(2, gap="medium")

        tone_options = [
            "Friendly",
            "Formal",
            "Humorous",
            "Motivational",
            "Educational",
        ]

        current_tone_str = st.session_state.get("post_tone", "Friendly")
        default_tone_idx = (
            tone_options.index(current_tone_str)
            if current_tone_str in tone_options
            else 0
        )

        with col_tone:
            tone_input = st.selectbox(
                "Tone",
                options=tone_options,
                index=default_tone_idx,
            )

        with col_words:
            word_count_input = st.slider(
                "Word Count",
                min_value=300,
                max_value=1000,
                value=int(st.session_state.get("post_word_count", 500)),
                step=50,
                format="%d words",
            )

        # Generate Button (Input 4)
        st.write("")
        col_btn_l, col_btn_c, col_btn_r = st.columns([1, 1.6, 1])
        with col_btn_c:
            generate_clicked = st.button(
                "Generate Blog",
                type="primary",
                disabled=not bool(api_key),
                use_container_width=True,
            )

        # Handle Generate click
        if generate_clicked:
            clean_topic = topic_input.strip()
            if not clean_topic:
                st.warning("Please enter a topic first.")
                st.stop()
            else:
                new_post = run_generation(clean_topic, tone_input, word_count_input)
                if new_post:
                    st.session_state["post"] = new_post
                    st.session_state["post_topic"] = clean_topic
                    st.session_state["post_tone"] = tone_input
                    st.session_state["post_word_count"] = word_count_input

                    # Prepend to recent drafts
                    first_line = clean_topic.capitalize()
                    now_str = datetime.now().strftime("%b %d")
                    st.session_state["recent_drafts"].insert(
                        0,
                        {
                            "id": f"draft-{datetime.now().timestamp()}",
                            "title": first_line,
                            "date": now_str,
                            "word_count": word_count_input,
                            "tone": tone_input,
                            "content": new_post,
                        },
                    )
                    st.rerun()

        # Display Article Output only when non-empty
        if st.session_state.get("post") and st.session_state["post"].strip():
            st.markdown('<div class="article-paper">', unsafe_allow_html=True)

            meta_tone = st.session_state.get("post_tone", "Friendly")
            meta_words = st.session_state.get("post_word_count", 500)
            st.markdown(
                f'<div class="article-meta-badge">{meta_tone} &nbsp;•&nbsp; ~{meta_words} words &nbsp;•&nbsp; Markdown Ready</div>',
                unsafe_allow_html=True,
            )

            st.markdown(st.session_state["post"])
            st.markdown("</div>", unsafe_allow_html=True)

            # Action bar: Download, Regenerate, Clear
            slug = slugify(st.session_state.get("post_topic") or topic_input)
            download_filename = f"{slug}.md"

            col_down, col_regen, col_clr = st.columns([1.4, 1.0, 0.8], gap="small")

            with col_down:
                st.download_button(
                    label="Download as Markdown",
                    data=st.session_state["post"],
                    file_name=download_filename,
                    mime="text/markdown",
                    use_container_width=True,
                )

            with col_regen:
                regenerate_clicked = st.button(
                    "Regenerate",
                    use_container_width=True,
                )

            with col_clr:
                clear_clicked = st.button(
                    "Clear",
                    use_container_width=True,
                )

            if regenerate_clicked:
                regen_topic = st.session_state.get("post_topic") or topic_input.strip()
                regen_tone = st.session_state.get("post_tone") or tone_input
                regen_word_count = (
                    st.session_state.get("post_word_count") or word_count_input
                )

                if not regen_topic:
                    st.warning("Please enter a topic first.")
                    st.stop()

                regen_result = run_generation(
                    regen_topic, regen_tone, regen_word_count
                )
                if regen_result:
                    st.session_state["post"] = regen_result
                    st.rerun()

            if clear_clicked:
                st.session_state["post"] = None
                st.session_state["post_topic"] = ""
                st.session_state["post_tone"] = "Friendly"
                st.session_state["post_word_count"] = 500
                st.session_state["topic_input_val"] = ""
                st.rerun()

    # Right Column: Writing Tips and Recent Drafts
    with col_right:
        # Writing Tips Card
        with st.container(border=True):
            st.markdown(
                """
                <div class="side-card-title">Writing Tips</div>
                <ul class="side-card-list">
                    <li>Be specific with your topic.</li>
                    <li>Choose a tone that fits your audience.</li>
                    <li>Set a realistic word count.</li>
                    <li>Regenerate if you want a different take.</li>
                </ul>
                """,
                unsafe_allow_html=True,
            )

        # Recent Drafts Card
        with st.container(border=True):
            st.markdown(
                '<div class="side-card-title">Recent Drafts</div>',
                unsafe_allow_html=True,
            )

            for idx, draft in enumerate(st.session_state["recent_drafts"][:3]):
                st.markdown(
                    f"""
                    <div style="padding: 6px 0; border-bottom: 1px solid #ECE6DB; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: baseline;">
                            <span style="font-weight: 600; font-size: 0.94rem; color: #201C18;">{draft['title']}</span>
                            <span style="font-size: 0.78rem; color: #8A8377;">{draft.get('date', '')}</span>
                        </div>
                        <div style="font-size: 0.81rem; color: #6E675D; margin-top: 2px;">{draft.get('word_count', 500)} words • {draft.get('tone', 'Friendly')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Read Draft", key=f"read_draft_{idx}", use_container_width=True
                ):
                    st.session_state["post"] = draft["content"]
                    st.session_state["post_topic"] = draft["title"]
                    st.session_state["post_tone"] = draft.get("tone", "Friendly")
                    st.session_state["post_word_count"] = draft.get("word_count", 500)
                    st.session_state["topic_input_val"] = draft["title"]
                    st.rerun()

            st.write("")
            if st.button(
                "View All Archive", key="view_all_drafts", use_container_width=True
            ):
                st.session_state["nav_view"] = "My Drafts"
                st.rerun()


elif st.session_state["nav_view"] in ("History", "My Drafts"):
    view_title = (
        "Articles & Drafts Archive"
        if st.session_state["nav_view"] == "My Drafts"
        else "Generation History"
    )
    st.markdown(
        f'<div class="kicker">{st.session_state["nav_view"].upper()}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<h1 class="editorial-title">{view_title}</h1>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="editorial-subtitle">Browse, read, or export previous blog posts.</div>',
        unsafe_allow_html=True,
    )

    for idx, draft in enumerate(st.session_state["recent_drafts"]):
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #FDFBF7; border: 1px solid #E6DFD3; border-radius: 14px; padding: 18px 24px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <h3 style="font-family: 'Newsreader', serif; font-size: 1.4rem; margin: 0; color: #201C18;">{draft['title']}</h3>
                        <span style="font-size: 0.85rem; color: #6E675D;">{draft.get('date', '')}</span>
                    </div>
                    <div style="font-size: 0.88rem; color: #6E675D; margin-top: 4px; margin-bottom: 10px;">
                        {draft.get('word_count', 500)} words &nbsp;•&nbsp; {draft.get('tone', 'Friendly')} Tone
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_a, col_b, _ = st.columns([1, 1.4, 4])
            with col_a:
                if st.button("Open", key=f"open_archive_{idx}"):
                    st.session_state["post"] = draft["content"]
                    st.session_state["post_topic"] = draft["title"]
                    st.session_state["post_tone"] = draft.get("tone", "Friendly")
                    st.session_state["post_word_count"] = draft.get("word_count", 500)
                    st.session_state["topic_input_val"] = draft["title"]
                    st.session_state["nav_view"] = "New Article"
                    st.rerun()
            with col_b:
                st.download_button(
                    label="Download Markdown",
                    data=draft["content"],
                    file_name=f"{slugify(draft['title'])}.md",
                    mime="text/markdown",
                    key=f"dl_archive_{idx}",
                )


elif st.session_state["nav_view"] == "About":
    st.markdown('<div class="kicker">ABOUT INKSPARK</div>', unsafe_allow_html=True)
    st.markdown(
        '<h1 class="editorial-title">Editorial Publishing, Powered by AI</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="article-paper" style="margin-top: 1.5rem;">
            <h2>The InkSpark Philosophy</h2>
            <p>
                InkSpark is designed for writers, students, and thinkers who appreciate the craft of a well-structured essay.
                Rather than producing generic walls of text, InkSpark guides large language models to construct structured,
                engaging posts featuring a catchy title, compelling introduction, distinct thematic sections, and a clear,
                thoughtful conclusion.
            </p>
            <h2>Design Principles</h2>
            <p>
                We believe creative software should feel like high-grade stationery: quiet, dependable, and warm.
                InkSpark abandons high-saturation neon gradients and frantic animations in favor of warm ivory backgrounds,
                charcoal typography, and classical publication aesthetics.
            </p>
            <h2>Markdown Export Ready</h2>
            <p>
                Every generated article is formatted in standard GitHub Flavored Markdown, making it effortless to paste into
                static site generators (Hugo, Astro, Jekyll), publishing platforms (Medium, Substack, Ghost), or personal notes
                (Obsidian, Notion).
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
