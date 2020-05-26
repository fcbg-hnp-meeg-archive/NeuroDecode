#----------------------------------------------------------------------
# Parameters to define
#----------------------------------------------------------------------
DATA_PATH = ''

SPATIAL_FILTER = None
SPATIAL_CHANNELS = ['Fz', 'F3', 'F4', 'F7', 'F8', 'Cz', 'C3', 'C4', 'P3', 'Pz', 'P4']

STREAMBUFFER = 2                   # Stream buffer [sec]
WINDOWSIZE = 2                     # window length of acquired data when calling get_window [sec]

TIMER_SLEEP = 0.25*60

NJOBS = 4                          # For multicore PSD processing

_root_music_path_ = '/home/sam/Dropbox/proj_data/meditation_sounds'

MUSIC_STATE_1_PATH: f"{_root_music_path_}/snippets/waves 07.wav"
MUSIC_STATE_2_PATH: f"{_root_music_path_}/snippets/Recording of rain shower_AOS01619.wav"

FEATURE_TYPE = 'THETA' # or 'ALPHA_THETA'
MUSIC_MIX_STYLE = 'ADDITIVE_POSITIVE'

