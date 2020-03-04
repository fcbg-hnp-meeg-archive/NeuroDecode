#-------------------------------------------
# Data 
#-------------------------------------------
DATA_PATH = r'C:\Users\adesvachez\git\nd_data\AlphaTheta\a1-AlphaTheta\fif'

EPOCH = [0, 20]

#-------------------------------------------
# Trigger
#-------------------------------------------
TRIGGER_FILE = r'C:\Users\adesvachez\git\NeuroDecode\neurodecode\triggers\triggerdef_16.ini'
TRIGGER_DEF = ['INIT']
LOAD_EVENTS = {'selected':'False', 'False':None, 'True':r''}

#-------------------------------------------
# Channels specification
#-------------------------------------------
PICKED_CHANNELS = ['Pz']
EXCLUDED_CHANNELS = []

REREFERENCE = {'selected':'False', 'False':None, 'True':dict(New=['Cz'], Old=['M1/2', 'M2/2'])}

#-------------------------------------------
# Filters
#-------------------------------------------
SP_FILTER = None
SP_CHANNELS = None 
TP_FILTER = {'selected':'False', 'False':None, 'True':[1, 40]}
NOTCH_FILTER = {'selected':'False', 'False':None, 'True':[50]}

#-------------------------------------------
# Unit conversion
#-------------------------------------------
MULTIPLIER = 1

#-------------------------------------------
# Features
#-------------------------------------------
FEATURES = {'selected':'PSD','PSD':dict(fmin=4, fmax=12, wlen=2.0, wstep=3, decim=1)}

#-------------------------------------------
# Parallel processing
#-------------------------------------------
N_JOBS = 8
