from game import Player, Move, targetting_cards

class Dumb(Player):
  """
  Minimal legal move player, frequently suicides unnecessarily
  """
  def get_brain_name(self):
    return 'dumb'

  def new_game(self, initial_card, other_players):
    self.current_card = initial_card
    self.others = other_players

  def decide_turn(self, card, **info):
    player = None

    if self.current_card == 7 and card in [5,6]:
      self.current_card, card = card, 7

    if card in targetting_cards:
      available = [p for p in self.others if p not in info['immune']]
      if available:
        player = available[0]
      elif not available and card == 5:
        player = self

    guess = None
    if card == 1:
      guess = 2

    return Move("I'm dumb", card, player, guess)

#  def player_discarded(self, player, card):
#    pass
#
#  def player_moved(self, player, move):
#    pass
#
#  def player_revealed(self, player, card):
#    pass
#
  def replace_card(self, card):
    self.current_card = card

  def player_dead(self, player, last_card):
    self.others.remove(player)

