from game import *
from dumb import Dumb

print '========== GAME ==========='
winner = play_game([Dumb(), Dumb(), Dumb(), Dumb()])
print 'WINNER: ', winner
print
