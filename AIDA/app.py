import streamlit as st
import pandas as pd

# Set up page configurations
st.set_page_config(
    page_title="AIDA | AI Decision Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium look
st.markdown("""
<style>
    /* Styling headers */
    .premium-header {
        font-family: 'Inter', sans-serif;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    /* Metrics box */
    .metric-box {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-title {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #0F172A;
    }
</style>
""", unsafe_allow_html=True)

# Main Application
def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🤖 AIDA")
        st.caption("AI Decision Assistant")
        st.divider()
        page = st.radio("Navigation", ["📊 Dashboard", "📁 Ingérer des données", "🎯 Recommandations", "⚙️ Paramètres"])
        st.divider()
        st.success("Statut: Connecté en tant que Manager")

    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "📁 Ingérer des données":
        show_data_ingestion()
    elif page == "🎯 Recommandations":
        st.info("Module de recommandations en cours de développement (US-11)")
    elif page == "⚙️ Paramètres":
        st.info("Gestion des accès utilisateurs en cours de développement (US-17)")

def show_data_ingestion():
    st.markdown("<h2 class='premium-header'>📁 Importation de données clients (CSV)</h2>", unsafe_allow_html=True)
    st.write("Veuillez charger le fichier contenant les données métier à analyser.")
    
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Fichier importé avec succès !")
            
            st.subheader("Prévisualisation des données")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.info(f"Le jeu de données contient {df.shape[0]} lignes et {df.shape[1]} colonnes.")
            
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

def show_dashboard():
    st.markdown("<h2 class='premium-header'>📊 Aperçu Global des Performances</h2>", unsafe_allow_html=True)
    
    # Placeholder KPI row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('''
            <div class="metric-box">
                <div class="metric-title">Total Clients</div>
                <div class="metric-value">--</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown('''
            <div class="metric-box">
                <div class="metric-title">Chiffre d'Affaires</div>
                <div class="metric-value">--</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        st.markdown('''
            <div class="metric-box">
                <div class="metric-title">Clients à Risque</div>
                <div class="metric-value">--</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with col4:
        st.markdown('''
            <div class="metric-box">
                <div class="metric-title">Actions Réalisées</div>
                <div class="metric-value">--</div>
            </div>
        ''', unsafe_allow_html=True)

    st.write("---")
    st.warning("Veuillez charger des données via le menu 'Ingérer des données' pour afficher les KPI réels.")

if __name__ == "__main__":
    main()
