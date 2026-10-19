import sqlite3
import pandas as pd
import streamlit as st
import base64

# Page Configuration
st.set_page_config(
    page_title="Central University of South Bihar | CS Alumni Directory",
    page_icon="🎓",
    layout="wide"
)

# Custom Header & Navigation Bar Styling
st.markdown("""
<style>
    .top-bar {
        background-color: #0056B3;
        color: white;
        padding: 6px 15px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: -60px;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 15px;
    }
    .top-bar a {
        color: white;
        text-decoration: none;
        margin-right: 15px;
    }
    .brand-title {
        color: #0F172A;
        font-family: 'Georgia', serif;
        font-size: 1.8rem;
        font-weight: 800;
        line-height: 1.2;
    }
    .brand-sub {
        color: #1E3A8A;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .brand-tagline {
        color: #475569;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-box {
        background-color: #FEF3C7;
        border: 1px solid #F59E0B;
        padding: 8px 12px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        color: #92400E;
    }
</style>

<div class="top-bar">
    <a href="#">[ RTI ]</a> | 
    <a href="#">[ Public Self Disclosure ]</a> | 
    <a href="#">✉ Webmail</a>
</div>
""", unsafe_allow_html=True)

# --- BRANDING HEADER WITH LOGOS ---
col_main_logo, col_badges = st.columns([3, 1])

with col_main_logo:
    c_logo, c_text = st.columns([1, 4])
    with c_logo:
        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135755.png", width=90)
    with c_text:
        st.markdown('<div class="brand-title">दक्षिण बिहार केन्द्रीय विश्वविद्यालय</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">Central University of South Bihar</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-tagline">(Established under the Central Universities Act, 2009) UGC Category I University</div>', unsafe_allow_html=True)

