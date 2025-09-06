import streamlit as st
from streamlit_option_menu import option_menu

def render_nav_banner(pages):
    st.markdown("## 内定者図鑑")

    def page_changed(*args):
        if st.session_state.nav_key:
            st.session_state.active_page = st.session_state.nav_key
    
    if 'active_page' not in st.session_state:
        st.session_state.active_page = "みんなの図鑑"
        
    option_menu(
        menu_title=None, 
        options=pages,
        icons=['people-fill', 'person-fill', 'pencil-square'],
        key="nav_key",
        on_change=page_changed,
        default_index=pages.index(st.session_state.active_page) if st.session_state.active_page in pages else 0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "5px 0px", 
                "background-color": "#FFFFFF", 
                "width": "100%",
                "border-top": "1px solid #E0E0E0", # タイトルとの区切り線
                "border-bottom": "1px solid #E0E0E0", # メニューとコンテンツの区切り線
                "margin-bottom": "2rem" # メニューとコンテンツ間のスペース
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin":"0px 4px",
                "--hover-color": "#eee"
            },
            "nav-link-selected": {
                "background-color": "#0078D4", 
                "color": "white!important"
            },
        }
    )
