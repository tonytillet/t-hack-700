import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import numpy as np
import json

# Configuration de la page
st.set_page_config(
    page_title="LUMEN - Alerte Grippe",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Fonction de chargement des données avec cache
@st.cache_data
def load_predictions():
    """Charge les prédictions depuis le fichier parquet"""
    try:
        df = pd.read_parquet('data/predictions/predictions.parquet')
        df['date'] = pd.to_datetime(df['date'])
        df['target_date'] = pd.to_datetime(df['target_date'])
        df['prediction_date'] = pd.to_datetime(df['prediction_date'])
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None

@st.cache_data
def load_geojson():
    """Charge le GeoJSON des départements français"""
    try:
        with open('data/departements.geojson', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"Impossible de charger la carte de France : {e}")
        return None

# Fonction pour calculer le niveau d'alerte
def get_alert_level(value):
    """Retourne le niveau d'alerte basé sur le nombre de cas"""
    if value > 150:
        return "Rouge", "#dc3545"
    elif value > 100:
        return "Orange", "#fd7e14"
    elif value > 50:
        return "Jaune", "#ffc107"
    else:
        return "Vert", "#28a745"

# Fonction pour calculer les métriques globales
def calculate_metrics(df, selected_date):
    """Calcule les métriques KPI pour une date donnée"""
    # Filtrer les données pour la date sélectionnée
    df_date = df[df['date'] == selected_date].copy()

    if len(df_date) == 0:
        return None

    # Métrique 1 : Total national des cas
    total_cases = df_date['y_target'].sum()

    # Métrique 2 : Nombre de départements en alerte rouge
    red_alert_count = len(df_date[df_date['y_target'] > 150])

    # Métrique 3 : Tendance hebdomadaire
    week_ago = selected_date - timedelta(days=7)
    df_week_ago = df[df['date'] == week_ago]

    if len(df_week_ago) > 0:
        total_week_ago = df_week_ago['y_target'].sum()
        trend_pct = ((total_cases - total_week_ago) / total_week_ago * 100) if total_week_ago > 0 else 0

        if trend_pct > 5:
            trend = "↗️ Hausse"
            trend_color = "inverse"
        elif trend_pct < -5:
            trend = "↘️ Baisse"
            trend_color = "normal"
        else:
            trend = "→ Stable"
            trend_color = "off"
    else:
        trend = "→ N/A"
        trend_color = "off"
        trend_pct = 0

    # Métrique 4 : Précision du modèle (MAE sur les 30 derniers jours)
    date_30_days_ago = selected_date - timedelta(days=30)
    df_recent = df[(df['date'] >= date_30_days_ago) & (df['date'] <= selected_date)]
    mae = df_recent['abs_error'].mean() if len(df_recent) > 0 else 0

    return {
        'total_cases': total_cases,
        'red_alert_count': red_alert_count,
        'trend': trend,
        'trend_pct': trend_pct,
        'trend_color': trend_color,
        'mae': mae
    }

# Chargement des données
df = load_predictions()

if df is not None:
    # Titre principal
    st.title("🧠 LUMEN - Système d'Alerte Grippe Prédictif")
    st.markdown("---")

    # Sidebar pour les filtres
    with st.sidebar:
        st.header("Filtres")

        # Sélecteur de date
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()

        selected_date = st.date_input(
            "Date de référence",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )
        selected_date = pd.Timestamp(selected_date)

        st.markdown("---")
        st.markdown("### À propos")
        st.markdown("""
        **LUMEN** prédit les cas d'urgences liées à la grippe
        à J+7 pour tous les départements français.

        **Niveaux d'alerte :**
        - 🔴 Rouge : > 150 cas
        - 🟠 Orange : 100-150 cas
        - 🟡 Jaune : 50-100 cas
        - 🟢 Vert : < 50 cas
        """)

    # Calcul des métriques
    metrics = calculate_metrics(df, selected_date)

    if metrics:
        # Section 1 : Dashboard KPI
        st.header("📊 Tableau de Bord National")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="Cas d'urgences (total)",
                value=f"{int(metrics['total_cases']):,}",
                delta=None
            )

        with col2:
            st.metric(
                label="Départements en alerte 🔴",
                value=f"{metrics['red_alert_count']} / 96",
                delta=None
            )

        with col3:
            st.metric(
                label="Tendance hebdomadaire",
                value=metrics['trend'],
                delta=f"{metrics['trend_pct']:.1f}%",
                delta_color=metrics['trend_color']
            )

        with col4:
            st.metric(
                label="Précision modèle (MAE)",
                value=f"{metrics['mae']:.2f}",
                delta=None
            )

        st.markdown("---")

        # Section 2 : Carte de France interactive
        st.header("🗺️ Carte de France Interactive")

        # Charger le GeoJSON
        geojson_data = load_geojson()

        if geojson_data:
            # Filtrer les données pour la date sélectionnée
            df_map = df[df['date'] == selected_date].copy()

            # Ajouter les niveaux d'alerte
            df_map['alert_level'] = df_map['y_target'].apply(lambda x: get_alert_level(x)[0])

            # Créer la carte choroplèthe
            fig_map = px.choropleth(
                df_map,
                geojson=geojson_data,
                locations='department',
                featureidkey='properties.code',
                color='y_target',
                color_continuous_scale=[
                    [0, '#28a745'],      # Vert
                    [0.33, '#ffc107'],   # Jaune
                    [0.66, '#fd7e14'],   # Orange
                    [1, '#dc3545']       # Rouge
                ],
                range_color=[0, 200],
                labels={'y_target': 'Cas d\'urgences'},
                hover_name='department',
                hover_data={
                    'department': False,
                    'y_target': ':.0f',
                    'prediction': ':.0f'
                }
            )

            fig_map.update_geos(
                fitbounds="locations",
                visible=False
            )

            fig_map.update_layout(
                title=f"Carte des alertes par département - {selected_date.strftime('%d/%m/%Y')}",
                height=700,
                margin={"r": 0, "t": 50, "l": 0, "b": 0}
            )

            st.plotly_chart(fig_map, use_container_width=True)

            # Légende des niveaux d'alerte
            col_legend1, col_legend2, col_legend3, col_legend4 = st.columns(4)
            with col_legend1:
                st.markdown("🟢 **Vert** : < 50 cas")
            with col_legend2:
                st.markdown("🟡 **Jaune** : 50-100 cas")
            with col_legend3:
                st.markdown("🟠 **Orange** : 100-150 cas")
            with col_legend4:
                st.markdown("🔴 **Rouge** : > 150 cas")

        else:
            # Fallback si le GeoJSON n'est pas disponible
            st.warning("Carte GeoJSON non disponible. Affichage du Top 20 des départements.")

            df_map = df[df['date'] == selected_date].copy()
            df_map_sorted = df_map.sort_values('y_target', ascending=True).tail(20)

            fig_map = go.Figure()

            for idx, row in df_map_sorted.iterrows():
                alert_level, color = get_alert_level(row['y_target'])
                fig_map.add_trace(go.Bar(
                    y=[row['department']],
                    x=[row['y_target']],
                    orientation='h',
                    name=row['department'],
                    marker=dict(color=color),
                    hovertemplate=(
                        f"<b>Département {row['department']}</b><br>" +
                        f"Cas réels: {row['y_target']:.0f}<br>" +
                        f"Prédiction J+7: {row['prediction']:.0f}<br>" +
                        f"Niveau: {alert_level}<br>" +
                        "<extra></extra>"
                    ),
                    showlegend=False
                ))

            fig_map.update_layout(
                title=f"Top 20 départements les plus touchés - {selected_date.strftime('%d/%m/%Y')}",
                xaxis_title="Nombre de cas d'urgences",
                yaxis_title="Département",
                height=600,
                hovermode='closest'
            )

            st.plotly_chart(fig_map, use_container_width=True)

        st.markdown("---")

        # Section 3 : Graphique temporel avec prédictions
        st.header("📈 Évolution Temporelle et Prédictions")

        # Sélecteur de département
        departments = sorted(df['department'].unique())
        selected_dept = st.selectbox(
            "Sélectionnez un département",
            departments,
            index=departments.index('75') if '75' in departments else 0
        )

        # Filtrer les données pour le département sélectionné
        df_dept = df[df['department'] == selected_dept].sort_values('date')

        # Créer le graphique temporel
        fig_time = go.Figure()

        # Ligne des valeurs réelles
        fig_time.add_trace(go.Scatter(
            x=df_dept['date'],
            y=df_dept['y_target'],
            mode='lines',
            name='Valeurs réelles',
            line=dict(color='#0066cc', width=2),
            hovertemplate='Date: %{x|%d/%m/%Y}<br>Cas réels: %{y:.0f}<extra></extra>'
        ))

        # Ligne des prédictions
        fig_time.add_trace(go.Scatter(
            x=df_dept['date'],
            y=df_dept['prediction'],
            mode='lines',
            name='Prédictions J+7',
            line=dict(color='#ff6b35', width=2, dash='dot'),
            hovertemplate='Date: %{x|%d/%m/%Y}<br>Prédiction: %{y:.0f}<extra></extra>'
        ))

        # Ajouter une ligne verticale pour la date sélectionnée avec add_shape
        y_max = max(df_dept['y_target'].max(), df_dept['prediction'].max())
        fig_time.add_shape(
            type="line",
            x0=selected_date, x1=selected_date,
            y0=0, y1=y_max * 1.1,
            line=dict(color="green", width=2, dash="dash")
        )
        fig_time.add_annotation(
            x=selected_date,
            y=y_max * 1.1,
            text="Aujourd'hui",
            showarrow=False,
            yshift=10,
            font=dict(color="green")
        )

        # Ajouter les seuils d'alerte avec add_shape
        fig_time.add_shape(
            type="line",
            x0=df_dept['date'].min(), x1=df_dept['date'].max(),
            y0=150, y1=150,
            line=dict(color="#dc3545", width=1, dash="dash")
        )
        fig_time.add_annotation(
            x=df_dept['date'].max(),
            y=150,
            text="Seuil rouge",
            showarrow=False,
            xshift=50,
            font=dict(color="#dc3545", size=10)
        )

        fig_time.add_shape(
            type="line",
            x0=df_dept['date'].min(), x1=df_dept['date'].max(),
            y0=100, y1=100,
            line=dict(color="#fd7e14", width=1, dash="dash")
        )
        fig_time.add_annotation(
            x=df_dept['date'].max(),
            y=100,
            text="Seuil orange",
            showarrow=False,
            xshift=50,
            font=dict(color="#fd7e14", size=10)
        )

        fig_time.add_shape(
            type="line",
            x0=df_dept['date'].min(), x1=df_dept['date'].max(),
            y0=50, y1=50,
            line=dict(color="#ffc107", width=1, dash="dash")
        )
        fig_time.add_annotation(
            x=df_dept['date'].max(),
            y=50,
            text="Seuil jaune",
            showarrow=False,
            xshift=50,
            font=dict(color="#ffc107", size=10)
        )

        fig_time.update_layout(
            title=f"Département {selected_dept} - Cas réels vs Prédictions",
            xaxis_title="Date",
            yaxis_title="Nombre de cas d'urgences",
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig_time, use_container_width=True)

        # Afficher la prédiction J+7 pour ce département
        latest_prediction = df_dept[df_dept['date'] == selected_date]['prediction'].values
        if len(latest_prediction) > 0:
            pred_value = latest_prediction[0]
            alert_level, color = get_alert_level(pred_value)

            st.markdown(f"""
            <div style='background-color: {color}; color: white; padding: 15px; border-radius: 10px; text-align: center;'>
                <h3>Prédiction J+7 pour le département {selected_dept}</h3>
                <h2>{pred_value:.0f} cas attendus</h2>
                <h3>Niveau d'alerte : {alert_level}</h3>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Section 4 : Comparaison régionale (Top 10)
        st.header("🏆 Top 10 Départements")

        col_top1, col_top2 = st.columns(2)

        with col_top1:
            st.subheader("Les plus touchés actuellement")
            df_top = df[df['date'] == selected_date].nlargest(10, 'y_target')[['department', 'y_target']]

            fig_top = px.bar(
                df_top,
                x='y_target',
                y='department',
                orientation='h',
                color='y_target',
                color_continuous_scale=['#28a745', '#ffc107', '#fd7e14', '#dc3545'],
                labels={'y_target': 'Cas', 'department': 'Département'}
            )
            fig_top.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_top, use_container_width=True)

        with col_top2:
            st.subheader("Prédictions J+7 les plus élevées")
            df_pred_top = df[df['date'] == selected_date].nlargest(10, 'prediction')[['department', 'prediction']]

            fig_pred_top = px.bar(
                df_pred_top,
                x='prediction',
                y='department',
                orientation='h',
                color='prediction',
                color_continuous_scale=['#28a745', '#ffc107', '#fd7e14', '#dc3545'],
                labels={'prediction': 'Prédiction', 'department': 'Département'}
            )
            fig_pred_top.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_pred_top, use_container_width=True)

        st.markdown("---")

        # Section 5 : Timeline des épidémies
        st.header("⏱️ Timeline des Épidémies")

        # Agréger les données par date pour voir l'évolution nationale
        df_timeline = df.groupby('date').agg({
            'y_target': 'sum',
            'prediction': 'sum'
        }).reset_index()

        # Séparer par année
        df_timeline['year'] = df_timeline['date'].dt.year

        fig_timeline = px.area(
            df_timeline,
            x='date',
            y='y_target',
            color='year',
            title="Évolution des cas d'urgences au niveau national",
            labels={'y_target': 'Total cas', 'date': 'Date', 'year': 'Année'},
            color_discrete_sequence=['#0066cc', '#ff6b35']
        )

        fig_timeline.update_layout(height=400)
        st.plotly_chart(fig_timeline, use_container_width=True)

        st.markdown("---")

        # Section 6 : Performance du modèle
        st.header("🎯 Performance du Modèle")

        col_perf1, col_perf2 = st.columns(2)

        with col_perf1:
            st.subheader("Distribution des erreurs")

            # Histogramme des erreurs
            fig_error_dist = px.histogram(
                df,
                x='error',
                nbins=50,
                title="Distribution des erreurs de prédiction",
                labels={'error': 'Erreur', 'count': 'Fréquence'},
                color_discrete_sequence=['#0066cc']
            )
            fig_error_dist.update_layout(height=400)
            st.plotly_chart(fig_error_dist, use_container_width=True)

        with col_perf2:
            st.subheader("Valeurs réelles vs Prédictions")

            # Scatter plot
            df_sample = df.sample(min(1000, len(df)))  # Échantillon pour performance

            fig_scatter = px.scatter(
                df_sample,
                x='y_target',
                y='prediction',
                color='abs_error',
                color_continuous_scale='Reds',
                title="Prédictions vs Valeurs réelles",
                labels={'y_target': 'Valeur réelle', 'prediction': 'Prédiction', 'abs_error': 'Erreur absolue'}
            )

            # Ligne de référence parfaite
            max_val = max(df_sample['y_target'].max(), df_sample['prediction'].max())
            fig_scatter.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                name='Prédiction parfaite',
                line=dict(color='red', dash='dash')
            ))

            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Métriques de performance globale
        st.subheader("Métriques globales")
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        mae_global = df['abs_error'].mean()
        rmse_global = np.sqrt((df['error'] ** 2).mean())

        # R² calculation
        ss_res = ((df['y_target'] - df['prediction']) ** 2).sum()
        ss_tot = ((df['y_target'] - df['y_target'].mean()) ** 2).sum()
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        with col_m1:
            st.metric("MAE (Erreur Absolue Moyenne)", f"{mae_global:.2f}")

        with col_m2:
            st.metric("RMSE (Erreur Quadratique)", f"{rmse_global:.2f}")

        with col_m3:
            st.metric("R² Score", f"{r2:.3f}")

        with col_m4:
            precision_pct = (1 - (mae_global / df['y_target'].mean())) * 100
            st.metric("Précision", f"{precision_pct:.1f}%")

    else:
        st.warning("Aucune donnée disponible pour la date sélectionnée")

else:
    st.error("Impossible de charger les données. Vérifiez que le fichier 'data/predictions/predictions.parquet' existe.")
