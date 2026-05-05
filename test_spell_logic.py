"""
Unit tests for Spell Chess game logic.

Run with:
    pytest test_spell_logic.py -v

These tests verify the Spell Chess rules described in SPELL_CHESS_RULES.md.
Each test creates a fresh SpellChessGame, sets up a position, performs an
action, and checks that the result matches the specification.
"""

import chess
from spell_logic import SpellChessGame, squares_in_3x3, squares_in_jump_range


# ------------------------------------------------------------------ #
#  Demo tests — provided to students as examples                      #
# ------------------------------------------------------------------ #

class TestFreezeTarget:
    """Casting Freeze should mark the opponent's color as frozen."""

    def test_freeze_affects_opponent_not_caster(self):
        game = SpellChessGame()
        # White casts freeze
        game.cast_freeze(chess.E5)
        # The frozen color should be Black (the opponent), not White
        assert game.freeze_effect_color == chess.BLACK


class TestNewGameResetsBoard:
    """Calling new_game() should bring the board back to the starting position."""

    def test_board_resets_after_moves(self):
        game = SpellChessGame()
        game.board.push_san("e4")
        game.new_game()
        assert game.board.fen() == chess.STARTING_FEN


# ------------------------------------------------------------------ #
#  YOUR TESTS GO BELOW                                                #
#  Write tests that check the rules from SPELL_CHESS_RULES.md.        #
#  If a test fails, you've found a bug — document it!                 #
# ------------------------------------------------------------------ #
# ------------------------------------------------------------------
# Freeze Spell Tests
# ------------------------------------------------------------------
class TestFreezeSpellInitialState:
    """Tests for the initial Freeze spell state."""

    def test_initial_freeze_charges_are_five_for_both_players(self):
        """Each side should begin the game with 5 Freeze charges."""
        game = SpellChessGame()

        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5

    def test_initial_freeze_cooldowns_are_zero_for_both_players(self):
        """Each side should begin the game with no Freeze cooldown."""
        game = SpellChessGame()

        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0

    def test_initial_freeze_effect_is_inactive(self):
        """A new game should not have an active Freeze effect."""
        game = SpellChessGame()

        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0

class TestFreezeArea:
    """Tests for the 3x3 Freeze area helper."""

    def test_squares_in_3x3_center_includes_nine_squares(self):
        """
        A Freeze centered in the middle of the board should include the center
        square and all 8 surrounding squares.
        """
        squares = squares_in_3x3(chess.E4)

        expected = {
            chess.D3, chess.E3, chess.F3,
            chess.D4, chess.E4, chess.F4,
            chess.D5, chess.E5, chess.F5,
        }

        assert squares == expected
        assert len(squares) == 9

    def test_squares_in_3x3_corner_includes_only_valid_board_squares(self):
        """
        A Freeze centered on a corner should include only valid board squares,
        including the center corner square itself.
        """
        squares = squares_in_3x3(chess.A1)

        expected = {
            chess.A1, chess.A2,
            chess.B1, chess.B2,
        }

        assert squares == expected
        assert len(squares) == 4


