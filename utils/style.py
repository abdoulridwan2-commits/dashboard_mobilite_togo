def inject_styles():
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
            --primary: #0f8f73;
            --primary-dark: #0b6b5f;
            --primary-light: #edf7f3;
            --accent: #f8cb4d;
            --text: #1a2728;
            --muted: #5d6f72;
            --card: #ffffff;
            --border: #dfe9e6;
            --bg: #eef4f1;
            --shadow: 0 10px 30px rgba(15, 143, 115, 0.08);
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: linear-gradient(180deg, #edf4f1 0%, #eff5f2 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f7fbfa 0%, #edf6f3 100%);
            border-right: 1px solid var(--border);
        }

        .block-container {
            padding-top: 0.5rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            max-width: 100% !important;
        }

        .top-banner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-height: 128px;
            width: 100%;
            margin: 0 0 1.2rem 0;
            border-radius: 0;
            background: linear-gradient(90deg, #0d7b66 0%, #0f8f73 38%, #2b9f62 100%);
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            padding: 0.8rem 1.25rem;
        }

        .top-banner::after {
            content: "";
            position: absolute;
            right: 0;
            top: 0;
            width: 24%;
            height: 100%;
            background: linear-gradient(120deg, rgba(255,255,255,0.03), rgba(0,0,0,0.06));
            clip-path: polygon(25% 0%, 100% 0%, 100% 100%, 0% 100%);
        }

        .banner-title {
            flex: 1;
            text-align: center;
            font-size: clamp(2rem, 2.4vw, 3.1rem);
            font-weight: 800;
            color: white;
            letter-spacing: 0.02em;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            z-index: 1;
        }

        .banner-left, .banner-right {
            width: 18%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1;
        }

        .logo-mark {
            width: 74px;
            height: 74px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f4c542, #d8a526);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0b604d;
            font-size: 2.1rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.15);
            font-weight: 900;
        }

        .banner-photo {
            width: 170px;
            height: 88px;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(0,0,0,0.16)),
                        url('https://images.unsplash.com/photo-1558980664-10e7170b5df9?auto=format&fit=crop&w=800&q=80') center/cover no-repeat;
            border: 2px solid rgba(255,255,255,0.2);
        }

        .metric-card {
            background: rgba(255,255,255,0.68);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow);
            height: 100%;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: clamp(1.7rem, 2vw, 2.5rem);
            font-weight: 800;
            color: var(--text);
            line-height: 1.1;
        }

        .metric-detail {
            color: var(--primary-dark);
            font-size: 0.78rem;
            font-weight: 600;
            margin-top: 0.35rem;
        }

        .panel {
            background: rgba(255,255,255,0.62);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: var(--shadow);
        }

        .nav-box {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(15,143,115,0.25);
            border-radius: 10px;
            padding: 0.5rem 0.75rem;
            margin: 0.4rem 0;
            cursor: pointer;
            color: var(--text);
        }

        .sidebar-logo {
            display: flex;
            align-items: center;
            gap: 0.9rem;
            margin: 0.8rem 0 1.5rem 0;
            padding: 0.5rem 0.2rem;
        }

        .sidebar-logo .mark {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #f2c763, #d9a229);
            color: #0c6a5f;
            font-size: 1.7rem;
            font-weight: 800;
        }

        .sidebar-logo .name {
            font-size: 2rem;
            font-weight: 800;
            color: #0c6a5f;
            letter-spacing: -0.02em;
        }

        .footer-note {
            margin-top: 1.5rem;
            text-align: center;
            font-size: 0.96rem;
            color: #2d3f41;
            font-weight: 700;
            padding-top: 0.7rem;
            border-top: 1px solid var(--border);
            font-style: italic;
        }

        .stRadio > div {
            gap: 0.5rem;
        }

        .stTabs [role="tablist"] {
            gap: 0.5rem;
        }

        .stTabs [role="tab"] {
            border-radius: 10px 10px 0 0;
            padding: 0.5rem 1rem;
        }

        .section-title {
            color: var(--primary-dark);
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .kicker {
            color: var(--muted);
            font-size: 0.8rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
