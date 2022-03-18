import io
from typing import Coroutine, Callable, Type, TYPE_CHECKING

import discord
import discord.commands

if TYPE_CHECKING:
    from bot import DiscordBot


def check_knight(color: bool, board: 'Board', pos: tuple[int, int]) -> bool:
    """
    Check if there is a knight of the opposite `color` at
    position `pos` on board `board`.
    color : bool
        True if white
    board : Board
        Representation of the current chess board
    pos : tup
        Indices to check if there's is a knight
    Precondition `pos` is a valid position on the board.
    """
    piece = board.board[pos[0]][pos[1]]
    if piece is not None and piece.color != color and piece.name == 'N':
        return False
    return True


def check_diag_castle(color: bool, board: 'Board', start: tuple[int, int], to: tuple[int, int]) -> bool:
    """
    Checks the diagonal path from `start` (non-inclusive) to `to` (inclusive)
    on board `board` for any threats from the opposite `color`
    color : bool
        True if white
    board : Board
        Representation of the current chess board
    start : tup
        Starting point of the diagonal path
    to : tup
        Ending point of the diagonal path
    Precondition: `start` and `to` are valid positions on the board
    """

    if abs(start[0] - to[0]) != abs(start[1] - to[1]):
        return False

    x_pos = 1 if to[0] - start[0] > 0 else -1
    y_pos = 1 if to[1] - start[1] > 0 else -1

    i = start[0] + x_pos
    j = start[1] + y_pos

    exists_piece = board.board[i][j] is not None
    if exists_piece and (board.board[i][j].name == 'P' or board.board[i][j].name == 'K') and \
            board.board[i][j].color != color:
        return False

    while i <= to[0] if x_pos == 1 else i >= to[0]:
        if exists_piece and board.board[i][j].color != color:
            if board.board[i][j].name in ['B', 'Q']:
                return False
            else:
                return True
        if exists_piece and board.board[i][j].color == color:
            return True
        i += x_pos
        j += y_pos
        try:
            exists_piece = board.board[i][j] is not None
        except IndexError:
            return True

    return True


def check_diag(board: 'Board', start: tuple[int, int], to: tuple[int, int]) -> bool:
    """
    Checks if there are no pieces along the diagonal path from
    `start` (non-inclusive) to `to` (non-inclusive).
    board : Board
        Representation of the current board
    start : tup
        Start location of diagonal path
    to : tup
        End location of diagonal path
    """

    if abs(start[0] - to[0]) != abs(start[1] - to[1]):
        return False

    x_pos = 1 if to[0] - start[0] > 0 else -1
    y_pos = 1 if to[1] - start[1] > 0 else -1

    i = start[0] + x_pos
    j = start[1] + y_pos
    while i < to[0] if x_pos == 1 else i > to[0]:
        if board.board[i][j] is not None and not board.board[i][j].ghost:
            return False
        i += x_pos
        j += y_pos
    return True


def check_updown_castle(color: bool, board: 'Board', start: tuple[int, int], to: tuple[int, int]) -> bool:
    """
    Checks if there are any threats from the opposite `color` from `start` (non-inclusive)
    to `to` (inclusive) on board `board`.
    color : bool
        True if white's turn

    board : Board
        Representation of the current board
    start : tup
        Start location of vertical path
    to : tup
        End location of vertical path
    """

    x_pos = 1 if to[0] - start[0] > 0 else -1
    i = start[0] + x_pos

    front_piece = board.board[i][start[1]]
    if front_piece is not None and front_piece.name == 'K' and front_piece.color != color:
        return False

    while i <= to[0] if x_pos == 1 else i >= to[0]:
        if board.board[i][start[1]] is not None and board.board[i][start[1]].color != color:
            if board.board[i][start[1]].name in ['R', 'Q']:
                return False
            else:
                return True
        if board.board[i][start[1]] is not None and board.board[i][start[1]].color == color:
            return True
        i += x_pos

    return True


def check_updown(board: 'Board', start: tuple[int, int], to: tuple[int, int]) -> bool:
    """
    Checks if there are no pieces along the vertical or horizontal path
    from `start` (non-inclusive) to `to` (non-inclusive).
    board : Board
        Representation of the current board
    start : tup
        Start location of diagonal path
    to : tup
        End location of diagonal path
    """
    if start[0] == to[0]:
        smaller_y = min(start[1], to[1])
        bigger_y = max(start[1], to[1])

        for i in range(smaller_y + 1, bigger_y):
            if board.board[start[0]][i] is not None and not board.board[start[0]][i].ghost:
                return False
        return True
    else:
        smaller_x = min(start[0], to[0])
        bigger_x = max(start[0], to[0])

        for i in range(smaller_x + 1, bigger_x):
            if board.board[i][start[1]] is not None and not board.board[i][start[1]].ghost:
                return False
        return True


