from flask import render_template, Flask, request, send_file
from pytube import YouTube
import os
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = { 'username': 'nuhman' }
    video_qualities = [
        {
            'title': '720p',
            'value': '720p'
        },
        {
            'title': '480p',
            'value': '480p'
        },
        {
            'title': '360p',
            'value': '360p'
        },
        {
            'title': '240p',
            'value': '240p'
        },
        {
            'title': '144p',
            'value': '144p'
        },        
    ]
    return render_template('index.html', user=user, video_qualities=video_qualities)

@app.route('/download', methods=['POST'])
def download_video():    
    url = request.form['ytlinktext']
    selected_quality = request.form.get('quality')  # This will get the quality selected by the user.
    audioonly = request.form.get('audioonly')
    audioonlymp3 = request.form.get('audioonlymp3')
    yt = YouTube(url)
    
    is_mp3 = False
    if audioonly:        
        stream = yt.streams.filter(only_audio=True).order_by('abr').first()
        print(f"Downloading audio only")
    if audioonlymp3:        
        stream = yt.streams.filter(only_audio=True).order_by('abr').first()
        print(f"Downloading audio mp3 only")
        is_mp3 = True
    elif selected_quality:
        stream = yt.streams.filter(res=selected_quality).first()
        print(f"Downloading selected resolution: {stream.resolution}")
    else:
        stream = yt.streams.get_highest_resolution()
        print(f"Downloading highest resolution: {stream.resolution}")
    
    filename = stream.download()
    if is_mp3:
        # Ensure the proper file extension is set for audio files
        base, ext = os.path.splitext(filename)
        new_filename = base + '.mp3'
        os.rename(filename, new_filename)
        filename = new_filename

    print(f"Downloaded video: {filename}")
    return send_file(filename, as_attachment=True)
