# Subtitle_Synchronization
 ## Summer Internship


\
\

### How to use this project: \
\
Download the folder and unzip it.\
$cd Subtitle_Synchronization \
$wget https://s3.amazonaws.com/audioanalysis/models.tar.gz \
$tar -xzf models.tar.gz \
$pip install -r requirements.txt \
$python synchro.py <audio_film.wav> <unsynchronized_subtitles.srt>  \
you can use test.wav and test45.wav to test it \
The program will print the number of seconds and will create a synchronized version of your subtitles called newSubs.srt
