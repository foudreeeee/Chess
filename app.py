"""Échiquier web : tu choisis la couleur du bot, il joue le MEILLEUR coup.

Lancer en local :  streamlit run app.py   (ou ./run_local.sh)
"""

import base64

import chess
import chess.svg
import streamlit as st

from engine import get_best_move

st.set_page_config(
    page_title="Échecs", page_icon="♟",
    layout="centered", initial_sidebar_state="collapsed",
)

LIGHT, DARK = "#ebecd0", "#739552"      # cases (style chess.com)
SELECTED = "#f6f669"                      # case sélectionnée
LASTMOVE = "#f5f682"                      # dernier coup
TARGET = "rgba(0,0,0,.18)"                # pastille coup légal
MOVETIME = 0.4                            # temps de réflexion du moteur (s)


# --------------------------------------------------------------------------- #
# Pièces : SVG (python-chess) -> data URI, une variable CSS par pièce.
# Nettes et identiques sur tous les appareils (desktop + mobile).
# --------------------------------------------------------------------------- #
@st.cache_data
def piece_vars():
    css = {}
    for pt in range(1, 7):
        for color in (chess.WHITE, chess.BLACK):
            pc = chess.Piece(pt, color)
            svg = chess.svg.piece(pc)
            uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
            name = f"--{'w' if color else 'b'}{chess.piece_symbol(pt)}"
            css[pc.symbol()] = (name, uri)
    return css


PIECES = piece_vars()


def piece_varname(piece):
    return PIECES[piece.symbol()][0]


# --------------------------------------------------------------------------- #
# État
# --------------------------------------------------------------------------- #
def new_game():
    st.session_state.board = chess.Board()
    st.session_state.selected = None
    st.session_state.last_move = None
    st.session_state.started = False


if "board" not in st.session_state:
    st.session_state.bot = chess.WHITE
    new_game()

ss = st.session_state


# --------------------------------------------------------------------------- #
# Contrôles (sur la page principale, visibles sur mobile)
# --------------------------------------------------------------------------- #
st.markdown("### ♟ Échecs")
choice = st.radio("Je joue", ["Blancs", "Noirs"], horizontal=True)
bot_color = chess.WHITE if choice == "Blancs" else chess.BLACK
human_color = not bot_color               # comportement : le bot joue la couleur choisie
if bot_color != ss.bot:                    # changer de couleur = nouvelle partie
    ss.bot = bot_color
    new_game()

c1, c2 = st.columns(2)
if not ss.started:
    if c1.button("▶️ Commencer", type="primary", use_container_width=True):
        ss.started = True
        st.rerun()
if c2.button("🔄 Nouvelle partie", use_container_width=True):
    new_game()
    st.rerun()


# --------------------------------------------------------------------------- #
# Coup du bot (meilleur coup pour sa couleur)
# --------------------------------------------------------------------------- #
board = ss.board
if ss.started and not board.is_game_over() and board.turn == bot_color:
    with st.spinner("Le bot réfléchit…"):
        move = get_best_move(board, MOVETIME)
    if move is not None:
        board.push(move)
        ss.last_move = move
        ss.selected = None
        st.rerun()


# --------------------------------------------------------------------------- #
# Clics
# --------------------------------------------------------------------------- #
def build_move(frm, to):
    piece = board.piece_at(frm)
    if piece and piece.piece_type == chess.PAWN and chess.square_rank(to) in (0, 7):
        return chess.Move(frm, to, promotion=chess.QUEEN)  # promotion auto en Dame
    return chess.Move(frm, to)


def on_click(sq):
    if not ss.started or board.is_game_over() or board.turn != human_color:
        return
    if ss.selected is None:
        piece = board.piece_at(sq)
        if piece and piece.color == board.turn:
            ss.selected = sq
        st.rerun()
    elif sq == ss.selected:
        ss.selected = None
        st.rerun()
    else:
        move = build_move(ss.selected, sq)
        if move in board.legal_moves:
            board.push(move)
            ss.last_move = move
            ss.selected = None
        else:
            piece = board.piece_at(sq)
            ss.selected = sq if (piece and piece.color == board.turn) else None
        st.rerun()


def legal_targets():
    if ss.selected is None:
        return set()
    return {m.to_square for m in board.legal_moves if m.from_square == ss.selected}


