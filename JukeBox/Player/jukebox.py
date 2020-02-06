import vlc
import os, sys
import threading

def play_file(prompt, file_path, startup_time=1.5):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(file_path)
    media.get_mrl()
    player.set_media(media)
    player.play()
    wait_until_end(player, prompt)
    player.stop()
    return


def wait_until_end(player, prompt):
    Ended = 6 # code for ended in vlc
    print(prompt)
    try:
        current_state = player.get_state()
        while current_state != Ended:
            current_state = player.get_state()
    except KeyboardInterrupt:
        sys.stderr.write("\r")
        return