class Piece:
    """
    A class to represent a piece in chess

    ...
    Attributes:
    -----------
    name : str
        Represents the name of a piece as following -
        Pawn -> P
        Rook -> R
        Knight -> N
        Bishop -> B
        Queen -> Q
        King -> K
    color : bool
        True if piece is white
    Methods:
    --------
    is_valid_move(board, start, to) -> bool
        Returns True if moving the piece at `start` to `to` is a legal
        move on board `board`
        Precondition: [start] and [to] are valid coordinates on the board.board
    is_white() -> bool
        Return True if piece is white
    """

    def __init__(self, color: bool):
        self.name: str = ""
        self.ghost = False
        self.color: bool = color
        self.emoji_white: str = "\u200b"
        self.emoji_black: str = "\u200b"

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        return False

    def is_valid_capture(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        return self.is_valid_move(board, start, to, apply_move)

    def is_white(self) -> bool:
        return self.color

    def emoji(self) -> str:
        if self.color:
            return self.emoji_white
        else:
            return self.emoji_black

    def __str__(self):
        if self.color:
            return self.name
        else:
            return '\033[94m' + self.name + '\033[0m'


class Rook(Piece):
    def __init__(self, color: bool, first_move=True):
        """
        Same as base class Piece, except `first_move` is used to check
        if this rook can castle.
        """
        super().__init__(color)
        self.name = "R"
        self.emoji_white = '·♜·'
        self.emoji_black = '♖'
        self.first_move = first_move

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        if start[0] == to[0] or start[1] == to[1]:
            return check_updown(board, start, to)
        return False


class Knight(Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.name = "N"
        self.emoji_white = '·♞·'
        self.emoji_black = '♘'

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        if abs(start[0] - to[0]) == 2 and abs(start[1] - to[1]) == 1:
            return True
        if abs(start[0] - to[0]) == 1 and abs(start[1] - to[1]) == 2:
            return True
        return False


class Bishop(Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.name = "B"
        self.emoji_white = '·♝·'
        self.emoji_black = '♗'

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        return check_diag(board, start, to)


class Queen(Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.name = "Q"
        self.emoji_white = '·♛·'
        self.emoji_black = '♕'

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        # diagonal
        if abs(start[0] - to[0]) == abs(start[1] - to[1]):
            return check_diag(board, start, to)

        # up/down
        elif start[0] == to[0] or start[1] == to[1]:
            return check_updown(board, start, to)
        return False


class King(Piece):
    def __init__(self, color: bool, first_move=True):
        """
        Same as base class Piece, except `first_move` is used to check
        if this king can castle.
        """
        super().__init__(color)
        self.name = "K"
        self.first_move = first_move
        self.emoji_white = '·♚·'
        self.emoji_black = '♔'

    def can_castle(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], right: bool, apply_move=False):
        """
        Returns True if king at `start` can move to `to` on `board`.
        board : Board
            Represents the current board
        start : tup
            Position of the king
        to : tup
            Position of the resulting move
        right: bool
            True if castling to the right False otherwise
        Precondition: moving from `start` to `to` is a castling move
        """

        if board.board[to[0]][to[1]]:
            return False

        if not check_updown(board, start, to):
            return False

        # White castling to the right
        if self.color and right:

            rook_found = None
            for x in range(start[1] + 1, board.max_size[1]):
                if board.board[start[0]][x]:
                    if board.board[start[0]][x].name != 'R':
                        return False
                    if board.board[start[0]][x].color and board.board[start[0]][x].first_move:
                        rook_found = (start[0], x)
                        break
            if rook_found is None:
                return False

            knight_attack = check_knight(self.color, board, (6, 3)) and \
                            check_knight(self.color, board, (6, 4)) and \
                            check_knight(self.color, board, (5, 4)) and \
                            check_knight(self.color, board, (5, 5)) and \
                            check_knight(self.color, board, (5, 6)) and \
                            check_knight(self.color, board, (5, 7)) and \
                            check_knight(self.color, board, (6, 7))
            if not knight_attack:
                return False

            diags = check_diag_castle(self.color, board, (7, 5), (2, 0)) and \
                    check_diag_castle(self.color, board, (7, 6), (1, 0)) and \
                    check_diag_castle(self.color, board, (7, 5), (5, 7)) and \
                    check_diag_castle(self.color, board, (7, 6), (6, 7))
            if not diags:
                return False

            updowns = check_updown_castle(self.color, board, (7, 5), (0, 5)) and \
                      check_updown_castle(self.color, board, (7, 6), (0, 6))
            if not updowns:
                return False

            if apply_move:
                board.board[to[0]][to[1]] = King(True, False)
                board.board[to[0]][to[1] - 1] = Rook(True, False)
                board.board[start[0]][start[1]] = None
                board.board[rook_found[0]][rook_found[1]] = None
            return True

        # White castling to the left
        if self.color and not right:

            rook_found = None
            for x in range(start[1] - 1, -1, -1):
                if board.board[start[0]][x]:
                    if board.board[start[0]][x].name != 'R':
                        return False
                    if board.board[start[0]][x].color and board.board[start[0]][x].first_move:
                        rook_found = (start[0], x)
                        break
            if rook_found is None:
                return False

            knight_attack = check_knight(self.color, board, (6, 0)) and \
                            check_knight(self.color, board, (6, 1)) and \
                            check_knight(self.color, board, (5, 1)) and \
                            check_knight(self.color, board, (5, 2)) and \
                            check_knight(self.color, board, (5, 3)) and \
                            check_knight(self.color, board, (5, 4)) and \
                            check_knight(self.color, board, (6, 4)) and \
                            check_knight(self.color, board, (6, 5))
            if not knight_attack:
                return False

            diags = check_diag_castle(self.color, board, (7, 2), (5, 0)) and \
                    check_diag_castle(self.color, board, (7, 3), (4, 0)) and \
                    check_diag_castle(self.color, board, (7, 2), (2, 7)) and \
                    check_diag_castle(self.color, board, (7, 3), (3, 7))
            if not diags:
                return False

            updowns = check_updown_castle(self.color, board, (7, 2), (0, 2)) and \
                      check_updown_castle(self.color, board, (7, 3), (0, 3))
            if not updowns:
                return False
            if apply_move:
                board.board[to[0]][to[1]] = King(True, False)
                board.board[to[0]][to[1] + 1] = Rook(True, False)
                board.board[start[0]][start[1]] = None
                board.board[rook_found[0]][rook_found[1]] = None

            return True

        # Black castling to the right
        if not self.color and right:
            rook_found = None
            for x in range(start[1] + 1, board.max_size[1]):
                if board.board[start[0]][x]:
                    if board.board[start[0]][x].name != 'R':
                        return False
                    if not board.board[start[0]][x].color and board.board[start[0]][x].first_move:
                        rook_found = (start[0], x)
                        break
            if rook_found is None:
                return False

            knight_attack = check_knight(self.color, board, (1, 3)) and \
                            check_knight(self.color, board, (1, 4)) and \
                            check_knight(self.color, board, (1, 7)) and \
                            check_knight(self.color, board, (2, 4)) and \
                            check_knight(self.color, board, (2, 5)) and \
                            check_knight(self.color, board, (2, 6)) and \
                            check_knight(self.color, board, (2, 7))
            if not knight_attack:
                return False

            diags = check_diag_castle(self.color, board, (0, 5), (5, 0)) and \
                    check_diag_castle(self.color, board, (0, 6), (6, 0)) and \
                    check_diag_castle(self.color, board, (0, 5), (2, 7)) and \
                    check_diag_castle(self.color, board, (0, 6), (1, 7))
            if not diags:
                return False

            updowns = check_updown_castle(self.color, board, (0, 2), (7, 2)) and \
                      check_updown_castle(self.color, board, (0, 3), (7, 3))
            if not updowns:
                return False

            if apply_move:
                board.board[to[0]][to[1]] = King(False, False)
                board.board[to[0]][to[1] - 1] = Rook(False, False)
                board.board[start[0]][start[1]] = None
                board.board[rook_found[0]][rook_found[1]] = None

            return True

        # Black castling to the left
        if not self.color and not right:

            rook_found = None
            for x in range(start[1] - 1, -1, -1):
                if board.board[start[0]][x]:
                    if board.board[start[0]][x].name != 'R':
                        return False
                    if not board.board[start[0]][x].color and board.board[start[0]][x].first_move:
                        rook_found = (start[0], x)
                        break
            if rook_found is None:
                return False

            knight_attack = check_knight(self.color, board, (1, 0)) and \
                            check_knight(self.color, board, (1, 1)) and \
                            check_knight(self.color, board, (1, 4)) and \
                            check_knight(self.color, board, (1, 5)) and \
                            check_knight(self.color, board, (2, 1)) and \
                            check_knight(self.color, board, (2, 2)) and \
                            check_knight(self.color, board, (2, 3)) and \
                            check_knight(self.color, board, (2, 4))
            if not knight_attack:
                return False

            diags = check_diag_castle(self.color, board, (0, 2), (5, 7)) and \
                    check_diag_castle(self.color, board, (0, 3), (4, 7)) and \
                    check_diag_castle(self.color, board, (0, 2), (2, 0)) and \
                    check_diag_castle(self.color, board, (0, 3), (3, 0))
            if not diags:
                return False

            updowns = check_updown_castle(self.color, board, (0, 2), (7, 2)) and \
                      check_updown_castle(self.color, board, (0, 3), (7, 3))
            if not updowns:
                return False

            if apply_move:
                board.board[to[0]][to[1]] = King(False, False)
                board.board[to[0]][to[1] + 1] = Rook(False, False)
                board.board[start[0]][start[1]] = None
                board.board[rook_found[0]][rook_found[1]] = None

            return True

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        for y in range(board.max_size[0]):
            for x in range(board.max_size[1]):
                if (y, x) != start and (y, x) != to:
                    piece = board.board[y][x]
                    if piece is not None and piece.color != self.color:
                        if piece.name == 'K':
                            if abs(y - to[0]) == 1 or y - to[0] == 0:
                                if x - to[1] == 0 or abs(x - to[1]) == 1:
                                    return False
                        elif piece.is_valid_capture(board, (y, x), to, False):
                            return False

        if self.first_move and abs(start[1] - to[1]) == 2 and start[0] - to[0] == 0:
            return self.can_castle(board, start, to, to[1] - start[1] > 0, apply_move)

        if abs(start[0] - to[0]) == 1 or start[0] - to[0] == 0:
            if start[1] - to[1] == 0 or abs(start[1] - to[1]) == 1:
                return True

        return False


class GhostPawn(Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.name = "GP"
        self.ghost = True

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        return False


class Pawn(Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.name = "P"
        self.emoji_white = '·♟·'
        self.emoji_black = '♙'
        self.first_move = True

    def is_valid_move(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        if self.color:
            if self.is_valid_capture(board, start, to, apply_move):
                return True

            # vertical move
            if start[1] == to[1]:
                if (start[0] - to[0] == 2 and self.first_move) or (start[0] - to[0] == 1):
                    for i in range(start[0] - 1, to[0] - 1, -1):
                        if board.board[i][start[1]] is not None:
                            return False
                    # insert a GhostPawn
                    if apply_move and start[0] - to[0] == 2:
                        board.white_ghost_piece = (start[0] - 1, start[1])
                    return True
                return False
            return False

        else:
            if self.is_valid_capture(board, start, to, apply_move):
                return True

            if start[1] == to[1]:
                if (to[0] - start[0] == 2 and self.first_move) or (to[0] - start[0] == 1):
                    for i in range(start[0] + 1, to[0] + 1):
                        if board.board[i][start[1]] is not None:
                            return False
                    # insert a GhostPawn
                    if apply_move and to[0] - start[0] == 2:
                        board.black_ghost_piece = (start[0] + 1, start[1])
                    return True
                return False
            return False

    def is_valid_capture(self, board: 'Board', start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        if self.color:
            if start[0] == to[0] + 1 and (start[1] == to[1] + 1 or start[1] == to[1] - 1):
                if board.board[to[0]][to[1]] is not None:
                    return True
                return False

            return False

        else:
            if start[0] == to[0] - 1 and (start[1] == to[1] - 1 or start[1] == to[1] + 1):
                if board.board[to[0]][to[1]] is not None:
                    return True
                return False

            return False


class Board:
    """
    A class to represent a chess board.
    ...
    Attributes:
    -----------
    board : list[list[Piece]]
        represents a chess board

    turn : bool
        True if white's turn
    white_ghost_piece : tup
        The coordinates of a white ghost piece representing a takeable pawn for en passant
    black_ghost_piece : tup
        The coordinates of a black ghost piece representing a takeable pawn for en passant
    Methods:
    --------
    print_board() -> None
        Prints the current configuration of the board
    move(start:tup, to:tup) -> None
        Moves the piece at `start` to `to` if possible. Otherwise, does nothing.

    """

    def __init__(self, board: list[list[Piece or None]], max_size=(8, 8)):
        """
        Initializes the board per standard chess rules
        """

        self.board: list[list[Piece or None]] = board
        self.max_size = max_size

        self.white_ghost_piece = None
        self.black_ghost_piece = None

    @staticmethod
    def empty(size=(8, 8)) -> list[list[Piece or None]]:
        board: list[list[Piece or None]] = []
        # Board set-up
        for i in range(size[1]):
            board.append([None] * size[0])

        return board

    @classmethod
    def default(cls):
        board: list[list[Piece or None]] = Board.empty()
        # White
        board[7][0] = Rook(True)
        board[7][1] = Knight(True)
        board[7][2] = Bishop(True)
        board[7][3] = Queen(True)
        board[7][4] = King(True)
        board[7][5] = Bishop(True)
        board[7][6] = Knight(True)
        board[7][7] = Rook(True)

        for i in range(8):
            board[6][i] = Pawn(True)

        # Black
        board[0][0] = Rook(False)
        board[0][1] = Knight(False)
        board[0][2] = Bishop(False)
        board[0][3] = Queen(False)
        board[0][4] = King(False)
        board[0][5] = Bishop(False)
        board[0][6] = Knight(False)
        board[0][7] = Rook(False)

        for i in range(8):
            board[1][i] = Pawn(False)
        return cls(board)

    @classmethod
    def small(cls):
        board: list[list[Piece or None]] = Board.empty()
        # White
        board[7][0] = Rook(True)
        board[7][1] = Knight(True)
        board[7][2] = Bishop(True)
        board[7][3] = King(True)

        for i in range(4):
            board[6][i] = Pawn(True)

        # Black
        board[0][0] = Rook(False)
        board[0][1] = Knight(False)
        board[0][2] = Bishop(False)
        board[0][3] = King(False)

        for i in range(4):
            board[1][i] = Pawn(False)
        return cls(board, max_size=(8, 4))

    def __str__(self):
        tmp_str = ('*' * round(len(self.board[0]) * 4.2)) + '\n'
        for i in range(len(self.board)):
            tmp_str += '|'
            for j in self.board[i]:
                if j is None or j.name == 'GP':
                    tmp_str += '   |'
                elif len(j.name) == 2:
                    tmp_str += (' ' + str(j) + '|')
                else:
                    tmp_str += (' ' + str(j) + ' |')
            tmp_str += '\n'
        tmp_str += '*' * round(len(self.board[0]) * 4.2)
        return tmp_str


class Chess:
    """
    A class to represent the game of chess.

    ...
    Attributes:
    -----------
    board : Board
        represents the chess board of the game
    turn : bool
        True if white's turn
    Methods:
    --------
    promote(pos:stup) -> None
        Promotes a pawn that has reached the other side to another, or the same, piece
    move(start:tup, to:tup) -> None
        Moves the piece at `start` to `to` if possible. Otherwise, does nothing.
    """

    def __init__(self, board=Board.default()):
        self.board = board

        self.turn = True

    def promotion_by_string(self, promote: str, pos: tuple[int, int]):
        if promote == '' or promote == 'Q':
            self.promotion(pos, Queen)
            return
        elif promote == 'R':
            self.promotion(pos, Rook)
            return
        elif promote == 'N':
            self.promotion(pos, Knight)
            return
        elif promote == 'B':
            self.promotion(pos, Bishop)
            return

    def promotion(self, pos: tuple[int, int], cls: Type[Piece]):
        old_piece = self.board.board[pos[0]][pos[1]]
        new_piece = cls(old_piece.color)
        new_piece.first_move = False
        self.board.board[pos[0]][pos[1]] = new_piece

    def has_valid_move(self, start: tuple[int, int]) -> bool:
        for y in range(self.board.max_size[0]):
            for x in range(self.board.max_size[1]):
                if self.is_valid_move(start, (y, x)):
                    return True
        return False

    def check_promotion(self):
        i = 0
        while i < len(self.board.board[0]):
            if not self.turn and self.board.board[0][i] is not None and \
                    self.board.board[0][i].name == 'P':
                return 0, i
            elif self.turn and self.board.board[-1][i] is not None and \
                    self.board.board[7][i].name == 'P':
                return len(self.board.board) - 1, i
            i += 1
        return None

    def in_check(self) -> bool:
        for y in range(self.board.max_size[0]):
            for x in range(self.board.max_size[1]):
                if self.board.board[y][x] is not None \
                        and self.board.board[y][x].color == self.turn and self.board.board[y][x].name == 'K':
                    for y2 in range(self.board.max_size[0]):
                        for x2 in range(self.board.max_size[1]):
                            if (x, y) != (x2, y2) and self.board.board[y2][x2] is not None and \
                                    self.board.board[y2][x2].color != self.turn and \
                                    self.board.board[y2][x2].name != 'K' and \
                                    self.board.board[y2][x2].is_valid_capture(self.board, (y2, x2), (y, x)):
                                return True
        return False

    def in_check_after_move(self, start: tuple[int, int], to: tuple[int, int]) -> bool:
        start_t = self.board.board[start[0]][start[1]]
        to_t = self.board.board[to[0]][to[1]]
        self.board.board[start[0]][start[1]] = None
        self.board.board[to[0]][to[1]] = start_t

        res = self.in_check()

        self.board.board[to[0]][to[1]] = to_t
        self.board.board[start[0]][start[1]] = start_t
        return res

    def in_checkmate(self) -> bool:
        if not self.in_check():
            return False
        for y in range(self.board.max_size[0]):
            for x in range(self.board.max_size[1]):
                if self.board.board[y][x] is not None \
                        and self.board.board[y][x].color == self.turn:
                    for y2 in range(self.board.max_size[0]):
                        for x2 in range(self.board.max_size[1]):
                            if (x, y) != (x2, y2) and self.is_valid_move((y, x), (y2, x2)) \
                                    and not self.in_check_after_move((y, x), (y2, x2)):
                                return False
        return True

    def in_stalemate(self) -> bool:
        for y in range(self.board.max_size[0]):
            for x in range(self.board.max_size[1]):
                if self.board.board[y][x] is not None:
                    for y2 in range(self.board.max_size[0]):
                        for x2 in range(self.board.max_size[1]):
                            if (x, y) != (x2, y2) and self.is_valid_move((y, x), (y2, x2)):
                                return False
        return True

    def is_valid_move(self, start: tuple[int, int], to: tuple[int, int], apply_move=False) -> bool:
        if self.board.board[start[0]][start[1]] is None:
            return False

        if to[0] >= self.board.max_size[0] or to[1] >= self.board.max_size[1]:
            return False

        target_piece = self.board.board[start[0]][start[1]]
        if self.turn != target_piece.color:
            return False

        if self.board.white_ghost_piece:
            self.board.board[self.board.white_ghost_piece[0]][self.board.white_ghost_piece[1]] = GhostPawn(True)

        if self.board.black_ghost_piece:
            self.board.board[self.board.black_ghost_piece[0]][self.board.black_ghost_piece[1]] = GhostPawn(False)

        end_piece = self.board.board[to[0]][to[1]]

        if self.in_check_after_move(start, to):
            return False

        end_piece_same_color = end_piece is not None and self.board.board[start[0]][start[1]].color == end_piece.color

        if target_piece.name == 'P' and end_piece_same_color:
            return False

        if end_piece_same_color and not end_piece.ghost:
            return False

        res = target_piece.is_valid_move(self.board, start, to, apply_move)

        if self.board.white_ghost_piece:
            self.board.board[self.board.white_ghost_piece[0]][self.board.white_ghost_piece[1]] = None

        if self.board.black_ghost_piece:
            self.board.board[self.board.black_ghost_piece[0]][self.board.black_ghost_piece[1]] = None

        return res

    def move(self, start: tuple[int, int], to: tuple[int, int]):
        """
        Moves a piece at `start` to `to`. Does nothing if there is no piece at the starting point.
        Does nothing if the piece at `start` belongs to the wrong color for the current turn.
        Does nothing if moving the piece from `start` to `to` is not a valid move.
        start : tup
            Position of a piece to be moved
        to : tup
            Position of where the piece is to be moved

        precondition: `start` and `to` are valid positions on the board
        """

        target_piece = self.board.board[start[0]][start[1]]

        if target_piece.name != 'P':
            self.board.black_ghost_piece = None
            self.board.white_ghost_piece = None

        if self.is_valid_move(start, to, apply_move=True):
            target_piece.first_move = False

            if self.turn and to == self.board.black_ghost_piece:
                self.board.board[self.board.black_ghost_piece[0] + 1][self.board.black_ghost_piece[1]] = None
                self.board.black_ghost_piece = None
            elif not self.turn and to == self.board.white_ghost_piece:
                self.board.board[self.board.white_ghost_piece[0] - 1][self.board.white_ghost_piece[1]] = None
                self.board.white_ghost_piece = None

            self.board.board[to[0]][to[1]] = target_piece
            self.board.board[start[0]][start[1]] = None

            self.turn = not self.turn


class ChessButton(discord.ui.Button):
    def __init__(self, x: int, y: int, pos: tuple[int, int],
                 callback: Callable[['ChessButton', discord.Interaction], Coroutine],
                 light_field: bool):
        self.default_style = discord.ButtonStyle.secondary
        if light_field:
            self.default_style = discord.ButtonStyle.success
        super().__init__(style=self.default_style, label="\u200b", row=y)
        self.x = x
        self.y = y
        self.pos = pos
        self.chess_callback = callback

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        await self.chess_callback(self, interaction)


class ChessView(discord.ui.View):
    children: list[ChessButton]

    def __init__(self, callback: Callable[['ChessButton', discord.Interaction], Coroutine],
                 x_rows=4, y_cols=4, x_offset=0, y_offset=0):
        super().__init__()

        for x in range(x_rows):
            for y in range(y_cols):
                xi = x + x_offset
                yi = y + y_offset
                self.add_item(ChessButton(x, y, (yi, xi), callback, (xi + (yi % 2)) % 2 == 1))

    async def on_timeout(self) -> None:
        print('Timeout')

    async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
        print('Error')


class ChessViewHolder:
    async def check_send_prefix_message(self, template: str, white: bool):

        content = self.bot.i18n.get(template).format(
            '\n'.join(map(lambda x: self.bot.i18n.get('GAMES_CHESS_MOVE').format(x[0], x[1].mention), self.moves)),
            self.bot.i18n.get('GAMES_CHESS_WHITE') if white else
            self.bot.i18n.get('GAMES_CHESS_BLACK'), )
        if len(content) < 2000:
            return await self.original_context.edit(content=content)

        content = self.bot.i18n.get(template + '_MARKDOWN').format(
            '\n'.join(map(lambda x: self.bot.i18n.get('GAMES_CHESS_MOVE').format(x[0], x[1].display_name), self.moves)),
            self.bot.i18n.get('GAMES_CHESS_WHITE') if white else
            self.bot.i18n.get('GAMES_CHESS_BLACK'), )

        await self.original_context.edit(content='', file=discord.File(fp=io.StringIO(content),
                                                                       filename='moves.md'))

    async def check_result(self, interaction: discord.Interaction):
        if self.chess_game.in_checkmate():
            if self.chess_game.turn:
                content = self.bot.i18n.get('GAMES_CHESS_WON').format(
                    self.bot.i18n.get('GAMES_CHESS_BLACK'),
                    ', '.join(map(lambda x: x.mention, self.black_players)))
            else:
                content = self.bot.i18n.get('GAMES_CHESS_WON').format(
                    self.bot.i18n.get('GAMES_CHESS_WHITE'),
                    ', '.join(map(lambda x: x.mention, self.white_players)))
        elif self.chess_game.in_stalemate():
            content = self.bot.i18n.get('GAMES_CHESS_STALEMATE').format(
                ', '.join(map(lambda x: x.mention, self.black_players + self.white_players)))
        else:
            return
        await (await interaction.channel.fetch_message(self.suffix_message)).edit(
            content=content, view=None)

    def on_promotion_piece(self, piece: Type[Piece]):
        async def on_promotion(button: ChessButton, interaction: discord.Interaction):
            if not self.chess_game.turn and interaction.user in self.black_players:
                return
            if self.chess_game.turn and interaction.user in self.white_players:
                return

            await interaction.response.defer()

            self.moves.append((self.bot.i18n.get('GAMES_CHESS_PROMOTED_MOVE')
                               .format(self.bot.i18n.get('GAMES_CHESS_PIECE_{}'.format(piece(False).name))),
                               interaction.user,))

            self.chess_game.promotion(self.promotion_square, piece)

            self.promotion_square = None

            await (await interaction.channel.fetch_message(self.suffix_message)).edit(
                content=self.suffix_content, view=None)

            await self.check_send_prefix_message('GAMES_CHESS_TO_MOVE_HEADER', self.chess_game.turn)

            for i in range(len(self.views)):
                view = self.views[i]
                self.update_view(view)
                await (await interaction.channel.fetch_message(self.view_messages[i])).edit(view=view)

            await self.check_result(interaction)

        return on_promotion

    async def on_click(self, button: ChessButton, interaction: discord.Interaction):
        if self.chess_game.turn and interaction.user in self.black_players:
            return await interaction.response.send_message(
                embed=discord.Embed(title=self.bot.i18n.get('GAMES_NOT_YOUR_TURN'), color=discord.Color.red()),
                ephemeral=True)
        if not self.chess_game.turn and interaction.user in self.white_players:
            return await interaction.response.send_message(
                embed=discord.Embed(title=self.bot.i18n.get('GAMES_NOT_YOUR_TURN'), color=discord.Color.red()),
                ephemeral=True)
        await interaction.response.defer()

        if self.selected_pos is None:
            self.selected_pos = button.pos

            for i in range(len(self.views)):
                view = self.views[i]
                for child in view.children:
                    valid_move = self.chess_game.is_valid_move(self.selected_pos, child.pos)
                    if self.selected_pos == child.pos:
                        child.disabled = False
                        child.style = child.default_style
                    elif valid_move:
                        child.disabled = False
                        child.style = discord.ButtonStyle.primary
                    else:
                        child.disabled = True
                        child.style = child.default_style

                await (await interaction.channel.fetch_message(self.view_messages[i])).edit(view=view)
            return

        if self.selected_pos == button.pos:
            self.selected_pos = None
        else:
            if not self.chess_game.is_valid_move(self.selected_pos, button.pos):
                return

            self.chess_game.move(self.selected_pos, button.pos)
            self.moves.append((translate_back(self.selected_pos) + translate_back(button.pos),
                               interaction.user))

            if not self.chess_game.turn and interaction.user not in self.white_players:
                self.white_players.append(interaction.user)
            if self.chess_game.turn and interaction.user not in self.black_players:
                self.black_players.append(interaction.user)

            promotion_square = self.chess_game.check_promotion()

            self.selected_pos = None

            if promotion_square is not None:
                self.promotion_square = promotion_square
                await (await interaction.channel.fetch_message(self.suffix_message)).edit(
                    content=self.bot.i18n.get('GAMES_CHESS_PROMOTE_TO'), view=self.promotion_view)

                for i in range(len(self.views)):
                    view = self.views[i]

                    for child in view.children:
                        child.disabled = True
                        if child.pos == self.promotion_square:
                            child.label = '🧨'
                            child.style = discord.ButtonStyle.primary
                        else:
                            child.style = child.default_style

                    await (await interaction.channel.fetch_message(self.view_messages[i])).edit(view=view)

                await self.check_send_prefix_message('GAMES_CHESS_TO_PROMOTE_HEADER',
                                                     not self.chess_game.turn)

                return

            await self.check_send_prefix_message('GAMES_CHESS_TO_MOVE_HEADER',
                                                 self.chess_game.turn)

        for i in range(len(self.views)):
            view = self.views[i]
            self.update_view(view)

            await (await interaction.channel.fetch_message(self.view_messages[i])).edit(view=view)

        await self.check_result(interaction)

    def update_view(self, view: ChessView):
        for child in view.children:
            piece = self.chess_game.board.board[child.pos[0]][child.pos[1]]
            child.style = child.default_style
            if piece is None or piece.ghost:
                child.disabled = True
                child.label = "\u200b"
            else:
                child.label = str(piece.emoji())
                child.disabled = self.chess_game.turn != piece.color or not self.chess_game.has_valid_move(child.pos)

    def __init__(self, bot: 'DiscordBot', ctx: discord.commands.context.ApplicationContext):
        self.bot = bot

        self.selected_pos: tuple[int, int] or None = None
        self.promotion_square: tuple[int, int] or None = None
        self.suffix_message: int or None = None

        self.chess_game: Chess = Chess(Board.small())

        self.suffix_content = '=' * 29

        self.views = [
            ChessView(self.on_click, 4, 4, 0, 0),
            ChessView(self.on_click, 4, 4, 0, 4)
        ]

        self.promotion_list = [
            Knight(False),
            Bishop(False),
            Rook(False),
            Queen(False)
        ]

        self.promotion_view = discord.ui.View()
        for i in range(len(self.promotion_list)):
            piece = self.promotion_list[i]
            child = ChessButton(i, 0, (0, i), self.on_promotion_piece(type(piece)), True)
            child.style = discord.ButtonStyle.primary
            child.label = piece.emoji()
            self.promotion_view.add_item(child)

        self.original_context: discord.commands.context.ApplicationContext = ctx
        self.view_messages: list[int] or None = None
        self.current_player = True
        self.white_players = []
        self.black_players = []

        self.moves = []

    async def start(self):
        for view in self.views:
            self.update_view(view)

        await self.original_context.respond(self.bot.i18n.get('GAMES_CHESS_TO_MOVE_HEADER')
                                            .format('', self.bot.i18n.get('GAMES_CHESS_WHITE')))
        self.view_messages = []
        for view in self.views:
            self.view_messages.append((await self.original_context.send(view=view)).id)
        self.suffix_message = (await self.original_context.send(content=self.suffix_content)).id


BOARD_TRANSLATE_KEYS = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}


def translate(s):
    """
    Translates traditional board coordinates of chess into list indices
    """
    try:
        row = s[0]
        col = int(s[1])
        if col < 1 or col > 8:
            print(s[0] + "is not in the range from 1 - 8")
            return None
        if row < 'a' or row > 'h':
            print(s[1] + "is not in the range from a - h")
            return None
        return 8 - col, BOARD_TRANSLATE_KEYS[row]
    except ValueError or KeyError:
        print("{} is not in the format '[letter][number]'".format(s))
        return None


def translate_back(pos: tuple[int, int]):
    return '{}{}'.format(list(BOARD_TRANSLATE_KEYS.keys())[pos[1]], 8 - pos[0])


def main(pre_moves=None):
    if pre_moves is None:
        pre_moves = []

    chess = Chess(Board.default())
    print(str(chess.board))

    def _move(s):
        promo = chess.check_promotion()
        if promo is not None:
            if s not in ['Q', 'R', 'N', 'B', '']:
                print("Not a valid promotion piece")
                return
            chess.promotion_by_string(s, promo)

        else:
            split = s.split(' ')

            if len(split) == 2:
                start, to = split[:2]
            elif len(split) == 1 and len(split[0]) == 4:
                start, to = split[0][:2], split[0][2:]
            else:
                return

            start = translate(start)
            to = translate(to)
            print(start, to)

            if start is None or to is None:
                return

            try:
                chess.move(start, to)
            except:
                pass

            if chess.in_checkmate():
                print('You won!')
            elif chess.in_stalemate():
                print('its a Stalemate')

        print(str(chess.board))

    for m in pre_moves:
        _move(m)

    while True:

        if chess.check_promotion():
            _move(input("Promote pawn to [Q, R, N, B]: "))
        else:
            _move(input("Move (e.g. a2 a4): "))


if __name__ == "__main__":
    main([
        'a2a4',
        'b8c6',
        'x',
        'c6b8',
        'b2b4',
        'b8c6',
        'c1b2',
        'c6b8',
        'b1c3',
        'b8c6',
        'd1b1',
        'c6b8',
        'b1a2',
        'b8c6',
        'e1c1',
        'h2h4',
        'c6b8',
        'h1h3',
        'b8c6',
        'g1f3',
        'c6b8',
        'e2e3',
        'b8c6',
        'f1e2',
        'c6b8',
        'e1g1',
        'h3h1',
        'b8c6',
        'e1g1'
    ])