# --------------------------------------------------------------------------- #
# Style de l'échiquier (responsive)
# --------------------------------------------------------------------------- #
def board_css(selected, targets):
    # Déclaration des variables de pièces (une seule fois).
    var_decls = ";".join(f"{name}:url('{uri}')" for name, uri in PIECES.values())
    parts = [
        f"""
<style>
/* Un peu moins d'espace en haut, surtout sur mobile */
[data-testid="stMainBlockContainer"]{{ padding-top:2.5rem !important; }}

/* Plateau : largeur RESPONSIVE (s'adapte à l'écran), centré, encadré */
.st-key-board{{
  {var_decls};
  box-sizing:border-box;
  width:min(96vw,460px); margin:0 auto !important;
  border:7px solid #6b4f34; border-radius:6px; overflow:hidden;
  box-shadow:0 8px 24px rgba(0,0,0,.25);
  background:#739552; font-size:0; line-height:0;
  gap:0 !important;
}}
/* Reset : aucun gap/marge/padding dans le plateau (ni sur le conteneur lui-même) */
.st-key-board, .st-key-board *{{
  margin:0 !important; padding:0 !important; gap:0 !important; box-shadow:none !important;
}}
.st-key-board [data-testid="stHorizontalBlock"]{{ display:flex !important; flex-wrap:nowrap !important; }}
.st-key-board [data-testid="stHorizontalBlock"] > div{{
  flex:1 1 0 !important; min-width:0 !important; width:auto !important;
}}
/* Chaque case = un carré qui suit la largeur du plateau */
[class*="st-key-sq_"], [class*="st-key-sq_"] > div{{
  display:block !important; width:100% !important; line-height:0 !important;
}}
[class*="st-key-sq_"] button{{
  display:block !important;
  aspect-ratio:1/1 !important; width:100% !important; height:auto !important; min-height:0 !important;
  border:0 !important; border-radius:0 !important; box-shadow:none !important;
  padding:0 !important; margin:0 !important; color:transparent !important;
  background-position:center !important; background-repeat:no-repeat !important;
}}
[class*="st-key-sq_"] button:active{{ filter:brightness(1.08); }}
"""
    ]
    for sq in chess.SQUARES:
        name = chess.square_name(sq)
        is_light = (chess.square_rank(sq) + chess.square_file(sq)) % 2 == 1
        bg = LIGHT if is_light else DARK
        if ss.last_move and sq in (ss.last_move.from_square, ss.last_move.to_square):
            bg = LASTMOVE
        if sq == selected:
            bg = SELECTED

        piece = board.piece_at(sq)
        is_target = sq in targets
        layers = []
        if piece:
            layers.append(f"var({piece_varname(piece)}) center/86% no-repeat")
        if is_target and not piece:
            layers.append(
                f"radial-gradient(circle,{TARGET} 22%,transparent 24%) center/100% no-repeat"
            )
        layers.append(bg)  # couleur de fond = dernière couche
        parts.append(f".st-key-sq_{name} button{{background:{', '.join(layers)} !important;}}")
        if is_target and piece:  # capture : anneau autour de la pièce
            parts.append(
                f".st-key-sq_{name} button{{box-shadow:inset 0 0 0 4px rgba(0,0,0,.28) !important;}}"
            )
    parts.append("</style>")
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Rendu
# --------------------------------------------------------------------------- #
st.markdown(board_css(ss.selected, legal_targets()), unsafe_allow_html=True)

perspective = bot_color        # la couleur choisie est en bas du plateau
ranks = range(7, -1, -1) if perspective == chess.WHITE else range(8)
files = list(range(8)) if perspective == chess.WHITE else list(range(7, -1, -1))

with st.container(key="board"):
    for r in ranks:
        cols = st.columns(8, gap="small")
        for i, f in enumerate(files):
            sq = chess.square(f, r)
            if cols[i].button(" ", key=f"sq_{chess.square_name(sq)}"):
                on_click(sq)

# Statut
if not ss.started:
    st.caption("Choisis ta couleur, puis clique **▶️ Commencer**.")
elif board.is_game_over():
    if board.is_checkmate():
        gagnant = "Blancs" if board.turn == chess.BLACK else "Noirs"
        st.success(f"Échec et mat — les {gagnant} gagnent !")
    else:
        st.info("Partie nulle.")
elif board.is_check():
    st.warning("Échec !")
