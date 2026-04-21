# AIDA - AI Decision Assistant

**AIDA** est une plateforme d'aide à la décision basée sur l'intelligence artificielle, conçue pour ingérer, analyser et recommander des actions métiers en fonction de vos données clients.

Ce projet est réalisé dans le cadre de la **Phase 1** du développement, suivant une méthodologie Agile/Scrum.

## 🎯 Vision du Produit
L'objectif est d'offrir une interface centralisée permettant aux managers et aux analystes :
1. D'importer des fichiers de données brutes (CSV).
2. De visualiser les KPI importants (clients à risque, CA, etc.).
3. D'obtenir des recommandations d'actions automatisées propulsées par IA.
4. De suivre et valider la réalisation des actions métiers de manière sécurisée et traçable.

## ⚙️ Stack Technique
Cette première ébauche fonctionnelle utilise **Python** et le framework **Streamlit** pour accélérer le développement des interfaces orientées data.

- **Backend / Frontend :** Python 3 / Streamlit
- **Traitement de l'information :** Pandas

## 🚀 Installation & Exécution (Local)

1. **Cloner le repository :**
```bash
git clone <URL_DU_REPO>
cd AIDA
```

2. **Créer et activer un environnement virtuel (recommandé) :**
```bash
python3 -m venv venv
# Mac/Linux :
source venv/bin/activate
# Windows :
venv\Scripts\activate
```

3. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application :**
```bash
streamlit run app.py
```
L'application s'ouvrira automatiquement dans votre navigateur (par défaut `http://localhost:8501`).

## 📚 Organisation des Epics (Scrum)
Le Product Backlog de cette application couvre 6 axes de développement majeurs :
- **Epic 1** : Ingestion et qualité des données
- **Epic 2** : Visualisation et compréhension
- **Epic 3** : Recommandations et aide à la décision
- **Epic 4** : Gestion des actions
- **Epic 5** : Sécurité et contrôle d’accès
- **Epic 6** : Traçabilité et qualité produit

---
*PS: This README completes [US-21]*
