VERSION_NUMBER = '2.2'


PLAYING_STRING_DEFAULT = "Playing: %s - %s: %s."
PLAYING_STRING_COMMANDS_DEFAULT = "\nCommands:\n - q (stop),\n - space (pause/resume), \n - d (next),\n - a (restart),\n - z (previous),\n - 0-9 (set volume)"
PLAYING_STRING_COMMANDS_SPECIAL = PLAYING_STRING_COMMANDS_DEFAULT + "\n - d (next)"
player_actions = ['resume', 'next', 'pause', 'restart', 'previous', 'stop', 'volume']
player_stop = 'stop'
list_of_speech_commands = ['quit', 'single', 'shuffle', 'play', 'voice', 'debug', 'auto', 'select', 'no', 'yes']
quit_string = '406'
alb_mode_string = 'alb'
perf_search_string = 'se'

chromedriver_update_url = "https://chromedriver.chromium.org"



"""
iTunesSearchAPI keys used
"""
track_name='trackName'
artist_name='artistName'
collection_name='collectionName'
artworkUrl100='artworkUrl100'
primary_genre_name='primaryGenreName'
track_num='trackNumber'
track_count='trackCount'
collection_id = 'collectionId'
collection_artist_name = 'collectionArtistName'
