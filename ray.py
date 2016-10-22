from game import Player, Move, targetting_cards

GUARD = 1
PRIEST = 2
BARON = 3
HANDMAID = 4
PRINCE = 5
KING = 6
COUNTESS = 7
PRINCESS = 8

full_deck_counts = {
  GUARD: 5,
  PRIEST: 2, BARON: 2, HANDMAID: 2, PRINCE: 2,
  KING: 1, COUNTESS: 1, PRINCESS: 1
}

class Ray(Player):
  """
  Ray's AI
  """

  def get_brain_name(self):
    return 'ray'

  def new_game(self, initial_card, other_players):
    self.remaining_cards = full_deck_counts.copy()
    self.current_card = initial_card
    self.others = other_players

  def decide_turn(self, drawn, **info):
    # Components of the move
    card = None
    player = None
    guess = None

    # Discard the countess if we draw it
    if self.current_card == COUNTESS and drawn in [5,6]:
      self.current_card, card = drawn, self.current_card
    # Otherwise play the drawn card
    else:
      card = drawn

    # Target someone if we need to
    if card in targetting_cards:
      available = [p for p in self.others if p not in info['immune']]
      if available:
        player = available[0]
      elif not available and card == 5:
        player = self

    # Guess someone if we need to
    if card == GUARD:
      guess = self.guess_card()

    return Move("it's raining", card, player, guess)

  def guess_card(self):
    max_card, max_count = None, -1
    for card, count in self.remaining_cards.iteritems():
      # Cannot guess guard
      if card == GUARD:
        continue
      if count > max_count:
        max_card, max_count = card, count
    return max_card

  def card_discarded(self, card):
    self.remaining_cards[card] = self.remaining_cards[card]-1

  def player_discarded(self, player, card):
    self.card_discarded(card)

  def player_moved(self, player, move):
    self.card_discarded(move.card)
#
#  def player_revealed(self, player, card):
#    pass
#
  def replace_card(self, card):
    self.current_card = card

  def player_dead(self, player, last_card):
    self.others.remove(player)
