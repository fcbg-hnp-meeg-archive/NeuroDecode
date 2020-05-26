########################################################################
class Basic:
    """
    Contains the basic parameters for the online modality for the neurofeedback protocol
    """
    params0 = dict()
    params0.update({'DATA_PATH': str})

    params1 = dict()
    params1.update({'GLOBAL_TIME': int})
    
    params2 = dict()
    params2.update({'START_VOICE_FILE': str})
    params2.update({'END_VOICE_FILE': str})

########################################################################
class Advanced:
    """
    Contains the advanced parameters for the online modality for the neurofeedback protocol
    """
    params0 = dict()
    params0.update({'TRIGGER_DEVICE': (None, 'ARDUINO','USB2LPT','SOFTWARE','DESKTOP')})
    params0.update({'TRIGGER_FILE': str})          # full list: PYCNBI_ROOT/Triggers/triggerdef_*.py
    
    params1 = dict()
    params1.update({'SCREEN_SIZE': ((1920, 1080), (1920, 1200), (1600, 1200), (1680, 1050), (1280, 1024), (1024, 768))})
    params1.update({'SCREEN_POS': ((0, 0), (1920, 0))})
