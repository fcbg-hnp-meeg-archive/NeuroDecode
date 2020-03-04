########################################################################
class Basic:
    """
    Contains the basic parameters for the online modality for the neurofeedback protocol
    """
    params0 = dict()
    params0.update({'DATA_PATH': str})

    # PSD ratio: above
    params1 = dict()
    params1.update({'UP_CHANNELS': list})
    params1.update({'UP_FREQ': dict(min=float, max=float)})

    # PSD ratio: below
    params2 = dict()
    params2.update({'DOWN_CHANNELS': list})
    params2.update({'DOWN_FREQ': dict(min=float, max=float)})


########################################################################
class Advanced:
    """
    Contains the advanced parameters for the online modality for the neurofeedback protocol
    """
    params0 = dict()
    params0.update({'STREAMBUFFER': float})     # Buffer length
    params0.update({'WINDOWSIZE': float})       # Windows length in sec for PSD computation

    params1 = dict()
    params1.update({'UP_FEEDBACK_PATH':str})
    params1.update({'DOWN_FEEDBACK_PATH':str})
    params1.update({'SOUND_INC':float})

    params2 = dict()
    params2.update({'NJOBS': int})              # For multicore PSD compoutation