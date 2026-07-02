# ♟ Chess — le moteur joue le meilleur coup

Interface web d'échecs (Streamlit) où un moteur joue **toujours le meilleur coup**.
Tu choisis la couleur jouée par le bot, tu joues l'autre camp, le bot répond au mieux.

## Fonctionnalités
- Échiquier cliquable (clic sur ta pièce → clic sur la case cible).
- **Choix de la couleur du bot** (Blancs / Noirs) ; toi tu joues l'autre camp.
- Bouton **Commencer la partie** : rien ne bouge tant que tu ne l'as pas cliqué.
- Bouton **Nouvelle partie**.
- Le bot joue automatiquement le meilleur coup pour sa couleur ; promotion des pions en Dame.
- Surbrillance du dernier coup et des coups légaux, détection échec / mat / nulle.

Le meilleur coup est calculé par **Stockfish** s'il est installé, sinon par un
**minimax alpha-beta** intégré (l'appli marche même sans binaire externe).

## Lancer en local

```bash
./run_local.sh
```

Le script crée un environnement virtuel, installe les dépendances et démarre Streamlit
(l'appli s'ouvre sur http://localhost:8501).

Pour le vrai « meilleur coup », installe Stockfish :
- Arch : `sudo pacman -S stockfish`
- Debian/Ubuntu : `sudo apt install stockfish`
- macOS : `brew install stockfish`