with col_badges:
    st.markdown("""
        <div class="badge-box">
            🌟 NAAC Accredited A++<br>
            <span style="font-size: 0.8rem; font-weight: normal;">5th Convocation Portal</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border-top: 2px solid #B91C1C; margin-top: 10px; margin-bottom: 15px;'>", unsafe_allow_html=True)

# --- LOCAL CONVOCATION BANNER IMAGE ---
st.image(
    "banner.jpeg", 
    caption="5th Convocation Ceremony | Central University of South Bihar, Gaya (12 October 2026)", 
    use_container_width=True
)

st.markdown("---")

# --- DATABASE SETUP ---
DB_NAME = "cusb_alumni.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS alumni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            degree TEXT NOT NULL,
            passout_year INTEGER NOT NULL,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            domain TEXT NOT NULL,
            email TEXT NOT NULL,
            linkedin TEXT,
            open_for_mentorship TEXT NOT NULL,
            photo_data TEXT,
            status TEXT DEFAULT 'Pending'
        )
    ''')
    try:
        c.execute("ALTER TABLE alumni ADD COLUMN photo_data TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

init_db()

def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

def add_alumnus(name, degree, year, company, role, domain, email, linkedin, mentorship, photo_data):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO alumni (name, degree, passout_year, company, role, domain, email, linkedin, open_for_mentorship, photo_data, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending')
    ''', (name, degree, year, company, role, domain, email, linkedin, mentorship, photo_data))
    conn.commit()
    conn.close()

def fetch_alumni(status='Approved'):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT * FROM alumni WHERE status='{status}'", conn)
    conn.close()
    return df

def update_alumni_status(alumni_id, new_status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE alumni SET status = ? WHERE id = ?", (new_status, alumni_id))
    conn.commit()
    conn.close()

def delete_alumnus(alumni_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM alumni WHERE id = ?", (alumni_id,))
    conn.commit()
    conn.close()

# --- NAVIGATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Search Directory", 
    "📝 Register Profile", 
    "📊 Placement Analytics", 
    "🛡️ Admin Moderation"
])

# TAB 1: SEARCH DIRECTORY
with tab1:
    st.header("Find & Connect with Alumni")
    df = fetch_alumni(status='Approved')
    
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            search_company = st.text_input("Filter by Company / Organization")
        with col2:
            search_domain = st.selectbox("Filter by Technical Domain", ["All"] + list(df['domain'].unique()))
        with col3:
            search_mentorship = st.selectbox("Open for Mentorship?", ["All", "Yes", "No"])
            
        filtered_df = df.copy()
        if search_company:
            filtered_df = filtered_df[filtered_df['company'].str.contains(search_company, case=False, na=False)]
        if search_domain != "All":
            filtered_df = filtered_df[filtered_df['domain'] == search_domain]
        if search_mentorship != "All":
            filtered_df = filtered_df[filtered_df['open_for_mentorship'] == search_mentorship]
            
        st.write(f"**Showing {len(filtered_df)} verified alumni profile(s):**")
        for idx, row in filtered_df.iterrows():
            with st.expander(f"📌 **{row['name']}** — {row['role']} at **{row['company']}** ({row['passout_year']})"):
                c_img, c_details = st.columns([1, 3])
                with c_img:
                    if row.get('photo_data') and pd.notna(row['photo_data']):
                        st.image(f"data:image/png;base64,{row['photo_data']}", width=120)
                    else:
                        st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
                with c_details:
                    st.write(f"🎓 **Degree:** {row['degree']}")
                    st.write(f"🏢 **Company:** {row['company']} | **Role:** {row['role']}")
                    st.write(f"🛠️ **Domain:** {row['domain']}")
                    st.write(f"✉️ **Email:** [{row['email']}](mailto:{row['email']})")
                    if row['linkedin']:
                        st.write(f"🔗 **LinkedIn:** [View Profile]({row['linkedin']})")
                    st.write(f"🤝 **Open for Mentorship/Referrals:** **{row['open_for_mentorship']}**")
    else:
        st.info("No approved alumni profiles available yet.")

# TAB 2: REGISTER PROFILE
with tab2:
    st.header("Alumni Self-Registration Portal")
    with st.form("alumni_reg_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Full Name *")
            degree = st.selectbox("Degree Completed *", [
                "M.Sc. Computer Science", 
                "M.Sc. Artificial Intelligence", 
                "Ph.D. Computer Science", 
                "Other"
            ])
            passout_year = st.number_input("Graduation Year *", min_value=2015, max_value=2030, value=2026)
            company = st.text_input("Current Company / Organization *")
            photo_file = st.file_uploader("Upload Profile Photo (Optional)", type=["jpg", "jpeg", "png"])
            
        with col_b:
            role = st.text_input("Job Title / Designation *")
            domain = st.selectbox("Primary Domain *", [
                "Software Engineering", 
                "Data Science / AI / ML", 
                "Cyber Security & Digital Forensics", 
                "Cloud & DevOps", 
                "Academia & Research", 
                "Other"
            ])
            email = st.text_input("Contact Email *")
            linkedin = st.text_input("LinkedIn Profile URL (Optional)")
            
        mentorship = st.radio("Are you open to guiding current CUSB students for referrals/mentorship?", ["Yes", "No"], horizontal=True)
        submit_btn = st.form_submit_button("Submit Registration")
        
        if submit_btn:
            if name and company and role and email:
                photo_b64 = image_to_base64(photo_file) if photo_file else None
                add_alumnus(name, degree, passout_year, company, role, domain, email, linkedin, mentorship, photo_b64)
                st.success("🎉 Registration submitted! Your profile is pending moderation and will appear live once approved.")
            else:
                st.error("Please fill in all mandatory fields marked with *.")

# TAB 3: PLACEMENT ANALYTICS
with tab3:
    st.header("Placement & Industry Insights Dashboard")
    df = fetch_alumni(status='Approved')
    if not df.empty:
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.subheader("Top Hiring Domains")
            st.bar_chart(df['domain'].value_counts())
        with col_m2:
            st.subheader("Graduation Year Distribution")
            st.line_chart(df['passout_year'].value_counts())
    else:
        st.info("Analytics will display once approved alumni data is available.")

# TAB 4: ADMIN MODERATION PANEL
with tab4:
    st.header("🛡️ Departmental Admin Moderation Panel")
    admin_password = st.text_input("Enter Admin Passkey", type="password")
    
    try:
        correct_password = st.secrets["ADMIN_PASSWORD"]
        is_authenticated = (admin_password == correct_password)
    except Exception:
        is_authenticated = False
        st.warning("⚠️ Admin password secret is not configured in Streamlit Cloud settings.")
        
    if is_authenticated:
        st.success("Admin access granted.")
        pending_df = fetch_alumni(status='Pending')
        st.subheader(f"Pending Approvals ({len(pending_df)})")
        
        if not pending_df.empty:
            for idx, row in pending_df.iterrows():
                with st.container():
                    st.write(f"**{row['name']}** | {row['degree']} ({row['passout_year']}) — {row['role']} at **{row['company']}**")
                    col_btn1, col_btn2, _ = st.columns([1, 1, 4])
                    with col_btn1:
                        if st.button("Approve", key=f"app_{row['id']}"):
                            update_alumni_status(row['id'], 'Approved')
                            st.rerun()
                    with col_btn2:
                        if st.button("Reject / Delete", key=f"del_{row['id']}"):
                            delete_alumnus(row['id'])
                            st.rerun()
                    st.divider()
        else:
            st.info("No pending registrations to review.")
    elif admin_password:
        st.error("Incorrect passkey. Please check and try again.")
    else:
        st.info("Enter the passkey to manage pending profiles.")
