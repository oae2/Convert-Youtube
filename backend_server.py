# backend_server.py - Fixed with YouTube bot protection
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import threading
import time
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
CORS(app, origins=["https://oae2.github.io", "http://localhost:*"])

# Global dict to store conversion progress
conversion_status = {}

class ConversionProgress:
    def __init__(self):
        self.progress = 0
        self.status = "Initializing..."
        self.file_path = None
        self.error = None

def progress_hook(d):
    """Progress hook for yt-dlp"""
    conversion_id = d.get('conversion_id')
    if conversion_id and conversion_id in conversion_status:
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                conversion_status[conversion_id].progress = progress
                conversion_status[conversion_id].status = f"Downloading... {progress:.1f}%"
        elif d['status'] == 'finished':
            conversion_status[conversion_id].progress = 100
            conversion_status[conversion_id].status = "Download complete"
            conversion_status[conversion_id].file_path = d['filename']

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    parsed = urlparse(url)
    if parsed.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed.path == '/watch':
            return parse_qs(parsed.query)['v'][0]
        elif parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
    elif parsed.hostname in ['youtu.be']:
        return parsed.path[1:]
    return None

def get_format_selector(format_type, quality):
    """Get format selector for yt-dlp with proper quality filtering"""
    
    if quality == 'best':
        # Return best quality available
        if format_type == 'mp4':
            return 'best[ext=mp4]/best'
        elif format_type == 'webm':
            return 'best[ext=webm]/best'
        else:
            return 'best'
    
    # Extract height from quality string
    height = quality.replace('p', '')
    
    # More aggressive quality filtering
    if format_type == 'mp4':
        # Force specific height with strict filtering
        format_selector = f'best[height={height}][ext=mp4]/best[height<={height}][ext=mp4]/bestvideo[height={height}]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio'
    elif format_type == 'webm':
        format_selector = f'best[height={height}][ext=webm]/best[height<={height}][ext=webm]/bestvideo[height={height}]+bestaudio'
    else:
        # For other formats, be more specific about quality
        format_selector = f'bestvideo[height={height}]+bestaudio/bestvideo[height<={height}]+bestaudio/best[height<={height}]'
    
    print(f"📐 Quality filter: Looking for exactly {height}p or closest below")
    return format_selector

def get_ydl_opts_with_bypass():
    """Get yt-dlp options with bot protection bypass"""
    return {
        # User Agent to appear as a regular browser
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Keep-Alive': '300',
            'Connection': 'keep-alive',
        },
        # Additional options to bypass bot detection
        'extractor_args': {
            'youtube': {
                'skip': ['hls', 'dash'],  # Skip problematic formats
                'player_client': ['android', 'web'],  # Use mobile client
            }
        },
        # Sleep between requests to appear more human-like
        'sleep_interval': 1,
        'max_sleep_interval': 3,
        # Retry on errors
        'retries': 3,
        'fragment_retries': 3,
        # Don't check certificates to avoid some blocks
        'no_check_certificate': True,
        # Additional bypass options
        'geo_bypass': True,
        'geo_bypass_country': 'US',
        # Suppress warnings
        'quiet': True,
        'no_warnings': True,
    }

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video information without downloading"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
            
        # Use bypass options
        ydl_opts = get_ydl_opts_with_bypass()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            return jsonify({
                'title': info.get('title'),
                'duration': info.get('duration'),
                'thumbnail': info.get('thumbnail'),
                'uploader': info.get('uploader'),
                'view_count': info.get('view_count'),
                'video_id': video_id
            })
            
    except Exception as e:
        print(f"❌ Video info error: {str(e)}")
        return jsonify({'error': f'Failed to get video info: {str(e)}'}), 500

