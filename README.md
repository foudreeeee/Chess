# ♟ Chess — le moteur joue le meilleur coup

Interface web d'échecs (Streamlit) où un moteur joue **toujours le meilleur coup**.
Tu choisis ta couleur, tu joues ton camp, le moteur répond au mieux — ou tu regardes
deux moteurs s'affronter.

## Fonctionnalités
- Échiquier cliquable (clic sur ta pièce → clic sur la case cible).
- **Mode Vous vs Moteur** : le moteur joue toujours le meilleur coup pour son camp.
- **Mode Moteur vs Moteur** : lecture automatique de la meilleure partie possible.
- Boutons : Nouvelle partie, Annuler, ⚡ Jouer le meilleur coup, 💡 Suggestion.
- Choix de la couleur, du temps de réflexion, de la pièce de promotion.
- Surbrillance du dernier coup / des coups légaux, détection échec / mat / nulle, historique.

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

## Héberger sur GitHub + Streamlit Community Cloud

1. Crée un dépôt GitHub et pousse ces fichiers :
   ```bash
   git init && git add . && git commit -m "Chess best-move app"
   git branch -M main
   git remote add origin git@github.com:<toi>/<repo>.git
   git push -u origin main
   ```
2. Va sur https://share.streamlit.io → **New app** → sélectionne ton repo,
   branche `main`, fichier `app.py`.
3. Le fichier `packages.txt` installe automatiquement Stockfish sur le cloud.

C'est tout : l'appli est en ligne. 🎉
