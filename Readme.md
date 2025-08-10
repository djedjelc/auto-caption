📄 README — Générateur de sous-titres dynamiques pour vidéos courtes
🎯 Objectif

Développer un outil en Python permettant d'ajouter automatiquement des sous-titres dynamiques et stylisés à des vidéos, à la manière des contenus viraux sur TikTok ou Instagram.
Le script prend une vidéo en entrée, génère la transcription à l’aide d’un modèle de reconnaissance vocale, puis incruste les sous-titres à la vidéo avec des styles personnalisés (couleurs, polices, animations, emojis, etc.).
🧰 Fonctionnalités

    ✅ Transcription automatique audio → texte

    ✅ Découpage en phrases/segments synchronisés (avec timestamps)

    ✅ Incrustation du texte dans la vidéo avec styles dynamiques

    ✅ Support des emojis et surbrillance de mots

    ✅ Sortie vidéo stylisée prête à publier

🛠️ Technologies & bibliothèques utilisées
Fonction	Outil / Bibliothèque	Rôle
🔊 Transcription vocale	OpenAI Whisper	Reconnaissance vocale multilingue, ultra précis
📽️ Manipulation vidéo	MoviePy	Ajout de texte, effets dynamiques, montage vidéo
🎨 Overlay stylé	[PIL/Pillow] ou Manim	Pour gérer le rendu de texte animé ou stylisé
🎙 Découpage audio	[pydub]	Pour travailler le son et les segments

📁 Structure du projet

video-subtitles-gen/
├── input_videos/           # Vidéos à sous-titrer
├── output_videos/          # Vidéos exportées avec sous-titres
├── subtitles/              # Fichiers SRT ou JSON des transcriptions
├── styles/                 # Templates pour les sous-titres (polices, couleurs)
├── main.py                 # Script principal
├── utils.py                # Fonctions utilitaires
├── requirements.txt
└── README.md

🚀 Comment ça marche

    Déposer ta vidéo dans le dossier input_videos/.

    Lancer le script principal :

python main.py --file input_videos/ma_video.mp4

    Le script :

        transcrit l’audio avec Whisper

        génère un fichier .srt ou un format personnalisé JSON avec timestamps

        applique les sous-titres sur la vidéo avec un style dynamique

        exporte le rendu final dans output_videos/

🧠 Exemple d’idées de styles dynamiques

    Mot clé en jaune ou en gras selon l’émotion ou l’intensité

    Emojis ajoutés selon le contexte ("😂", "🔥", "💀")

    Texte zoomé ou coloré pour un mot important

    Fond coloré derrière chaque mot ou phrase

    Effets d’apparition (fade in/out, zoom, slide…)

📌 Améliorations futures

    🎨 Interface visuelle pour customiser les styles (via Streamlit ou Gradio)

    🌍 Support multilingue (détection automatique de langue)

    🧠 Détection d’émotions ou de ton (joyeux, énervé, ironique, etc.)

    🗣️ Animation karaoké "mot à mot"

✅ Exemples de bibliothèques utiles pour la suite

    WhisperX → pour une synchronisation mot-à-mot

    FFmpeg → pour traitement vidéo/audio plus complexe

    [TextBlob / spaCy] → pour NLP et traitement intelligent du texte