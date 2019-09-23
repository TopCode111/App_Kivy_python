import numpy as np
import scipy
import scipy.signal
import librosa
from aread import aread
import os
from classifier import Classifier

from errors import FanNotDetectedError, OffsetError

from kivy.logger import Logger

class Analyse:
    def __init__(self, file, progressbar, product_id, soundType="wav"):
        self.file = file
        self.soundType = soundType
        self.progressbar = progressbar
        self.product_id = product_id

    def fanDetector(self):
        hop_length=512
        sr = 44100

        # if wav, load all channels and split
        if self.soundType == "wav":
            dataMulti, sr = librosa.load(self.file, mono=False, sr=44100)
            data1 = dataMulti[0]
            data2 = dataMulti[1]
            data3 = dataMulti[2]
            # data1 = aread(self.file, target_sr=44100, channel=1)
            # data2 = aread(self.file, target_sr=44100, channel=2)
            # data3 = aread(self.file, target_sr=44100, channel=3)

        # else if flac, locate other channels
        else:
            data1 = aread(self.file, target_sr=44100)
            data2 = aread(self.file[:-7]+'-2.flac',target_sr=44100)
            data3 = aread(self.file[:-7]+'-3.flac',target_sr=44100)

        data1 = data1[:min(data1.shape[0],data2.shape[0],data3.shape[0])]
        data2 = data2[:min(data1.shape[0],data2.shape[0],data3.shape[0])]
        data3 = data3[:min(data1.shape[0],data2.shape[0],data3.shape[0])]


        S1,n_fft = librosa.spectrum._spectrogram(data1,n_fft=2048,hop_length=hop_length)
        S2,n_fft = librosa.spectrum._spectrogram(data2,n_fft=2048,hop_length=hop_length)
        S3,n_fft = librosa.spectrum._spectrogram(data3,n_fft=2048,hop_length=hop_length)
        rmse1 = librosa.feature.rmse(S=S1)
        rmse2 = librosa.feature.rmse(S=S2)
        rmse3 = librosa.feature.rmse(S=S3)


        rmse_min1 = scipy.ndimage.filters.minimum_filter1d(rmse1[0],150)-scipy.ndimage.filters.minimum_filter1d(rmse1[0],750)
        rmse_min2 = scipy.ndimage.filters.minimum_filter1d(rmse2[0],150)-scipy.ndimage.filters.minimum_filter1d(rmse2[0],750)
        rmse_min3 = scipy.ndimage.filters.minimum_filter1d(rmse3[0],150)-scipy.ndimage.filters.minimum_filter1d(rmse3[0],750)


        tmp3 = rmse_min3 > 0.65
        tmp1 = rmse_min1 > 0.4
        tmp2 = rmse_min2 > 0.07
        mask = np.concatenate([np.zeros(800),np.ones(650),np.zeros(1880-650),np.ones(2480-1880),np.zeros(200)]).astype(bool)

        conv = np.array([np.sum(mask&tmp1[i:i+len(mask)]) for i in range(len(tmp1)-len(mask))])
        conv2 = np.array([np.sum(mask&tmp2[i:i+len(mask)]) for i in range(len(tmp2)-len(mask))])
        conv3 = np.array([np.sum(mask&tmp3[i:i+len(mask)]) for i in range(len(tmp3)-len(mask))])


        conv = np.fmax(conv3,np.fmax(conv,conv2)).astype(float)

        try:
            peaks = scipy.signal.find_peaks_cwt(conv,np.array([600]))
        except ValueError as err:
            raise FanNotDetectedError()

        return np.array(peaks)[conv[peaks] > 800]*hop_length/sr


    def make_tags(self):

        file = self.file
        tp = self.product_id
        # tp = os.path.split(os.path.split(os.path.split(file)[0])[0])[1]

        print("tp")
        print(tp)

        if tp.startswith('1:'):
            marks = {
                'A':(87.787331-150.082176871,92.394416-150.082176871),
                'B':(92.316659-150.082176871,97.400004-150.082176871),
                'C':(97.550658-150.082176871,102.264659-150.082176871),
                'D':(102.298677-150.082176871,107.309126-150.082176871),
                'E':(107.513237-150.082176871,120.275058-150.082176871),
                'F':(120.313936-150.082176871,133.459681-150.082176871),
                'G':(133.688091-150.082176871,137.634244-150.082176871),
                'H':(137.677982-150.082176871,141.852546-150.082176871),
                'I':(142.100396-150.082176871,147.120563-150.082176871),
                'J':(147.120563-150.082176871,152.437179-150.082176871),
                'K':(152.505216-150.082176871,156.495107-150.082176871),
                'L':(158.579959-150.082176871,167.619177-150.082176871),
                'M':(169.276367-150.082176871,173.203081-150.082176871),
                'N':(173.980648-150.082176871,177.887923-150.082176871),
                'O':(180.045672-150.082176871,188.909938-150.082176871),
                'P':(191.242639-150.082176871,195.324867-150.082176871),

            }
        elif tp.startswith('2:'):
            marks = {
                'A':(88.863993-150.511746032,101.708985-150.511746032),
                'B':(101.708985-150.511746032,114.806985-150.511746032),
                'C':(114.982144-150.511746032,119.691975-150.511746032),
                'D':(119.691975-150.511746032,124.674275-150.511746032),
                'E':(124.888358-150.511746032,129.481416-150.511746032),
                'F':(129.967968-150.511746032,134.483178-150.511746032),
                'G':(134.658337-150.511746032,138.511835-150.511746032),
                'H':(138.589683-150.511746032,142.579416-150.511746032),
                'I':(142.774037-150.511746032,147.717412-150.511746032),
                'J':(147.717412-150.511746032,153.011106-150.511746032),
                'K':(153.108417-150.511746032,156.884066-150.511746032),
                'L':(158.985974-150.511746032,168.172090-150.511746032),
                'M':(169.962604-150.511746032,173.816102-150.511746032),
                'N':(174.516737-150.511746032,178.467546-150.511746032),
                'O':(180.316446-150.511746032,189.385789-150.511746032),
                'P':(191.546083-150.511746032,195.360657-150.511746032),
            }
        elif tp.startswith('3:'):
            marks = {
                'A':(19.494108-163.549750567,25.107918-163.549750567),
                'B':(25.370101-163.549750567,29.750107-163.549750567),
                'C':(29.827219-163.549750567,34.500253-163.549750567),
                'D':(34.808704-163.549750567,39.528006-163.549750567),
                'E':(39.589696-163.549750567,44.725407-163.549750567),
                'F':(45.049280-163.549750567,57.788310-163.549750567),
                'G':(57.850000-163.549750567,71.036284-163.549750567),
                'H':(110.903586-163.549750567,123.765996-163.549750567),
                'I':(123.765996-163.549750567,136.474180-163.549750567),
                'J':(136.690096-163.549750567,141.440243-163.549750567),
                'K':(141.440243-163.549750567,146.097854-163.549750567),
                'L':(146.205812-163.549750567,150.369902-163.549750567),
                'M':(150.369902-163.549750567,154.595681-163.549750567),
                'N':(154.842442-163.549750567,159.808505-163.549750567),
                'O':(159.808505-163.549750567,165.175553-163.549750567),
                'P':(165.175553-163.549750567,169.308798-163.549750567),
                'Q':(171.375420-163.549750567,180.443882-163.549750567),
                'R':(182.664730-163.549750567,186.489523-163.549750567),
                'S':(187.630792-163.549750567,191.640656-163.549750567),
                'T':(193.645588-163.549750567,202.775740-163.549750567),
                'U':(205.706025-163.549750567,209.777580-163.549750567),
            }

        elif tp.startswith('4:'):
            marks = {
                'A':(18.497502-162.330702948,23.3894030-162.330702948),
                'B':(23.389403-162.330702948,28.342453-162.330702948),
                'C':(28.770495-162.330702948,41.061397-162.330702948),
                'D':(41.672885-162.330702948,54.147233-162.330702948),
                'E':(94.352547-162.330702948,99.244449-162.330702948),
                'F':(99.244449-162.330702948,104.503243-162.330702948),
                'G':(104.747838-162.330702948,117.772525-162.330702948),
                'H':(118.078269-162.330702948,130.185725-162.330702948),
                'I':(130.491469-162.330702948,135.077626-162.330702948),
                'J':(135.077626-162.330702948,139.770794-162.330702948),
                'K':(140.504579-162.330702948,145.304758-162.330702948),
                'L':(170.238167-162.330702948,179.013015-162.330702948),
                'M':(192.282298-162.330702948,201.240592-162.330702948),
            }
        else:
            marks = {}

        output = {}
        for offset in self.fanDetector():

            print(offset)

            if offset < 75:
                continue
            for tag,(start,end) in marks.items():
                output[tag] = [offset+start, offset+end]
                # print("%f\t%f\t%s\n" % (offset+start,offset+end,tag))

        if not output:
            raise OffsetError()

        return output

    def preprocess(self, ch1, ch2, ch3):
        y = ch1 + ch2 + ch3
        #return librosa.feature.melspectrogram(y,n_fft=1024, hop_length=256, n_mels=256)
        return y

    def analyse(self):

        self.progressbar.update(10)

        out = self.make_tags()

        self.progressbar.update(25)

        classifier = Classifier()
        classes = []

        self.progressbar.update(40)

        cnt = 1
        for region, (start,stop) in out.items():

            self.progressbar.update(40 + cnt*3)

            length = stop - start

            if self.soundType == "wav":
                dataMulti, sr = librosa.load(self.file, sr=22050, mono=False, offset=start, duration=length)
                data1 = dataMulti[0]
                data2 = dataMulti[1]
                data3 = dataMulti[2]
                # data1 = aread(self.file, target_sr=22050, start=start, length=length, channel=1)
                # data2 = aread(self.file, target_sr=22050, start=start, length=length, channel=2)
                # data3 = aread(self.file, target_sr=22050, start=start, length=length, channel=3)

            else:
                # TODO: not fully implemented/tested !
                data1 = aread(self.file, start=start, length=length, target_sr=22050)
                data2 = aread(self.file[:-7]+'-2.flac', start=start, length=length, target_sr=22050)
                data3 = aread(self.file[:-7]+'-3.flac', start=start, length=length,target_sr=22050)

            dta = self.preprocess(data1,data2,data3)
            predict = classifier.predict(dta)

            classes.append(np.percentile(predict[0],85))
            print(region, start, stop)

            cnt += 1

        print(classes)

        val = np.max(classes)
        if val < 0.5:
            print('ok', val)
            return('ok', val)
        else:
            print('nok', val)
            return('nok', val)