@app.route('/api/convert', methods=['POST'])
def convert_video():
    """Start video conversion"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'mp4')
        quality = data.get('quality', '1080p')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        # Generate conversion ID
        conversion_id = f"conv_{int(time.time())}"
        conversion_status[conversion_id] = ConversionProgress()
        
        print(f"🚀 Starting conversion: {format_type.upper()} @ {quality.upper()}")
        print(f"📹 URL: {url}")
        
        # Start conversion in background thread
        thread = threading.Thread(
            target=perform_conversion,
            args=(conversion_id, url, format_type, quality)
        )
        thread.start()
        
        return jsonify({
            'conversion_id': conversion_id,
            'status': 'started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_conversion(conversion_id, url, format_type, quality):
    """Perform the actual video conversion"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        conversion_status[conversion_id].status = "Initializing conversion..."
        
        # Get format selector
        format_selector = get_format_selector(format_type, quality)
        print(f"🎯 Using format selector: {format_selector}")
        
        # Add quality to filename for identification
        quality_suffix = f"_{quality}" if quality != 'best' else "_best"
        filename_template = f'%(title)s{quality_suffix}.%(ext)s'
        
        # Configure yt-dlp options with bypass
        ydl_opts = get_ydl_opts_with_bypass()
        ydl_opts.update({
            'format': format_selector,
            'outtmpl': os.path.join(temp_dir, filename_template),
            'progress_hooks': [lambda d: progress_hook({**d, 'conversion_id': conversion_id})],
        })
        
        # Add format-specific options
        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        elif format_type in ['mov', 'avi', 'mkv']:
            # For these formats, we need to convert after download
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': format_type,
            }]
        
        conversion_status[conversion_id].status = "Connecting to YouTube..."
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Start actual download
            conversion_status[conversion_id].status = "Downloading video..."
            ydl.download([url])
            
        conversion_status[conversion_id].status = "Processing completed files..."
        
        # Find all downloaded files and their info
        all_files = os.listdir(temp_dir)
        video_files = [f for f in all_files if not f.endswith('.info.json')]
        
        print(f"📁 Files in temp directory:")
        for file in all_files:
            file_path = os.path.join(temp_dir, file)
            size_mb = os.path.getsize(file_path) / 1024 / 1024
            print(f"  {file} - {size_mb:.1f}MB")
        
        if video_files:
            # Select the main video file (usually the largest non-info file)
            main_file = max(video_files, key=lambda f: os.path.getsize(os.path.join(temp_dir, f)))
            conversion_status[conversion_id].file_path = os.path.join(temp_dir, main_file)
            
            # Get file size for verification
            file_size_mb = os.path.getsize(conversion_status[conversion_id].file_path) / 1024 / 1024
            
            print(f"🎉 Conversion complete: {main_file}")
            print(f"📊 Final file size: {file_size_mb:.1f}MB")
            
            conversion_status[conversion_id].status = f"Conversion complete - {file_size_mb:.1f}MB"
        else:
            raise Exception("No video file found after conversion")
        
        conversion_status[conversion_id].progress = 100
        
    except Exception as e:
        conversion_status[conversion_id].error = str(e)
        conversion_status[conversion_id].status = f"Error: {str(e)}"
        print(f"❌ Conversion error: {str(e)}")

@app.route('/api/status/<conversion_id>', methods=['GET'])
def get_conversion_status(conversion_id):
    """Get conversion status"""
    if conversion_id not in conversion_status:
        return jsonify({'error': 'Conversion not found'}), 404
        
    status = conversion_status[conversion_id]
    
    # Get file size if file exists
    file_size_mb = None
    if status.file_path and os.path.exists(status.file_path):
        file_size_mb = os.path.getsize(status.file_path) / 1024 / 1024
    
    return jsonify({
        'progress': status.progress,
        'status': status.status,
        'error': status.error,
        'completed': status.progress >= 100 and not status.error,
        'file_available': status.file_path is not None,
        'file_size_mb': round(file_size_mb, 1) if file_size_mb else None
    })

@app.route('/api/download/<conversion_id>', methods=['GET'])
def download_file(conversion_id):
    """Download converted file"""
    if conversion_id not in conversion_status:
        return jsonify({'error': 'Conversion not found'}), 404
        
    status = conversion_status[conversion_id]
    if not status.file_path or not os.path.exists(status.file_path):
        return jsonify({'error': 'File not ready'}), 404
        
    return send_file(
        status.file_path,
        as_attachment=True,
        download_name=os.path.basename(status.file_path)
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'YouTube Converter API is running'})

if __name__ == '__main__':
    print("🚀 Starting YouTube Converter Backend...")
    print("📡 API will be available at: https://convert-youtube.onrender.com")
    print("🔧 yt-dlp with YouTube bot protection enabled!")
    print("⚡ Quality selection system is now active!")
    print("🛡️ Anti-bot measures activated!")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
