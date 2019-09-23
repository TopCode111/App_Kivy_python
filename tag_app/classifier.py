import numpy as np
import scipy.signal
import librosa


class Classifier:
    def __init__(self):
        self._taps = scipy.signal.firwin2(386,[0,3100,3200,4000,4100,11025],[0,0,1,1,0,0],window='hann',nyq=11025)
        self._taps2 = scipy.signal.firwin2(386,[0,8000,8500,10500,11025],[0,0,1,1,0],window='hann',nyq=11025)


    def predict(self,data):
        filtered_data = scipy.signal.fftconvolve(data,self._taps)
        rmse = librosa.feature.rmse(filtered_data,n_fft=256,hop_length=64)[0]
        rmse_med =4*scipy.signal.medfilt(rmse,19)
        spikes = (rmse-rmse_med)/rmse_med

        spikes[spikes < 0] = 0

        spikes2 = np.minimum(np.minimum(spikes,5),np.maximum(np.exp(-0.2*(spikes-15)),0))

        nok_indicator_pre = scipy.signal.fftconvolve(spikes2,scipy.signal.general_gaussian(1500,2,350)/np.sum(scipy.signal.general_gaussian(1500,2,350)**2)**0.5,'same')
        nok_indicator = 2/(1+np.exp(-nok_indicator_pre))-1


        filtered_data2 = scipy.signal.fftconvolve(data,self._taps2)
        rmse = librosa.feature.rmse(filtered_data2,n_fft=256,hop_length=64)[0]
        rmse_med =4*scipy.signal.medfilt(rmse,19)
        spikes = (rmse-rmse_med)/rmse_med

        spikes[spikes < 0] = 0


        error_indicator_pre = 5*scipy.signal.fftconvolve(spikes,scipy.signal.general_gaussian(6000,2,2500)/np.sum(scipy.signal.general_gaussian(1500,2,350)**2)**0.5,'same')
        error_indicator = 2/(1+np.exp(-error_indicator_pre))-1


        nok_indicator = nok_indicator*(1.-error_indicator)

        return np.array([nok_indicator,1.-nok_indicator-error_indicator,error_indicator])
