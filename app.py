import sqlite3
import pandas as pd
import streamlit as st
import base64

# Page Configuration
st.set_page_config(
    page_title="CUSB CS Alumni Network",
    page_icon="🎓",
    layout="wide"
)

# Custom Styling & CSS
st.markdown("""
<style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 10px;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 15px;
    }
    .badge-tag {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

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
    conn.commit()
    conn.close()

init_db()

# Helper: Convert Uploaded File to Base64 String
def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return base64.b64encode(bytes_data).decode()
    return None

# --- DATABASE HELPER FUNCTIONS ---
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

# --- BRANDING & HEADER SECTION ---
col_logo, col_heading = st.columns([1, 4])

with col_logo:
    # CUSB Logo
    st.image("https://upload.wikimedia.org/wikipedia/en/2/22/Central_University_of_South_Bihar_logo.png", width=120)

with col_heading:
    st.markdown('<div class="main-title">Central University of South Bihar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Department of Computer Science | Alumni Network & Placement Directory</div>', unsafe_allow_html=True)
    st.markdown('<span class="badge-tag">NAAC Accredited A++</span> <span class="badge-tag">Gaya, Bihar</span>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Campus Banner Graphic
st.image("https://images.unsplash.com/photo-1541829070764-84a7d30dd3f3?auto=format&fit=crop&w=1200&q=80", caption="CUSB Campus View | Panchanpur, Gaya", use_container_width=True)

st.markdown("---")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Search Directory", 
    "📝 Register Profile", 
    "📊 Placement Analytics", 
    "🛡️ Admin Moderation"
])

# --- TAB 1: SEARCH DIRECTORY ---
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
        st.info("No approved alumni profiles available yet. Register a profile or use the Admin tab to approve entries.")

# --- TAB 2: REGISTER PROFILE ---
with tab2:
    st.header("Alumni Self-Registration Portal")
    st.markdown("Graduated from CUSB Computer Science? Register your details and upload your photo below to join the official network.")
    
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
            
        mentorship = st.radio(
            "Are you open to guiding current CUSB students for referrals/mentorship?", 
            ["Yes", "No"], 
            horizontal=True
        )
        
        submit_btn = st.form_submit_button("Submit Registration")
        
        if submit_btn:
            if name and company and role and email:
                photo_b64 = image_to_base64(photo_file) if photo_file else None
                add_alumnus(name, degree, passout_year, company, role, domain, email, linkedin, mentorship, photo_b64)
                st.success("🎉 Registration submitted! Your profile is pending moderation and will appear live once approved.")
            else:
                st.error("Please fill in all mandatory fields marked with *.")

# --- TAB 3: PLACEMENT ANALYTICS ---
with tab3:
    st.header("Placement & Industry Insights Dashboard")
    df = fetch_alumni(status='Approved')
    
    if not df.empty:
        col_m1, col_m2 = st.columns(2)
        
        with col_m1:
            st.subheader("Top Hiring Domains")
            domain_counts = df['domain'].value_counts()
            st.bar_chart(domain_counts)
            
        with col_m2:
            st.subheader("Graduation Year Distribution")
            year_counts = df['passout_year'].value_counts()
            st.line_chart(year_counts)
            
        st.subheader("Top Hiring Companies")
        company_counts = df['company'].value_counts().head(5)
        st.dataframe(company_counts, use_container_width=True)
    else:
        st.info("Analytics charts will display once approved alumni data is available.")

# --- TAB 4: ADMIN MODERATION PANEL ---
with tab4:
    st.header("🛡️ Departmental Admin Moderation Panel")
    
    admin_password = st.text_input("Enter Admin Passkey", type="password")
    
    if admin_password == "cusb2026":
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