class TestFreezeCasting:
    """Tests for valid and invalid Freeze casting."""

    def test_cast_freeze_returns_true_when_valid(self):
        """Casting Freeze before moving with available charges should succeed."""
        game = SpellChessGame()

        result = game.cast_freeze(chess.E4)

        assert result is True

    def test_cast_freeze_costs_one_charge(self):
        """Each successful Freeze cast should cost exactly 1 charge."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_remaining[chess.WHITE] == 4

    def test_freeze_does_not_mark_caster_as_frozen(self):
        """Freeze should not mark the caster's own color as frozen."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_effect_color != chess.WHITE

    def test_freeze_effect_stores_opponent_color(self):
        """If White casts Freeze, Black should be the frozen color."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_effect_color == chess.BLACK

    def test_freeze_effect_stores_selected_3x3_area(self):
        """Casting Freeze should store the 3x3 area centered on the selected square."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        expected = {
            chess.D3, chess.E3, chess.F3,
            chess.D4, chess.E4, chess.F4,
            chess.D5, chess.E5, chess.F5,
        }

        assert game.freeze_effect_squares == expected

    def test_freeze_cooldown_starts_at_three_after_casting(self):
        """After casting Freeze, the caster should enter a 3-turn cooldown."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_cooldown[chess.WHITE] == 3

    def test_freeze_effect_duration_is_one_opponent_turn(self):
        """Freeze should last for exactly 1 opponent turn."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_effect_plies_left == 1

    def test_spell_casted_this_turn_is_marked_after_freeze(self):
        """After casting Freeze, spell_casted_this_turn should be True."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.spell_casted_this_turn is True

    def test_cannot_cast_freeze_twice_in_same_turn(self):
        """A player should not be able to cast Freeze twice in the same turn."""
        game = SpellChessGame()

        first = game.cast_freeze(chess.E4)
        second = game.cast_freeze(chess.D4)

        assert first is True
        assert second is False

    def test_cannot_cast_freeze_after_moving(self):
        """A player should not be able to cast Freeze after making a move."""
        game = SpellChessGame()

        game.make_move(chess.G1, chess.F3)
        result = game.cast_freeze(chess.E5)

        assert result is False

    def test_cannot_cast_freeze_when_no_charges_remaining(self):
        """A player with 0 Freeze charges should not be able to cast Freeze."""
        game = SpellChessGame()
        game.freeze_remaining[chess.WHITE] = 0

        result = game.cast_freeze(chess.E4)

        assert result is False

    def test_cannot_cast_freeze_during_cooldown(self):
        """A player cannot cast Freeze while Freeze cooldown is active."""
        game = SpellChessGame()
        game.freeze_cooldown[chess.WHITE] = 1

        result = game.cast_freeze(chess.E4)

        assert result is False

    def test_failed_freeze_cast_does_not_change_state(self):
        """A failed Freeze cast should not consume charges or create an active effect."""
        game = SpellChessGame()
        game.freeze_cooldown[chess.WHITE] = 1

        result = game.cast_freeze(chess.E4)

        assert result is False
        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0


class TestFreezeQueriesAndMovement:
    """Tests for frozen state queries and movement restrictions."""

    def test_is_frozen_returns_true_for_opponent_piece_in_frozen_area(self):
        """
        If White casts Freeze centered on E7, the Black pawn on E7 should be
        considered frozen.
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)

        assert game.is_frozen(chess.E7, chess.BLACK) is True

    def test_is_frozen_returns_false_for_caster_piece(self):
        """Freeze should not mark the caster's own piece as frozen."""
        game = SpellChessGame()

        game.cast_freeze(chess.E2)

        assert game.is_frozen(chess.E2, chess.WHITE) is False

    def test_get_legal_moves_excludes_moves_from_frozen_square(self):
        """
        Moves that originate from frozen squares should not appear in get_legal_moves().
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)
        game.make_move(chess.G1, chess.F3)  # White moves, now Black should move

        legal_moves = game.get_legal_moves()
        illegal_origin_moves = [
            move for move in legal_moves
            if move.from_square == chess.E7
        ]

        assert illegal_origin_moves == []

    def test_frozen_piece_cannot_be_moved(self):
        """
        A piece in the frozen area should not be movable on the opponent's next turn.
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)
        game.make_move(chess.G1, chess.F3)  # White moves, Black's turn starts

        result = game.make_move(chess.E7, chess.E6)

        assert result is False

    def test_frozen_piece_remains_on_board(self):
        """A frozen piece should remain on the board and still occupy its square."""
        game = SpellChessGame()

        game.cast_freeze(chess.E7)

        piece = game.board.piece_at(chess.E7)

        assert piece is not None
        assert piece.color == chess.BLACK
        assert piece.piece_type == chess.PAWN

    def test_non_frozen_piece_can_still_move(self):
        """
        A piece outside the frozen area should still be movable.
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)
        game.make_move(chess.G1, chess.F3)  # White moves, Black's turn starts

        result = game.make_move(chess.A7, chess.A6)

        assert result is True


class TestFreezeCooldownAndDuration:
    """Tests for Freeze cooldown and duration lifecycle."""

    def test_on_turn_start_decrements_freeze_cooldown_for_current_player(self):
        """
        Freeze cooldown should decrease by 1 at the start of each caster's turn.
        """
        game = SpellChessGame()
        game.freeze_cooldown[chess.WHITE] = 3
        game.board.turn = chess.WHITE

        game.on_turn_start()

        assert game.freeze_cooldown[chess.WHITE] == 2

    def test_freeze_remains_active_at_start_of_opponent_turn(self):
        """
        After the caster moves, Freeze should still be active when the opponent's turn starts.
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)
        game.make_move(chess.G1, chess.F3)

        assert game.freeze_effect_color == chess.BLACK
        assert game.is_frozen(chess.E7, chess.BLACK) is True

    def test_freeze_expires_after_opponent_completes_one_move(self):
        """
        Freeze should expire after the frozen opponent completes one move.
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)
        game.make_move(chess.G1, chess.F3)  # White moves, Black turn
        game.make_move(chess.A7, chess.A6)  # Black moves, Freeze should expire

        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0

class TestFreezeNewGameReset:
    """Tests for resetting Freeze state with new_game()."""

    def test_new_game_resets_freeze_state(self):
        """new_game() should reset Freeze charges, cooldown, and active effect."""
        game = SpellChessGame()
        game.cast_freeze(chess.E4)
        game.freeze_cooldown[chess.WHITE] = 2

        game.new_game()

        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5
        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0
        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0
        assert game.spell_casted_this_turn is False

    def test_new_game_clears_freeze_effect_after_active_freeze(self):
        """An active Freeze effect should be cleared when starting a new game."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)
        game.new_game()

        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0


