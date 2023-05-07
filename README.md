# Buggy Boo Le Grand Sage
Ce projet a pour but d'utiliser GPT 3.5 pour répondre aux questions des étudiants en informatique en utilisant les documents pdf des cours.

## Installation
Pour l'instant l'application n'est pas conteneurisée et n'a pas d'interface utilisateur comme tel. Pour cette raison, l'installation se résume à installer python puis à installer les dépendances. Pour installer les dépendances, effectuez la commande 
`pip install requirements.txt`

*Pour les ressources extérieures telles que qDrant et OpenAI (toutes les deux utilisées dans le projet) vous devez produire vos propres clés et bases de donnée.*

### QDrant
QDrant est une ressource de base de données vectorielles bien utile pour la recherche sémantique. Vous pouvez en lire plus [ici](https://qdrant.tech/)
Nous utilisons qDrant pour stocker les informations contenus dans les pdf de cours. La recherche sémantique est assez efficace, il faudrait par contre que je change un peu la façon d'ingérer les donnnées puisque l'assistant manque un peu de contexte lors de la recherche d'informations.

*Pour créer une collection dans votre cluster, vous pouvez utiliser l'api de qDrant ou encore le client python. [Référez-vous à la documentation](https://qdrant.tech/documentation/)*

### OpenAI
OpenAI permettent l'usage de l'engin GPT 3.5 Turbo ainsi que de plusieurs autres engins de traitement de texte naturel (NLP). Il est possible de créer un compte de développement gratuit sur leur [site](https://platform.openai.com/) et utiliser la clé d'api ainsi obtenue pour effectuer nos demandes à l'engin souhaité. OpenAI restreint présentement les demandes à 3 par minute par compte gratuit, mais en ajoutant une méthode de paiement il est possible d'augmenter ce nombre de demandes.

## Environnement
L'application a besoin de plusieurs valeurs et clés pour fonctionner. Pour des raisons de sécurité je n'ai pas inclu mes propres informations sensibles dans le projet. Pour utiliser l'application avec vos propres données, créez un fichier `.env` sous le dossier `/backend` et insérez-y les informations suivantes :
```
OPENAI_API_KEY=<Votre clé OpenAi>
QDRANT_API_KEY=<Votre clé pour la base de données qDrant>
QDRANT_URL=<L'url de base de votre cluster qDrant>
ENCODING_MODEL=<Votre modèle d'encodage>
COLLECTION_NAME=<Le nom de votre collection qDrant>
DATA_FILE_NAME=<Le nom par défaut de sauvegarde de données -- pour les scripts utilitaires>
BACKEND_API_URL=<L'adresse de votre serveur backend (API)>
```

## Lancement de l'application
Comme l'application n'a pas de réel interface usage, vous pouvez lancer l'application en lançant le serveur API puis en utilisant l'interface en ligne de commande.
- Lancer l'API : `python -m uvicorn API:app --reload`
- Lancer l'interface CLI : `python consoleApp.py`

Vous pourrez alors utiliser l'interface pour Intéroger Buggy Boo Le Grand Sage!