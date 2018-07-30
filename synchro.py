import argparse
import numpy as np
from scipy.io import wavfile
import pysrt
import librosa
from pydub import AudioSegment
import glob


parser = argparse.ArgumentParser(description='Read file and process audio')
parser.add_argument('wav_file', type=str, help='Audio File to read and process')
parser.add_argument('srt', type=str, help='Subtitles File to read and process')

args = parser.parse_args()

from sklearn.externals import joblib
model = joblib.load('model_random_forest.pkl') 

Liste_trailers=[args.wav_file]

def proc_file(wav_file):
    sr, data = wavfile.read(wav_file)
    if data.dtype != np.int16:
        raise TypeError('Bad sample type: %r' % data.dtype)

    # local import to reduce start-up time
    from audio.processor import WavProcessor, format_predictions

    with WavProcessor() as proc:
        predictions = proc.get_predictions(sr, data)
    #print(predictions)    
    #return(predictions)
    #print(format_predictions(predictions))
    return(predictions)

inst=0
trailer=[]
instant=[]
dico={'Trailer':trailer, 'Instant':instant}
for i in range(128):
  dico[i]=[]

for cpt in range(len(Liste_trailers)):
  file=Liste_trailers[cpt]
  i=0
  #print("trailer numéro         ", cpt+1)
  samples, sample_rate = librosa.load(file)
  test=False
  
  max_sec=len(samples)//sample_rate
  newAudio = AudioSegment.from_wav(file)
  #while  i<(len(samples)//sample_rate):
  while  i<max_sec:
      dico['Trailer'].append(file)
      dico['Instant'].append(i)

      t1 = i * 1000 #Works in milliseconds
      t2 = (i+1) * 1000
      newAudio = newAudio[t1:t2]
      newAudio.export('newSong.wav', format="wav") #Exports to a wav file in the current path
      L=proc_file('newSong.wav')
      L=L[0,:]
      for f in range(len(L)):
        dico[f].append(L[f])
      #print(i)
      i+=1
      inst+=1
      newAudio = AudioSegment.from_wav(file)

import pandas as pd
df = pd.DataFrame(data=dico)   
df=df.drop(['Instant'],axis=1)
df=df.drop(['Trailer'],axis=1)

X=df

pred=model.predict(X)


max_L=0
nbr_trailers=1
for i in range(nbr_trailers):
  samples, sample_rate = librosa.load(Liste_trailers[i])
  max_L=max_L+len(samples)//sample_rate

L=[0 for i in range (max_L)]
Instant=[]
Trailer=[]
samples, sample_rate = librosa.load(Liste_trailers[0])
temps_precedent=-(len(samples)//sample_rate)
max_temps=len(samples)//sample_rate
#print(temps_precedent)

for k in range(nbr_trailers):
  #print("trailer numero          ",k)
  file=args.srt
  subs=pysrt.open(file)
  i=0
  temps=subs[i].start.seconds+subs[i].start.minutes*60+subs[i].start.hours*60*60
  temps_end=subs[i].end.seconds+subs[i].end.minutes*60+subs[i].end.hours*60*60
  temps_precedent=temps_precedent+max_temps
  samples, sample_rate = librosa.load(Liste_trailers[k])
  max_temps=len(samples)//sample_rate
  #print('max temps', max_temps)
  
  for t in range(max_temps):
    Trailer.append(file)
    Instant.append(t)
  #print('Instant et Trailer fait')
  while temps<max_temps:
    #print(temps)
    for j in range(temps,min(max_temps,temps_end)):
      #print('temps precedent', temps_precedent)
      #print('            ',j+temps_precedent)
      L[j+temps_precedent]=1
    if i<len(subs)-1:
      i+=1
      temps=subs[i].start.seconds+subs[i].start.minutes*60+subs[i].start.hours*60*60
      temps_end=subs[i].end.seconds+subs[i].end.minutes*60+subs[i].end.hours*60*60
    else:
      break
def apply_delta(delta,L2):
  if delta<0:
    L2 = L2[-delta:]+[0 for i in range(-delta)]
  elif delta>0:
    L2 = [0 for i in range(delta)]+L2[:-delta]
  return L2

def hamming(L1,L2):
  a = 0
  for i in range(len(L1)):
    if L1[i]!=L2[i]:
      a+=1
  return a

def minimize (L1,L2):
  min=hamming(L1,L2)
  a=0
  for delta in range(1,len(L1)):
    L=apply_delta(delta,L2)
    if hamming(L1,L)<min:
      min=hamming(L1,L)
      a=delta
    L=apply_delta(-delta,L2)
    if hamming(L1,L)<min:
      min=hamming(L1,L)
      a=-delta
  return(a)

print('Il faut décaler le soutitre de ', minimize(pred,L),' secondes')
subs.shift(seconds=minimize(pred,L))

#save new subs
subs.save('./newSubs.srt', encoding='utf-8')



