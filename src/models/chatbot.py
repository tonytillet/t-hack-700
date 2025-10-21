#!/usr/bin/env python3
"""
Chatbot IA pour répondre aux questions sur la grippe et LUMEN
"""

class GrippeChatbot:
    """Chatbot spécialisé dans les questions sur la grippe et la plateforme LUMEN"""

    def __init__(self):
        """Initialise le chatbot avec sa base de connaissances"""
        self.knowledge_base = {
            "grippe": {
                "symptomes": "Fièvre, toux, maux de tête, courbatures, fatigue",
                "transmission": "Gouttelettes respiratoires, contact direct, surfaces contaminées",
                "prevention": "Vaccination, lavage des mains, port du masque, aération",
                "duree": "7-10 jours en moyenne, jusqu'à 2 semaines pour la fatigue"
            },
            "vaccination": {
                "efficacite": "60-70% d'efficacité contre les formes graves",
                "recommandations": "Personnes à risque, professionnels de santé, +65 ans",
                "periode": "Octobre à mars, idéalement avant décembre",
                "effets": "Réactions locales légères, rarement des effets systémiques"
            },
            "surveillance": {
                "indicateurs": "Urgences, sentinelles, Google Trends, Wikipedia",
                "seuils": "Critique ≥80, Élevé 60-79, Modéré 40-59, Faible <40",
                "frequence": "Mise à jour hebdomadaire, alertes en temps réel",
                "sources": "Santé Publique France, INSEE, Open-Meteo, Google"
            },
            "lumen": {
                "objectif": "Prédire les épidémies 1-2 mois à l'avance",
                "donnees": "Signaux faibles + données officielles + météo",
                "ia": "Random Forest avec features temporelles inter-années",
                "impact": "-40% pics d'urgences, +25% efficacité campagnes"
            }
        }

    def get_response(self, question):
        """Génère une réponse à la question de l'utilisateur"""
        question_lower = question.lower()

        # Recherche par mots-clés
        for category, info in self.knowledge_base.items():
            if any(keyword in question_lower for keyword in [category, "grippe", "vaccin", "surveillance", "lumen"]):
                if category == "grippe":
                    if "symptome" in question_lower:
                        return f"**Symptômes de la grippe :**\n{info['symptomes']}\n\n**Durée :** {info['duree']}"
                    elif "transmission" in question_lower or "contagieux" in question_lower:
                        return f"**Transmission de la grippe :**\n{info['transmission']}\n\n**Prévention :** {info['prevention']}"
                    else:
                        return f"**À propos de la grippe :**\n- **Symptômes :** {info['symptomes']}\n- **Transmission :** {info['transmission']}\n- **Prévention :** {info['prevention']}\n- **Durée :** {info['duree']}"

                elif category == "vaccination":
                    return f"**Vaccination contre la grippe :**\n- **Efficacité :** {info['efficacite']}\n- **Recommandations :** {info['recommandations']}\n- **Période :** {info['periode']}\n- **Effets secondaires :** {info['effets']}"

                elif category == "surveillance":
                    return f"**Surveillance grippale LUMEN :**\n- **Indicateurs :** {info['indicateurs']}\n- **Seuils d'alerte :** {info['seuils']}\n- **Fréquence :** {info['frequence']}\n- **Sources :** {info['sources']}"

                elif category == "lumen":
                    return f"**Plateforme LUMEN :**\n- **Objectif :** {info['objectif']}\n- **Données :** {info['donnees']}\n- **IA :** {info['ia']}\n- **Impact :** {info['impact']}"

        # Réponses par défaut
        if "bonjour" in question_lower or "salut" in question_lower:
            return "Bonjour ! Je suis l'assistant IA de LUMEN. Je peux vous aider avec des questions sur la grippe, la vaccination, la surveillance épidémiologique et la plateforme LUMEN. Que souhaitez-vous savoir ?"

        elif "aide" in question_lower or "help" in question_lower:
            return "**Comment puis-je vous aider ?**\n\nJe peux répondre à vos questions sur :\n- Les symptômes et la transmission de la grippe\n- La vaccination contre la grippe\n- Le système de surveillance LUMEN\n- Les indicateurs d'alerte et les seuils\n- Le fonctionnement de la plateforme\n\nPosez-moi votre question !"

        elif "merci" in question_lower:
            return "De rien ! N'hésitez pas si vous avez d'autres questions sur la surveillance grippale ou LUMEN."

        else:
            return "Je ne suis pas sûr de comprendre votre question. Je peux vous aider avec des informations sur la grippe, la vaccination, la surveillance épidémiologique et la plateforme LUMEN. Pouvez-vous reformuler votre question ?"
