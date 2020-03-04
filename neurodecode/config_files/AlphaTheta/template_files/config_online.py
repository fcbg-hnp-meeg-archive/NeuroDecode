#----------------------------------------------------------------------
# Parameters to define
#----------------------------------------------------------------------
DATA_PATH = ''

SPATIAL_FILTER = None
SPATIAL_CHANNELS = ['Fz', 'F3', 'F4', 'F7', 'F8', 'Cz', 'C3', 'C4', 'P3', 'Pz', 'P4']

ALPHA_CHANNELS = ['Pz']
ALPHA_REF = 239550
ALPHA_THR = 376355

THETA_CHANNELS = ['Pz']
THETA_REF = 702870
THETA_THR = 982914

STREAMBUFFER = 2                   # Stream buffer [sec]
WINDOWSIZE = 2                     # window length of acquired data when calling get_window [sec]

TIMER_SLEEP = 0.25*60

NJOBS = 8                          # For multicore PSD processing

ALPHA_FEEDBACK_PATH = r'C:\Users\adesvachez\Documents\meditation_sounds\babbling-brook.wav'
THETA_FEEDBACK_PATH = r'C:\Users\adesvachez\Documents\meditation_sounds\ocean-waves.wav'

ALPHA_SUP_FB_PATH = r'C:\Users\adesvachez\Documents\meditation_sounds\A-Tone.wav'
THETA_SUP_FB_PATH = r'C:\Users\adesvachez\Documents\meditation_sounds\ZenBuddhistTempleBell.wav'