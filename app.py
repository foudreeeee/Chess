"""Échiquier web : tu choisis la couleur du bot, il joue le MEILLEUR coup.

Lancer en local :  streamlit run app.py   (ou ./run_local.sh)
"""

import chess
import streamlit as st

from engine import get_best_move

st.set_page_config(page_title="Échecs", page_icon="♟", layout="centered")

GLYPH = {
    chess.PAWN: "♟",
    chess.KNIGHT: "♞",
    chess.BISHOP: "♝",
    chess.ROOK: "♜",
    chess.QUEEN: "♛",
    chess.KING: "♚",
}
EMPTY = " "

LIGHT, DARK = "#ebecd0", "#739552"      # cases (style chess.com)
SELECTED = "#f6f669"                      # case sélectionnée
LASTMOVE = "#f5f682"                      # dernier coup
TARGET = "rgba(0,0,0,.16)"                # pastille coup légal
MOVETIME = 0.4                            # temps de réflexion du moteur (s)


# --------------------------------------------------------------------------- #
# État
# --------------------------------------------------------------------------- #
def new_game():
    st.session_state.board = chess.Board()
    st.session_state.selected = None
    st.session_state.last_move = None
    st.session_state.started = False      # rien ne bouge avant "Commencer"


if "board" not in st.session_state:
    st.session_state.bot = chess.WHITE
    new_game()

ss = st.session_state


# --------------------------------------------------------------------------- #
# Contrôles
# --------------------------------------------------------------------------- #
st.sidebar.header("♟ Échecs")
choice = st.sidebar.radio("Je joue", ["Blancs", "Noirs"])
bot_color = chess.WHITE if choice == "Blancs" else chess.BLACK
human_color = not bot_color               # comportement inchangé : le bot joue la couleur choisie
if bot_color != ss.bot:                    # changer de couleur = nouvelle partie
    ss.bot = bot_color
    new_game()

if not ss.started:
    if st.sidebar.button("▶️ Commencer la partie", use_container_width=True, type="primary"):
        ss.started = True
        st.rerun()
if st.sidebar.button("🔄 Nouvelle partie", use_container_width=True):
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
# Style
# --------------------------------------------------------------------------- #
def board_css(selected, targets):
    parts = [
        """
<style>
/* Cases en PIXELS ENTIERS FIXES (--sq) : aucune largeur fractionnaire,
   donc aucune couture sous-pixel possible entre les cases. */
.st-key-board{
  --sq:62px;
  width:fit-content; max-width:100%; margin:0 auto !important;
  border:8px solid #6b4f34; border-radius:6px; overflow:hidden;
  box-shadow:0 8px 24px rgba(0,0,0,.25);
  background:#739552; font-size:0; line-height:0;
  gap:0 !important;                 /* <-- l'écart de 16px entre les rangées était ICI */
}
/* Reset universel DANS le plateau : gap/marge/padding sur TOUS les descendants */
.st-key-board, .st-key-board *{
  margin:0 !important; padding:0 !important; gap:0 !important;
  box-shadow:none !important;
}
.st-key-board [data-testid="stHorizontalBlock"]{
  display:flex !important; flex-wrap:nowrap !important;
}
.st-key-board [data-testid="stHorizontalBlock"] > div{
  flex:0 0 var(--sq) !important; width:var(--sq) !important; min-width:var(--sq) !important;
}
[class*="st-key-sq_"], [class*="st-key-sq_"] > div{
  display:block !important; width:var(--sq) !important; line-height:0 !important;
}
[class*="st-key-sq_"] button{
  display:block !important;
  width:var(--sq) !important; height:var(--sq) !important;
  border:0 !important; border-radius:0 !important; box-shadow:none !important;
  padding:0 !important; margin:0 !important;
  font-size:40px !important; line-height:1 !important;
  transition:none !important;
}
[class*="st-key-sq_"] button:hover{ filter:brightness(1.06); }
[class*="st-key-sq_"] button:focus{ outline:none !important; }
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
        parts.append(f".st-key-sq_{name} button{{background:{bg} !important;}}")
        if sq in targets:
            parts.append(
                f".st-key-sq_{name} button{{"
                f"background:radial-gradient(circle,{TARGET} 26%,transparent 28%),{bg} !important;}}"
            )
        piece = board.piece_at(sq)
        if piece:
            if piece.color == chess.WHITE:
                parts.append(
                    f".st-key-sq_{name} button{{color:#fafafa !important;"
                    "text-shadow:-1px -1px 0 #444,1px -1px 0 #444,-1px 1px 0 #444,"
                    "1px 1px 0 #444,0 0 2px #444;}"
                )
            else:
                parts.append(f".st-key-sq_{name} button{{color:#1a1a1a !important;}}")
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
            piece = board.piece_at(sq)
            label = GLYPH[piece.piece_type] if piece else EMPTY
            if cols[i].button(label, key=f"sq_{chess.square_name(sq)}"):
                on_click(sq)

# Statut
if not ss.started:
    st.caption("Choisis la couleur du bot, puis clique **▶️ Commencer la partie**.")
elif board.is_game_over():
    if board.is_checkmate():
        gagnant = "Blancs" if board.turn == chess.BLACK else "Noirs"
        st.success(f"Échec et mat — les {gagnant} gagnent !")
    else:
        st.info("Partie nulle.")
elif board.is_check():
    st.warning("Échec !")
