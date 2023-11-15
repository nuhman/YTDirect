from flask import render_template, Flask, request, send_file, Response, jsonify, stream_with_context
from pytube import YouTube
import requests
import os
from app import app

@app.route('/')
@app.route('/index')
def index():    
    video_qualities = [
        {
            'title': 'Low Res',
            'value': 'Low Res',
        },
        {
            'title': '144p',
            'value': '144p'
        },  
        {
            'title': '240p',
            'value': '240p'
        }, 
        {
            'title': '360p',
            'value': '360p'
        },
        {
            'title': '480p',
            'value': '480p'
        },
        {
            'title': '720p',
            'value': '720p'
        },    
    ]
    return render_template('index.html', video_qualities=video_qualities)

@app.route('/download', methods=['POST'])
def download_video():    
    url = request.form['ytlinktext']
    selected_quality = request.form.get('quality')  # This will get the quality selected by the user.
    audioonly = request.form.get('audioonly')
    yt = YouTube(url)
    
    is_mp3 = False
    if audioonly:        
        stream = yt.streams.filter(only_audio=True).order_by('abr').first()
        print(f"Downloading audio only")    
    elif selected_quality:
        if selected_quality == 'Low Res':
            stream = yt.streams.get_lowest_resolution()
        else:
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

@app.route('/geturl', methods=['POST'])
def get_download_url():
    url = request.form['ytlinktext']
    yt = YouTube(url)
    stream = yt.streams.get_lowest_resolution()
    video_url = stream.url

    # Instead of downloading, send the direct video URL to the client    
    return {'download_url': video_url} 

@app.route('/proxy', methods=['POST'])
def proxy():
    url = request.form['ytlinktext']
    selected_quality = request.form.get('quality')
    audioonly = request.form.get('audioonly') == 'low'
    print("audiononlu", audioonly)
    yt = YouTube(url)

    if audioonly:        
        stream = yt.streams.filter(only_audio=True).order_by('abr').first()
        print(f"Downloading audio only")
    else:
        if selected_quality == 'Low Res':
            stream = yt.streams.get_lowest_resolution()
            print(f"Downloading lowest resolution: {stream.resolution}")
        else:
            stream = yt.streams.filter(res=selected_quality).first()
            print(f"Downloading selected resolution: {stream.resolution}")
    
    video_url = stream.url

    req = requests.get(video_url, stream=True)
    return Response(stream_with_context(req.iter_content(chunk_size=1024)), content_type=req.headers['Content-Type'])


