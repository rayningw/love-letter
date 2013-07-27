from game import Player, Move, targetting_cards, full_deck


def flatten(l):
  return [item for sublist in l for item in sublist]

class Reasonable(Player):
  """
  Plays reasonably
  """
  def get_brain_name(self):
    return 'reasonable'

  def new_game(self, initial_card, other_players):
    self.current_card = initial_card
    self.others = other_players

    self.discards = {self:[]}
    for p in other_players: self.discards[p] = []

    self.known = {}

  def decide_turn(self, card, **info):
    preferred_order = [2,4,1,3,7,5,6,8]
    my_card_pair = sorted([self.current_card, card], key=lambda c: preferred_order.index(c))

    card = my_card_pair[0]

    discards = flatten([self.discards[p] for p in [self] + self.others])

    def rotated(l):
      return l[1:] + [l[0]]

    def exclude(cards, excluded):
      while cards and excluded:
        to_exclude = excluded.pop()
        for _ in xrange(len(cards)):
          if cards[0] == to_exclude:
            cards = cards[1:]
            break
          cards = rotated(cards)

      return cards

    def possible_cards(player):
      if player in self.known:
        return [self.known[player]]

      other_hand_cards = my_card_pair + [self.known[p] for p in self.known if p != player]
      excluded_cards = other_hand_cards + discards

      return exclude(full_deck, excluded_cards)

    def possible_higher_cards(player):
      return [c for c in possible_cards(player) if c != 1]

    def avg(l):
      return float(sum(l))/len(l) 

    target = None
    guess = None
    if card in targetting_cards:
      available = [p for p in self.others if p not in info['immune']]
      if available:
        if card == 1:
          # get a list of [ [player1, card1, card2, ...], [player2, card1, card2, ...] ... ]
          options = [[p] + possible_higher_cards(p) for p in available]
          options = [o for o in options if len(o) >= 2] # eliminate known guard-only hands
          options.sort(key=lambda l: len(l))
          if options:
            #print '---', options
            target, guess = options[0][0], options[0][1]
          else:
            #print '--- just a legal one'
            # if there are no possibilities, just make a legal move.
            # we probably shouldn't be playing a guard in the first place
            target, guess = available[0], 2 
        elif card == 2:
          target = ([p for p in self.others if p not in self.known and p in available] + available)[0]
        else:
          #print '---', [[p, possible_cards(p)] for p in available]
          options = [[p, avg(possible_cards(p))] for p in available]

          if card == 3:
            options.sort(key=lambda pair: pair[1])
          else:
            options.sort(key=lambda pair: -pair[1])

          #print '---', options
          target = options[0][0]
      elif not available and card == 5:
        target = self

    self.current_card = my_card_pair[1]
    return Move("Probably a reasonable move", card, target, guess)

  def player_discarded(self, player, card):
    self.discards[player].append(card)

  def player_moved(self, player, move):
    self.discards[player].append(move.card)
    if player in self.known.keys():
      if move.card == self.known[player]:
        # They might still have it for cards <= 5, but
        # it is not certain.
        del self.known[player]

  def player_revealed(self, player, card):
    self.known[player] = card

  def replace_card(self, card):
    # todo: known card coz of king swap
    self.discards[self].append(self.current_card)
    self.current_card = card

  def player_dead(self, player, last_card):
    self.discards[player].append(last_card)
    self.others.remove(player)