# ------------------------------------------------------------------ #
#  Jump Spell Tests                                                   #
# ------------------------------------------------------------------ #

class TestJumpStartingCharges:
    """Each side should begin with exactly 3 jump charges."""

    def test_white_starts_with_3_jump_charges(self):
        game = SpellChessGame()
        assert game.jump_remaining[chess.WHITE] == 3

    def test_black_starts_with_3_jump_charges(self):
        game = SpellChessGame()
        assert game.jump_remaining[chess.BLACK] == 3


class TestJumpRange:
    """Jump destination must be within Chebyshev distance 2."""

    def test_jump_range_excludes_distance_3(self):
        assert chess.E7 not in squares_in_jump_range(chess.E4)

    def test_jump_range_includes_distance_2(self):
        assert chess.E6 in squares_in_jump_range(chess.E4)

    def test_squares_in_jump_range_excludes_origin(self):
        """The jump range helper should not include the piece's current square."""
        assert chess.D4 not in squares_in_jump_range(chess.D4)

    def test_squares_in_jump_range_correct_count_center(self):
        """A center square has exactly 24 squares within Chebyshev distance 2."""
        assert len(squares_in_jump_range(chess.D4)) == 24


class TestJumpKingRestriction:
    """The King cannot be selected as the piece to Jump."""

    def test_cannot_jump_king(self):
        game = SpellChessGame()
        game.board.clear()
        game.board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
        game.board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        game.board.turn = chess.WHITE
        result = game.cast_jump(chess.E1, chess.E3)
        assert result == False

    def test_cannot_jump_opponents_piece(self):
        """A player cannot cast Jump on a piece belonging to the opponent."""
        game = SpellChessGame()
        result = game.cast_jump(chess.E7, chess.E5)
        assert result is False

    def test_new_game_resets_jump_cooldown(self):
        game = SpellChessGame()
        game.board.remove_piece_at(chess.C2)
        game.cast_jump(chess.B1, chess.C3)
        game.new_game()
        assert game.jump_cooldown[chess.WHITE] == 0
        assert game.jump_cooldown[chess.BLACK] == 0


class TestJumpDestinationMustBeEmpty:
    """Jump can only land on an empty square — it cannot capture."""

    def test_cannot_jump_to_occupied_square(self):
        game = SpellChessGame()
        result = game.cast_jump(chess.B1, chess.B3)
        assert result == False

    def test_jump_teleports_piece_ignoring_blockers(self):
        """The piece appears on the destination; intermediate squares are unchanged."""
        game = SpellChessGame()
        game.cast_jump(chess.C1, chess.E3)
        assert game.board.piece_at(chess.E3) is not None
        assert game.board.piece_at(chess.C1) is None


