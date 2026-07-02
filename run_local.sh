#!/usr/bin/env bash
# Lance l'appli d'échecs en local (crée un venv, installe les dépendances, démarre Streamlit).
set -e
cd "$(dirname "$0")"

# --- Environnement virtuel ---------------------------------------------------
if [ ! -d ".venv" ]; then
  echo "→ Création de l'environnement virtuel (.venv)…"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "→ Installation des dépendances Python…"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# --- Vérification de Stockfish ----------------------------------------------
if ! command -v stockfish >/dev/null 2>&1; then
  echo ""
  echo "⚠️  Stockfish introuvable : l'appli utilisera le moteur de secours (minimax)."
  echo "    Pour le VRAI meilleur coup, installe Stockfish :"
  echo "      Arch      : sudo pacman -S stockfish"
  echo "      Debian/Ubuntu : sudo apt install stockfish"
  echo "      macOS     : brew install stockfish"
  echo ""
else
  echo "✓ Stockfish détecté : $(command -v stockfish)"
fi

# --- Lancement ---------------------------------------------------------------
echo "→ Démarrage de Streamlit…  (Ctrl+C pour arrêter)"
streamlit run app.py
