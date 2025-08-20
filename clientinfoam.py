import streamlit as st
import pandas as pd

# Helper function to safely get a value from a Series, with default if key is missing or invalid
def safe_get(row, key, default=None, convert=None):
    if row is not None and key in row.index:
        value = row[key]
        if pd.notna(value):
            try:
                converted_value = convert(value) if convert else value
                # Format numeric values with commas if a conversion (e.g., float) is applied
                if convert in (float, int):
                    return f"{converted_value:,.2f}" if isinstance(converted_value, float) else f"{converted_value:,}"
                return converted_value
            except (ValueError, TypeError):
                st.session_state.setdefault('debug_issues', []).append(f"Invalid format for '{key}': {value}")
                return default
        else:
            st.session_state.setdefault('debug_issues', []).append(f"Null value for '{key}'")
            return default
    else:
        st.session_state.setdefault('debug_issues', []).append(f"Missing column '{key}'")
        return default

# Initialize session state for data and debug info
if 'masterlist' not in st.session_state:
    st.session_state.masterlist = pd.DataFrame(columns=[
        'Name', 'Account Key', 'Contract Number', 'Birthdate', 'Repayment Cycle',  # Fixed typo
        'Delay Days', 'Currency Code', 'Total Outstanding', 'Statement Balance',
        'Statement Minimum Payment',  # Fixed typo
        'Statement Overdue Amount', 'Installment Amount (01)',
        'Installment Amount (02)', 'Email (01)', 'Residence Add'
    ])
if 'debug_issues' not in st.session_state:
    st.session_state.debug_issues = []

# Main app
st.title("MASTER LIST CLIENT INFO SEARCH BAR")

# Create tabs
tab1, tab2 = st.tabs(["UPLOAD BUCKET 2 ML", "Search"])

with tab1:
    st.header("Data Source")
    uploaded_file = st.file_uploader("Upload XLSX", type="xlsx")
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            if not df.empty:
                st.session_state.masterlist = df
                st.success("Data uploaded successfully!")
            else:
                st.warning("Uploaded XLSX is empty!")
        except Exception as e:
            st.error(f"Error loading XLSX: {str(e)}")
    st.dataframe(st.session_state.masterlist)

    if st.button("Download Current Data as XLSX"):
        st.download_button(
            label="Download XLSX",
            data=st.session_state.masterlist.to_excel(index=False, engine='openpyxl'),
            file_name="data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

with tab2:
    st.header("Search Functionality")
    st.write("---")  # Spacer for organization
    
    # Name suggestion dropdown (replacing text input)
    available_names = st.session_state.masterlist['Name'].dropna().tolist() if not st.session_state.masterlist.empty else []
    selected_name = st.selectbox("Select a Name", options=[""] + available_names, key="name_suggestion", index=0)
    
    if not available_names:
        st.write("No names available. Please upload a valid XLSX with a 'Name' column.")
    
    # Use selected name from dropdown
    active_search = selected_name
    
    # Filter data (handled by selectbox filtering)
    row = None
    if active_search and not st.session_state.masterlist.empty:
        filtered = st.session_state.masterlist[st.session_state.masterlist['Name'].str.contains(active_search, case=False, na=False)]
        if not filtered.empty:
            row = filtered.iloc[0]
            st.success(f"Found match for '{active_search}'")
        else:
            st.warning("No match found for the selected name.")
    elif st.session_state.masterlist.empty:
        st.warning("No data available. Please upload an XLSX file first.")
    
    # Display debugging info for missing/invalid columns
    if row is not None and st.session_state.debug_issues:
        with st.expander("Debug: Issues with Data"):
            st.write("The following issues were found with the selected row:")
            for issue in st.session_state.debug_issues:
                st.write(f"- {issue}")
        st.session_state.debug_issues = []  # Reset after displaying
    
    # Display autofilled fields in an expander for organization with enhanced visibility
    if row is not None or st.session_state.masterlist.empty:
        with st.expander("Client Details", expanded=True):
            st.write("---")  # Spacer
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {safe_get(row, 'Name', '')}", unsafe_allow_html=True)
                st.markdown(f"**Account Key:** {safe_get(row, 'Account Key', '')}", unsafe_allow_html=True)
                st.markdown(f"**Contract Number:** {safe_get(row, 'Contract Number', '')}", unsafe_allow_html=True)
                st.markdown(f"**Birthdate:** {safe_get(row, 'Birthdate', None, lambda x: pd.to_datetime(x, errors='coerce')).strftime('%Y-%m-%d') if safe_get(row, 'Birthdate', None, lambda x: pd.to_datetime(x, errors='coerce')) else ''}", unsafe_allow_html=True)
                st.markdown(f"**Repayment Cycle:** {safe_get(row, 'Repayment Cycle', '')}", unsafe_allow_html=True)  # Fixed typo
                st.markdown(f"**Delay Days:** {safe_get(row, 'Delay Days', 0, lambda x: int(float(str(x)) if str(x).replace('.','').isdigit() else 0))}", unsafe_allow_html=True)
                st.markdown(f"**Currency Code:** {safe_get(row, 'Currency Code', '')}", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Total Outstanding:** {safe_get(row, 'Total Outstanding', 0.0, float)}", unsafe_allow_html=True)
                st.markdown(f"**Statement Balance:** {safe_get(row, 'Statement Balance', 0.0, float)}", unsafe_allow_html=True)
                st.markdown(f"**Statement Minimum Payment:** {safe_get(row, 'Statement Minum Payment', 0.0, float)}", unsafe_allow_html=True)  # Fixed typo
                st.markdown(f"**Statement Overdue Amount:** {safe_get(row, 'Statement Overdue Amount', 0.0, float)}", unsafe_allow_html=True)
                st.markdown(f"**Installment Amount (01):** {safe_get(row, 'Installment Amount (01)', 0.0, float)}", unsafe_allow_html=True)
                st.markdown(f"**Installment Amount (02):** {safe_get(row, 'Installment Amount (02)', 0.0, float)}", unsafe_allow_html=True)
                st.markdown(f"**Email (01):** {safe_get(row, 'Email (01)', '')}", unsafe_allow_html=True)
                st.markdown(f"**Residence Add:** {safe_get(row, 'Residence Add', '')}", unsafe_allow_html=True)
    
    # Display full masterlist below for reference
    st.write("---")  # Spacer
    st.subheader("Masterlist Preview")
    st.dataframe(st.session_state.masterlist)