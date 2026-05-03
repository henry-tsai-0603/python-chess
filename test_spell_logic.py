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

class TestFreezeSpell:
    """Unit tests for the Freeze spell rules."""

    def test_initial_freeze_charges_are_five_for_both_players(self):
        """Each side should begin the game with 5 Freeze charges."""
        game = SpellChessGame()

        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5

    def test_cast_freeze_returns_true_when_valid(self):
        """Casting Freeze before moving with available charges should succeed."""
        game = SpellChessGame()

        result = game.cast_freeze(chess.E4)

        assert result is True

    def test_cast_freeze_costs_one_charge(self):
        """Each Freeze cast should cost exactly 1 charge."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_remaining[chess.WHITE] == 4

    def test_freeze_affects_opponent_not_caster(self):
        """Freeze should affect the opponent's color, not the caster's color."""
        game = SpellChessGame()

        game.cast_freeze(chess.E4)

        assert game.freeze_effect_color == chess.BLACK

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

    def test_is_frozen_returns_true_for_opponent_piece_in_frozen_area(self):
        """
        If White casts Freeze centered on E7, the Black pawn on E7 should be
        considered frozen.
        """
        game = SpellChessGame()

        game.cast_freeze(chess.E7)

        assert game.is_frozen(chess.E7, chess.BLACK) is True

    def test_freeze_cooldown_decrements_on_caster_turn_start(self):
        """
        Freeze cooldown should decrease by 1 at the start of each caster's turn.
        """
        game = SpellChessGame()
        game.freeze_cooldown[chess.WHITE] = 3
        game.board.turn = chess.WHITE

        game.on_turn_start()

        assert game.freeze_cooldown[chess.WHITE] == 2

    def test_new_game_resets_freeze_state(self):
        """new_game() should reset Freeze charges, cooldown, and active effect."""
        game = SpellChessGame()
        game.cast_freeze(chess.E4)

        game.new_game()

        assert game.freeze_remaining[chess.WHITE] == 5
        assert game.freeze_remaining[chess.BLACK] == 5
        assert game.freeze_cooldown[chess.WHITE] == 0
        assert game.freeze_cooldown[chess.BLACK] == 0
        assert game.freeze_effect_color is None
        assert game.freeze_effect_squares == set()
        assert game.freeze_effect_plies_left == 0