class TestJumpCooldownAndCharges:
    """Cooldown, charge deduction, and new_game() reset behavior."""

    def test_jump_cooldown_is_2_turns(self):
        game = SpellChessGame()
        game.board.remove_piece_at(chess.C2)
        game.cast_jump(chess.B1, chess.D1)
        assert game.jump_cooldown[chess.WHITE] == 2

    def test_jump_deducts_one_charge(self):
        game = SpellChessGame()
        before = game.jump_remaining[chess.WHITE]
        game.board.remove_piece_at(chess.C2)
        game.cast_jump(chess.B1, chess.C3)
        assert game.jump_remaining[chess.WHITE] == before - 1

    def test_jump_with_zero_charges_fails(self):
        """A player with 0 jump charges cannot cast Jump."""
        game = SpellChessGame()
        game.jump_remaining[chess.WHITE] = 0
        result = game.cast_jump(chess.G1, chess.F3)
        assert result is False

    def test_jump_during_cooldown_fails(self):
        """Casting Jump while jump_cooldown > 0 must be rejected."""
        game = SpellChessGame()
        game.jump_cooldown[chess.WHITE] = 1
        result = game.cast_jump(chess.G1, chess.F3)
        assert result is False

    def test_jump_cooldown_decrements_each_turn(self):
        """The jump cooldown decreases by 1 at the start of each of the caster's turns."""
        game = SpellChessGame()
        game.board.remove_piece_at(chess.C2)
        game.cast_jump(chess.B1, chess.C3)
        game.make_move(chess.E2, chess.E4)
        game.make_move(chess.E7, chess.E5)
        assert game.jump_cooldown[chess.WHITE] == 1

    def test_cannot_cast_jump_twice_in_one_turn(self):
        game = SpellChessGame()
        game.board.remove_piece_at(chess.C2)
        game.cast_jump(chess.B1, chess.C3)
        result = game.cast_jump(chess.G1, chess.F3)
        assert result == False

    def test_jump_must_be_before_move(self):
        """Casting Jump after already making a move this turn must be rejected."""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        result = game.cast_jump(chess.G1, chess.F3)
        assert result is False

    def test_new_game_resets_jump_charges(self):
        game = SpellChessGame()
        game.board.remove_piece_at(chess.C2)
        game.cast_jump(chess.B1, chess.C3)
        game.new_game()
        assert game.jump_remaining[chess.WHITE] == 3
        assert game.jump_remaining[chess.BLACK] == 3

    def test_cannot_jump_opponents_piece(self):
        game = SpellChessGame()
        result = game.cast_jump(chess.E7, chess.E5)
        assert result == False


# ------------------------------------------------------------------ #
#  Standard Chess / Display / Reset Tests   (Owner: Rutav)            #
#  Traces to SPELL_CHESS_RULES.md and LISCO Spec SP-005..SP-008       #
# ------------------------------------------------------------------ #


# ================================================================== #
#  Standard Chess Tests (Chess-01 .. Chess-12)                       #
#  Covers turn order, legal/illegal moves, special moves, game end.  #
# ================================================================== #

