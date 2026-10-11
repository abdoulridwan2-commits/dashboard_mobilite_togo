def inject_styles():
    import streamlit as st

    st.markdown(
        """
        <style>
        :root {
            --primary: #0f8f73;
            --primary-dark: #0a614e;
            --primary-light: #e8f5f0;
            --accent: #f4c542;
            --accent-dark: #d4a409;
            --blue: #2b6cb0;
            --blue-light: #ebf4ff;
            --purple: #7b2cbf;
            --purple-light: #f3e8ff;
            --text: #1a2728;
            --muted: #5d6f72;
            --card: #ffffff;
            --border: #e2ece7;
            --bg: #f8faf9;
            --shadow-sm: 0 2px 6px rgba(15, 143, 115, 0.05);
            --shadow-md: 0 8px 24px rgba(15, 143, 115, 0.08);
        }

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fdfefe 0%, #f4f8f6 100%);
            border-right: 1px solid var(--border);
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100% !important;
        }

        /* BANDEAU VERT INSTITUTIONNEL */
        .top-banner {
            position: relative;
            background: linear-gradient(135deg, #0a614e 0%, #0f8f73 55%, #149c7f 100%);
            color: #ffffff;
            border-radius: 14px;
            padding: 1.8rem 2.2rem;
            margin-bottom: 1.8rem;
            box-shadow: 0 10px 30px rgba(10, 97, 78, 0.18);
            border: 1px solid rgba(255, 255, 255, 0.15);
            overflow: hidden;
        }

        .banner-copy {
            position: relative;
            z-index: 2;
        }

        .banner-badge {
            display: inline-block;
            background: rgba(244, 197, 66, 0.22);
            color: #ffdf79;
            border: 1px solid rgba(244, 197, 66, 0.45);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 0.6rem;
            text-transform: uppercase;
        }

        .banner-title {
            color: #ffffff !important;
            font-size: clamp(1.6rem, 2.4vw, 2.2rem);
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.15;
            margin: 0 0 0.35rem 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.12);
        }

        .banner-subtitle {
            color: #d8f3e9;
            font-size: 1rem;
            font-weight: 500;
            margin: 0 0 0.8rem 0;
            opacity: 0.95;
        }

        .banner-accent-bar {
            width: 72px;
            height: 4px;
            background: #f4c542;
            border-radius: 2px;
        }

        /* CARTES MÉTRIQUES */
        .metric-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.1rem 1.25rem;
            box-shadow: var(--shadow-sm);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: #cde4db;
        }

        .metric-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.4rem;
        }

        .metric-label {
            color: var(--muted);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .metric-icon {
            font-size: 1.25rem;
            opacity: 0.85;
        }

        .metric-value {
            font-size: clamp(1.6rem, 2.2vw, 2.1rem);
            font-weight: 800;
            color: var(--text);
            line-height: 1.1;
            margin: 0.2rem 0;
            font-feature-settings: "tnum";
        }

        .metric-detail {
            color: var(--primary);
            font-size: 0.8rem;
            font-weight: 600;
            margin-top: 0.25rem;
        }

        .metric-help {
            color: #7a8c8f;
            font-size: 0.72rem;
            margin-top: 0.2rem;
            font-style: italic;
        }

        /* PANNEAUX ET CONTENEURS */
        .panel {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.25rem;
            box-shadow: var(--shadow-sm);
            margin-bottom: 1.2rem;
        }

        .section-header {
            margin: 1.4rem 0 0.8rem 0;
            border-bottom: 2px solid #eef5f2;
            padding-bottom: 0.5rem;
        }

        .section-title {
            color: var(--primary-dark);
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 0.85rem;
            margin-top: 0.2rem;
        }

        /* BARRE LATÉRALE */
        .sidebar-logo {
            display: flex;
            align-items: center;
            gap: 0.85rem;
            padding: 0.5rem 0.2rem 1rem 0.2rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--border);
        }

        .sidebar-emblem {
            width: 48px;
            height: 60px;
            object-fit: contain;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.08));
        }

        .sidebar-brand .name {
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--primary-dark);
            letter-spacing: -0.02em;
            line-height: 1.1;
        }

        .sidebar-brand .subname {
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--accent-dark);
            margin-top: 0.1rem;
        }

        .sidebar-attribution {
            font-size: 0.62rem;
            color: #8c9ea0;
            margin-top: 0.2rem;
        }

        .sidebar-attribution a {
            color: #6d8284;
            text-decoration: none;
        }

        .sidebar-nav-title {
            font-size: 0.7rem;
            font-weight: 700;
            color: var(--muted);
            letter-spacing: 0.08em;
            margin: 0.6rem 0 0.4rem 0;
            text-transform: uppercase;
        }

        .nav-reset-holder {
            margin: 1.2rem 0 1rem 0;
            padding-top: 0.5rem;
            border-top: 1px dashed var(--border);
        }

        .sidebar-quote-box {
            margin-top: 2rem;
            padding: 0.9rem;
            background: linear-gradient(135deg, #eaf6f2 0%, #f4fbf8 100%);
            border-radius: 10px;
            border: 1px solid #cce8dd;
            border-left: 4px solid var(--primary);
        }

        .quote-flag-bar {
            width: 32px;
            height: 3px;
            background: #f4c542;
            margin-bottom: 0.4rem;
            border-radius: 2px;
        }

        .quote-text {
            color: #0d5c4b;
            font-size: 0.82rem;
            font-style: italic;
            font-weight: 600;
            line-height: 1.35;
            margin: 0;
        }

        /* ENCADRÉ DE LIMITATION MÉTHODOLOGIQUE */
        .limitation-box {
            background: #fbfcfe;
            border-left: 4px solid var(--blue);
            border-top: 1px solid var(--border);
            border-right: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin: 1rem 0;
        }

        .limitation-title {
            color: var(--blue);
            font-weight: 700;
            font-size: 0.88rem;
            margin-bottom: 0.25rem;
        }

        .limitation-text {
            color: #3d5254;
            font-size: 0.82rem;
            line-height: 1.45;
        }

        /* PIED DE PAGE */
        .footer-note {
            margin-top: 2.5rem;
            text-align: center;
            font-size: 0.88rem;
            color: var(--muted);
            padding: 1.2rem 0;
            border-top: 1px solid var(--border);
        }

        /* ONGLETS ET SÉLECTEURS */
        .stTabs [role="tab"] {
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--muted);
            padding: 0.6rem 1.2rem;
        }

        .stTabs [aria-selected="true"] {
            color: var(--primary) !important;
            border-bottom-color: var(--primary) !important;
        }

        /* FILTRES DANS EXPANDER */
        .filter-panel {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.8rem 1rem;
            margin-bottom: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

