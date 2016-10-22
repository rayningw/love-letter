import random

card_names = {
  1:'Guard',
  2:'Priest',
  3:'Baron',
  4:'Handmaid',
  5:'Prince',
  6:'King',
  7:'Countess',
  8:'Princess'
}

full_deck = 5*[1] + 2*[2,3,4,5] + [6,7,8]
targetting_cards = [1,2,3,5,6]
# Must target someone who is not yourself
must_target_others = [1,2,3,6]

def verbose_name(card):
  return card_names[card] + '(%d)' % card

class Move:
  def __init__(self, message, card, player=None, guess=None):
    """
    message - anything at all to say to your fellow AIs
    card - which card to play
    player - optional targetted player, if applicable to move
    guess - when playing the Guard, what card is guessed
    """

    assert card >= 1 and card <= 8

    if card == 5:
      assert player

    if card == 1 and player:
      assert guess >= 2 and guess <= 8

    self.message = message
    self.card = card
    self.player = player
    self.guess = guess

  def __str__(self):
    res = card_names[self.card]
    if self.player:
      res += ' targetting ' + str(self.player)
    if self.guess:
      res += ' guessing ' + card_names[self.guess]

    res += ' saying ' + repr(self.message)

    return res

class Player:
  def set_name(self, name):
    self.name = name

  def get_name(self):
    return self.name

  def __str__(self):
    return self.get_name()

  def __repr__(self):
    return str(self)

  # Override these:

  def get_brain_name(self):
    raise Exception("Name yourself")

  def new_game(self, initial_card, other_players):
    pass

  def decide_turn(self, card, **info):
    return Move(8)

  # Player was forced to discard a card
  def player_discarded(self, player, card):
    pass

  # Player made a move with a particlar card which discards it
  def player_moved(self, player, move):
    pass

  def player_revealed(self, player, card):
    pass

  def replace_card(self, card):
    pass

  def player_dead(self, player, last_card):
    pass


def play_game(players):
  """
  Plays a game with a list of players
  """
  players = list(players)
  deck = list(full_deck)
  random.shuffle(deck)

  extra_card = deck.pop()

  #deck, extra_card =  [3, 8, 2, 5, 4, 5, 3, 4, 7, 2, 1, 6, 1, 1, 1] , 1
  # prints a line of code you can paste above here to repeat a game
  print 'deck, extra_card = ', deck, ',', extra_card


  player_map = {}
  immune = set()

  player_cards = {}
  num = 1
  for p in players:
    p.set_name(p.get_brain_name() + str(num))
    player_cards[p] = deck.pop()
    p.new_game(player_cards[p], [other for other in players if other != p])
    player_map[p] = p
    num += 1
    print p, 'starts with ', card_names[player_cards[p]]

  while deck and len(players) > 1:
    next_card = deck.pop()

    current = players[0]

    if current in immune: immune.remove(current)

    move = current.decide_turn(next_card,
      immune = immune)

    print current.get_name(),
    print 'has', card_names[player_cards[current]],
    print 'picks up', card_names[next_card],
    print 'plays', move

    if move.player in immune:
      raise Exception("Illegal move %s" % move)

    if move.player and move.player not in players:
      raise Exception("Invalid target player %s" %  move)

    possible_cards = [next_card, player_cards[current]]
    if move.card not in possible_cards:
      raise Exception("Illegal move %s" % move)

    if (move.card in [5,6]) and (7 in possible_cards):
      raise Exception("Should have played Countess %s" % move)

    def kill(dead):
      print dead, 'is out of the game'
      players.remove(dead)
      for p in players:
        p.player_dead(dead, player_cards[dead])

    for p in players:
      if p != current:
        p.player_moved(current, move)

    if move.card != next_card: player_cards[current] = next_card

    def replace_card(player, card):
      player_cards[player] = card
      player.replace_card(card)

    if move.player is current and move.card != 5:
      raise Exception("can't target self")

    targettable_others = [p for p in players if p != current and p not in immune]
    if move.card in must_target_others and targettable_others and move.player not in targettable_others:
      raise Exception("Must target someone else where possible %s" % move)


    # Guard
    if move.card == 1:
      if move.player:
        if move.guess is player_cards[move.player]:
          kill(move.player)
    # Priest
    if move.card == 2:
      if move.player:
        current.player_revealed(move.player, player_cards[move.player])
    # Baron
    if move.card == 3:
      if move.player:
        a, b = player_cards[current], player_cards[move.player]
        if a > b:
          kill(move.player)
        if b > a:
          kill(current)
    # Handmaid
    if move.card == 4:
      immune.add(current)
    # Prince
    if move.card == 5:
      discarded = player_cards[move.player]
      for p in players:
        if p != current:
          p.player_discarded(move.player, discarded)

      if discarded == 8:
        kill(move.player)
      else:
        new_card = deck and deck.pop() or extra_card
        print '  ', move.player, 'picks up', card_names[new_card]
        replace_card(move.player, new_card)
    # King
    if move.card == 6:
      if move.player:
        a, b = player_cards[move.player], player_cards[current]
        replace_card(current, a)
        replace_card(move.player, b)
    # Countess
    if move.card == 7:
      pass
    # Princess
    if move.card == 8:
      kill(current)

    players = players[1:] + [players[0]]

  if len(players) > 1:
    print 'out of cards - still remaining are', ', '.join(map(str, players))
    players.sort(key=lambda p: -player_cards[p])
    print players[0], 'is the winner'
  else:
    print players[0], 'is the last one standing'

  return players[0]
