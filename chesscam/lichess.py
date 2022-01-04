#
# Lichess client for live play.
# Requires an API token with board play permissions.
#
import requests

with open('lichess_token.txt', 'r') as f:
    API_TOKEN = f.read()[:-1]

# Start a new game.
# Get board move.
# Make board move.
# Extra: chat, draw, takeback, claim victory.
