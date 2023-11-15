from flask import render_template, Flask, request, send_file, Response, jsonify, stream_with_context
from pytube import YouTube
import os
from datetime import datetime, timedelta
from app import app

@app.route('/')
@app.route('/index')
def index():    
    video_qualities = [
        {
            'title': 'Low Quality',
            'value': 'Low Quality',
        },
        {
            'title': '144p',
            'value': '144p'
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
        {
            'title': 'High Quality',
            'value': 'High Quality'
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
        is_mp3 = True
        stream = yt.streams.filter(only_audio=True).order_by('abr').first()
        print(f"Downloading audio only")    
    elif selected_quality:
        if selected_quality == 'Low Quality':
            stream = yt.streams.get_lowest_resolution()
        elif selected_quality == 'High Quality':
            stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.filter(res=selected_quality).first()
        print(f"Downloading selected resolution: {stream.resolution}")
    else:
        stream = yt.streams.get_highest_resolution()
        print(f"Downloading highest resolution: {stream.resolution}")
    
    filename = stream.download()
    if is_mp3:
        # Ensure the proper file extension is set for audio files
        try:
            base, ext = os.path.splitext(filename)
            new_filename = base + '.mp3'
            os.rename(filename, new_filename)
            filename = new_filename
        except:
            pass

    print(f"Downloaded file: {filename}")
    return send_file(filename, as_attachment=True)

@app.route('/cleanup')
def cleanup_old_files():
    try:
        #file_directory = './'
        file_directory = os.getenv('FILE_DIRECTORY', './app/')
        print(f"file_directory where files are stored: {file_directory}")
        current_time = datetime.now()
        files_count = 0

        for filename in os.listdir(file_directory):
            if filename.endswith(('.mp4', '.mp3')):
                filepath = os.path.join(file_directory, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                # Delete files older than 1 hour (or any other threshold)                  
                print(f"filename: {filename}, filepath: {filepath}, file_time: {file_time}")
                print(f"time_diff more than 15 mins: {current_time - file_time > timedelta(seconds=10)}")
                if current_time - file_time > timedelta(seconds=10):
                    print(f"deleting file: {filepath}")
                    os.remove(filepath)      
                    files_count += 1

        return {
            'message': "cleanup success :)",
            'delete_count': files_count
        }
    except BaseException as error:
        print('An exception occurred: {}'.format(error))
        return {'message': "cleanup failed :( Check Logs"}