class TestStandardChess:
    """Standard chess rules — turns, captures, special moves, game end."""

    # Chess-01
    def test_initial_turn_is_white(self):
        """At game start, it is White's turn (FIDE rule 1.2)."""
        game = SpellChessGame()
        assert game.current_turn() == chess.WHITE

    # Chess-02
    def test_turn_alternates_after_white_move(self):
        """After White's legal move, it should be Black's turn.
        BUG: after_move_pushed() flips board.turn back, so the side
        to move never actually advances after a successful move."""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        assert game.current_turn() == chess.BLACK

    # Chess-03
    def test_legal_pawn_move_accepted(self):
        """A legal pawn opening (e2-e4) is accepted."""
        game = SpellChessGame()
        assert game.make_move(chess.E2, chess.E4) is True

    # Chess-04
    def test_illegal_pawn_move_rejected(self):
        """A pawn cannot advance three squares from its starting square."""
        game = SpellChessGame()
        assert game.make_move(chess.E2, chess.E5) is False

    # Chess-05
    def test_cannot_move_opponents_piece(self):
        """White cannot move a Black piece on White's turn."""
        game = SpellChessGame()
        # Black pawn on e7 — White attempts to move it
        assert game.make_move(chess.E7, chess.E5) is False

    # Chess-06
    def test_castling_kingside_works(self):
        """White can castle kingside when path is clear and rights are intact."""
        game = SpellChessGame()
        game.board.set_fen(
            "rnbqk2r/pppp1ppp/5n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        )
        assert game.make_move(chess.E1, chess.G1) is True

    # Chess-07
    def test_en_passant_capture_works(self):
        """En passant: pawn captures diagonally onto an empty square.
        BUG: make_move rejects pawn moves to empty squares on different
        files, which is exactly what en passant looks like."""
        game = SpellChessGame()
        # White pawn on e5; Black just played d7-d5 (en passant target d6)
        game.board.set_fen(
            "rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3"
        )
        assert game.make_move(chess.E5, chess.D6) is True

    # Chess-08
    def test_pawn_promotes_to_queen(self):
        """Pawn reaching last rank promotes to Queen when requested."""
        game = SpellChessGame()
        game.board.set_fen("8/P7/8/8/8/8/8/k6K w - - 0 1")
        game.make_move(chess.A7, chess.A8, promotion=chess.QUEEN)
        piece = game.board.piece_at(chess.A8)
        assert piece is not None and piece.piece_type == chess.QUEEN

    # Chess-09
    def test_pawn_promotes_to_knight(self):
        """Pawn should be able to promote to Knight when requested.
        BUG: prepare_move returns the move WITHOUT a promotion field
        when KNIGHT is requested, so the pawn never actually becomes a knight."""
        game = SpellChessGame()
        game.board.set_fen("8/P7/8/8/8/8/8/k6K w - - 0 1")
        game.make_move(chess.A7, chess.A8, promotion=chess.KNIGHT)
        piece = game.board.piece_at(chess.A8)
        assert piece is not None and piece.piece_type == chess.KNIGHT

    # Chess-10
    def test_pawn_promotes_to_rook(self):
        """Pawn promotes to Rook when requested."""
        game = SpellChessGame()
        game.board.set_fen("8/P7/8/8/8/8/8/k6K w - - 0 1")
        game.make_move(chess.A7, chess.A8, promotion=chess.ROOK)
        piece = game.board.piece_at(chess.A8)
        assert piece is not None and piece.piece_type == chess.ROOK

    # Chess-11
    def test_checkmate_ends_game(self):
        """Fool's Mate position should be recognised as game over."""
        game = SpellChessGame()
        # Push directly via board to bypass make_move's turn-flip bug
        for san in ["f3", "e5", "g4", "Qh4#"]:
            game.board.push_san(san)
        assert game.is_game_over() is True

    # Chess-12
    def test_stalemate_ends_game(self):
        """A stalemate position should be recognised as game over."""
        game = SpellChessGame()
        # Black king on h8 has no legal moves and is not in check
        game.board.set_fen("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
        assert game.is_game_over() is True


# ================================================================== #
#  Display Tests (Display-01 .. Display-08)                          #
#  Covers status_text, freeze_info_text, jump_info_text, is_frozen,  #
#  get_legal_moves — the human-readable state surface.               #
# ================================================================== #

class TestDisplay:
    """Display / state-query surface that drives the UI labels."""

    # Display-01
    def test_status_text_shows_white_at_start(self):
        """Status text at start should mention White."""
        game = SpellChessGame()
        assert "White" in game.status_text()

    # Display-02
    def test_status_text_shows_black_after_white_moves(self):
        """After White moves, status text should mention Black.
        BUG (symptom of turn-flip in after_move_pushed): turn never advances."""
        game = SpellChessGame()
        game.make_move(chess.E2, chess.E4)
        assert "Black" in game.status_text()

    # Display-03
    def test_status_text_shows_check(self):
        """When the side to move is in check, status text should indicate it."""
        game = SpellChessGame()
        # Black king on e8 in check from White queen on e7
        game.board.set_fen("4k3/4Q3/8/8/8/8/8/4K3 b - - 0 1")
        assert "check" in game.status_text().lower()

    # Display-04
    def test_status_text_shows_game_over(self):
        """When the game is over, status text should reflect that."""
        game = SpellChessGame()
        for san in ["f3", "e5", "g4", "Qh4#"]:
            game.board.push_san(san)
        assert "game over" in game.status_text().lower()

    # Display-05
    def test_freeze_info_text_at_start(self):
        """Freeze label at start should show 5 charges for the side to move."""
        game = SpellChessGame()
        assert "Freeze: 5" in game.freeze_info_text()

    # Display-06
    def test_jump_info_text_at_start(self):
        """Jump label at start should show 3 charges for the side to move."""
        game = SpellChessGame()
        assert "Jump: 3" in game.jump_info_text()

    # Display-07
    def test_is_frozen_false_at_start(self):
        """No square is frozen for either color at game start."""
        game = SpellChessGame()
        assert game.is_frozen(chess.E4, chess.WHITE) is False
        assert game.is_frozen(chess.E4, chess.BLACK) is False

    # Display-08
    def test_legal_moves_count_at_start(self):
        """The standard starting position has exactly 20 legal moves."""
        game = SpellChessGame()
        assert len(game.get_legal_moves()) == 20


# ================================================================== #
#  Reset Tests (Reset-01 .. Reset-08)                                #
#  Covers new_game() — every piece of state must return to baseline. #
# ================================================================== #

class TestReset:
    """new_game() must restore every piece of state to a fresh-game baseline."""

    # Reset-01
    def test_new_game_resets_board(self):
        """new_game() should reset the board to STARTING_FEN.
        BUG: new_game() never calls self.board.reset(), so prior moves persist."""
        game = SpellChessGame()
        game.board.push_san("e4")
        game.board.push_san("e5")
        game.new_game()
        assert game.board.fen() == chess.STARTING_FEN

    # Reset-02
    def test_new_game_clears_move_history(self):
        """new_game() should clear the move stack.
        BUG (transitive): board is not reset, so move stack persists."""
        game = SpellChessGame()
        game.board.push_san("e4")
        game.new_game()
        assert len(game.board.move_stack) == 0

    # Reset-03
    def test_new_game_turn_is_white(self):
        """After new_game(), it should be White's turn."""
        game = SpellChessGame()
        game.board.push_san("e4")  # turn becomes Black
        game.new_game()
        assert game.current_turn() == chess.WHITE

    # Reset-04
    def test_new_game_resets_freeze_charges(self):
        """new_game() should restore both freeze charge counts to 5."""
        game = SpellChessGame()
        game.freeze_remaining[chess.WHITE] = 0
        game.freeze_remaining[chess.BLACK] = 2
        game.new_game()
        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5

    # Reset-05
    def test_new_game_resets_freeze_cooldown(self):
        """new_game() should clear freeze cooldowns for both sides."""
        game = SpellChessGame()
        game.freeze_cooldown[chess.WHITE] = 3
        game.freeze_cooldown[chess.BLACK] = 1
        game.new_game()
        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0

    # Reset-06
    def test_new_game_clears_active_freeze(self):
        """new_game() should clear any active freeze effect."""
        game = SpellChessGame()
        game.freeze_effect_color = chess.BLACK
        game.freeze_effect_squares = {chess.E4, chess.E5}
        game.freeze_effect_plies_left = 1
        game.new_game()
        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0

    # Reset-07
    def test_new_game_resets_spell_casted_flag(self):
        """new_game() should clear the per-turn spell-cast flag."""
        game = SpellChessGame()
        game.spell_casted_this_turn = True
        game.new_game()
        assert game.spell_casted_this_turn is False

    # Reset-08
    def test_new_game_resets_jump_casted_flag(self):
        """new_game() should clear the per-turn jump-cast flag."""
        game = SpellChessGame()
        game.jump_casted_this_turn = True
        game.new_game()
        assert game.jump_casted_this_turn is False