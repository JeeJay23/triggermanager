import vlc 
from time import sleep

_medias = []
_mi = 0

_player = vlc.MediaPlayer ()
_inst = _player.get_instance ()
_vplayer = vlc.MediaPlayer ()
_vplayer_inst = _vplayer.get_instance ()

def exec_player_cmd (mps, func):
    for mp in mps:
        func (mp)

def prep_players (paths):
    global _medias, _inst, _mi

    _medias = [_inst.media_new (p) for p in paths]
    _mi = 0

def skip ():
    global _medias, _mi, _player

    _player.set_media (_medias[_mi])
    _player.play ()
    _mi += 1
    _mi = _mi % len (_medias)

def play (file):
    global _player, _inst
    m = _inst.media_new (file)
    _player.set_media (m)
    _player.play ()
    print ("play: playing: %s" % file)

def play_video (file):
    global _vplayer_inst, _vplayer
    m = _vplayer_inst.media_new (file)
    _vplayer.set_media (m)
    _vplayer.play()

def prep_video_player (first_vid):
    global _vplayer_inst, _vplayer
    m = _vplayer_inst.media_new (first_vid)
    _vplayer.set_media (m)
    _vplayer.play()
    sleep (.5)
    _vplayer.pause ()
    _vplayer.set_position (0)

def stop ():
    global _player
    _player.stop ()

def pause ():
    global _player
    _player.pause ()

def stop_video ():
    global _vplayer
    _vplayer.stop ()

def dummy_func (add = None):
    print ('placeholder function %s' % str (add))