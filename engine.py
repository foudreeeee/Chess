"""Wrapper de moteur d'échecs.

Utilise Stockfish s'il est disponible (le vrai "meilleur coup").
Sinon, bascule sur un minimax alpha-beta intégré pour que l'appli
fonctionne partout, même sans binaire externe.
"""

import atexit
import os
import shutil

import chess

# Sentinelle : "uninitialized" tant qu'on n'a pas cherché le binaire.
_ENGINE = "uninitialized"

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}


def _find_stockfish_path():
    """Cherche un binaire Stockfish dans le PATH puis dans les emplacements courants."""
    for name in ("stockfish", "stockfish.exe"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in (
        "/usr/bin/stockfish",
        "/usr/local/bin/stockfish",
        "/usr/games/stockfish",
        "/opt/homebrew/bin/stockfish",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def _get_engine():
    """Retourne un moteur Stockfish (singleton) ou None si indisponible."""
    global _ENGINE
    if _ENGINE == "uninitialized":
        path = _find_stockfish_path()
        if path:
            try:
                import chess.engine

                _ENGINE = chess.engine.SimpleEngine.popen_uci(path)
                atexit.register(_quit_engine)
            except Exception:
                _ENGINE = None
        else:
            _ENGINE = None
    return _ENGINE


def _quit_engine():
    global _ENGINE
    if _ENGINE not in ("uninitialized", None):
        try:
            _ENGINE.quit()
        except Exception:
            pass
        _ENGINE = None


def engine_name():
    """Nom lisible du moteur actif (pour l'affichage)."""
    eng = _get_engine()
    if eng:
        try:
            return eng.id.get("name", "Stockfish")
        except Exception:
            return "Stockfish"
    return "Moteur de secours (minimax)"


def get_best_move(board, movetime=0.5):
    """Retourne le meilleur coup pour le camp au trait."""
    if board.is_game_over():
        return None
    eng = _get_engine()
    if eng:
        import chess.engine

        try:
            result = eng.play(board, chess.engine.Limit(time=movetime))
            if result.move is not None:
                return result.move
        except Exception:
            pass  # on retombe sur le minimax
    return _minimax_best(board, depth=3)


# --------------------------------------------------------------------------- #
# Moteur de secours : minimax alpha-beta (négamax)
# --------------------------------------------------------------------------- #

_INF = float("inf")


def _material(board):
    """Bilan matériel du point de vue des Blancs (centipions)."""
    score = 0
    for piece in board.piece_map().values():
        value = PIECE_VALUES[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    return score


def _eval_leaf(board):
    """Évaluation d'une position feuille, du point de vue du camp au trait."""
    if board.is_checkmate():
        return -100000
    if board.is_game_over():
        return 0
    perspective = 1 if board.turn == chess.WHITE else -1
    return perspective * _material(board)


def _ordered_moves(board):
    """Captures d'abord : accélère l'élagage alpha-beta."""
    return sorted(board.legal_moves, key=board.is_capture, reverse=True)


def _negamax(board, depth, alpha, beta):
    if depth == 0 or board.is_game_over():
        return _eval_leaf(board)
    best = -_INF
    for move in _ordered_moves(board):
        board.push(move)
        value = -_negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if value > best:
            best = value
        if value > alpha:
            alpha = value
        if alpha >= beta:
            break
    return best


def _minimax_best(board, depth=3):
    best_move = None
    best_value = -_INF
    alpha, beta = -_INF, _INF
    for move in _ordered_moves(board):
        board.push(move)
        value = -_negamax(board, depth - 1, -beta, -alpha)
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
        if value > alpha:
            alpha = value
    if best_move is None:
        legal = list(board.legal_moves)
        return legal[0] if legal else None
    return best_move
