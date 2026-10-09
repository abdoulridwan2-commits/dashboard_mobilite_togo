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
            justify-content: center;
            min-height: 205px;
            width: 100%;
            margin: 0 0 1.4rem 0;
            border-radius: 8px;
            background: #f8fcfa;
            border: 1px solid #d8e9e2;
            box-shadow: 0 12px 28px rgba(15, 85, 64, 0.1);
            overflow: hidden;
        }

        .banner-copy {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-width: 0;
            width: 100%;
            padding: 1.5rem 1.25rem;
        }

        .top-banner h1.banner-title {
            max-width: 1040px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 0.06em;
            margin: 0;
            font-size: 1.85rem;
            font-weight: 800;
            color: #12485b;
            letter-spacing: 0;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            line-height: 1.12;
            overflow-wrap: break-word;
        }

        .banner-title-lead,
        .banner-title-location {
            display: block;
            font-size: 0.84em;
        }

        .banner-title-focus {
            display: block;
            color: #078746;
            font-size: 1.2em;
            line-height: 1.08;
        }

        .banner-accent {
            width: 88px;
            height: 4px;
            margin-top: 1.1rem;
            background: #15965e;
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
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            margin: 0.8rem 0 1.3rem 0;
            padding: 0.5rem 0.2rem 0.9rem 0.2rem;
            border-bottom: 1px solid rgba(15,143,115,0.18);
        }

        .sidebar-emblem {
            display: block;
            width: 76px;
            height: 92px;
            object-fit: contain;
            filter: drop-shadow(0 4px 8px rgba(10,120,90,0.12));
        }

        .sidebar-brand {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .sidebar-logo .name {
            font-size: 1.4rem;
            font-weight: 800;
            color: #0c6a5f;
            letter-spacing: -0.02em;
            text-align: center;
        }

        .sidebar-attribution {
            margin-top: 0.35rem;
            text-align: center;
            font-size: 0.65rem;
            line-height: 1.45;
            color: #5d6f72;
        }

        .sidebar-attribution a {
            color: #49615e;
            text-decoration: underline;
            text-underline-offset: 2px;
        }

        .sidebar-group-heading {
            color: #0d5b4d;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 0.6rem 0 0.7rem 0;
        }

        .sidebar-section-label {
            color: #2b4a4d;
            font-size: 1.1rem;
            font-weight: 700;
            margin: 1.1rem 0 0.5rem 0;
        }

        .nav-reset-holder {
            margin-top: 1.3rem;
            padding-top: 0.7rem;
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

        @media (max-width: 760px) {
            .banner-copy {
                padding: 1.35rem 1rem;
            }

            .top-banner h1.banner-title {
                font-size: 1.65rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
