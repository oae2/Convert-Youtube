# backend_server.py - Fixed for Cloud Deployment (No Browser Cookies)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import tempfile
import threading
import time
import random
from urllib.parse import urlparse, parse_qs
import json

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

def get_random_api_key():
    """Get random YouTube API key for rotation"""
    api_keys = [
        'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',  # Key 1
        'AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w',  # Key 2  
        'AIzaSyB-63vPrdThhKuerbB2N_l7Kwwcxj6yUAc',  # Key 3
        'AIzaSyCjc_pVEDi4qsv5MoC0wINiZh2YAFQ7lUs',  # Key 4
        'AIzaSyDHQ9ipnphqTKC4FyttPrqyBFvWV_ZYLcg',  # Key 5
        'AIzaSyAcJstVgYWo-H0z7-B6H8vTG5Zr8BmEFfs',  # Key 6
        'AIzaSyBr8vIZJhVH5mRuURYGG_E5XQB3bZ2zEjc',  # Key 7
    ]
    return random.choice(api_keys)

def is_cloud_environment():
    """Detect if running on cloud platform"""
    cloud_indicators = [
        'RENDER',
        'HEROKU', 
        'VERCEL',
        'RAILWAY',
        'AWS',
        'GOOGLE_CLOUD'
    ]
    return any(indicator in os.environ.get(key, '') for key in os.environ for indicator in cloud_indicators) or \
           '/opt/render' in os.getcwd() or \
           '/app' in os.getcwd()

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

def get_optimized_ydl_opts():
    """Get optimized yt-dlp options for cloud deployment"""
    
    # Latest user agents from real browsers
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    ]
    
    is_cloud = is_cloud_environment()
    
    # Base options optimized for cloud
    opts = {
        # Enhanced headers to mimic real browser
        'http_headers': {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,th;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Connection': 'keep-alive',
        },
        
        # Enhanced extractor arguments with API rotation
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web', 'tv_embedded'],
                'player_skip': ['configs', 'webpage'],
                'skip': ['dash'],
                'innertube_host': ['youtubei.googleapis.com'],
                'innertube_key': [get_random_api_key()],  # Random API key rotation
                'player_params': ['CgIQBg%3D%3D'],  # Age restriction bypass
            }
        },
        
        # Network settings optimized for cloud
        'socket_timeout': 30 if is_cloud else 60,
        'retries': 5 if is_cloud else 12,
        'fragment_retries': 5 if is_cloud else 12,
        'retry_sleep_functions': {
            'http': lambda n: min(2 ** n, 15),
            'fragment': lambda n: min(2 ** n, 15),
        },
        
        # Shorter delays for cloud to avoid timeout
        'sleep_interval': random.uniform(0.5, 1.5) if is_cloud else random.uniform(2, 4),
        'max_sleep_interval': random.uniform(1.5, 3) if is_cloud else random.uniform(4, 8),
        'sleep_interval_requests': random.uniform(0.3, 1) if is_cloud else random.uniform(1, 3),
        
        # Enhanced bypass options
        'format_sort': ['res:720', 'ext:mp4', 'codec'],
        'prefer_free_formats': True,
        'no_check_certificate': True,
        'geo_bypass': True,
        'geo_bypass_country': random.choice(['US', 'CA', 'GB', 'AU']),
        
        # Output settings
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'writesubtitles': False,
        'writeinfojson': False,
    }
    
    # Only try cookies if NOT in cloud environment
    if not is_cloud:
        try:
            print("🍪 Local environment detected - attempting browser cookies...")
            browsers = [
                ('chrome', None, None, None),
                ('firefox', None, None, None), 
                ('edge', None, None, None),
            ]
            
            for browser_config in browsers:
                try:
                    opts['cookiesfrombrowser'] = browser_config
                    print(f"🍪 Successfully configured {browser_config[0]} cookies")
                    break
                except Exception as e:
                    print(f"⚠️ {browser_config[0]} cookies failed: {str(e)}")
                    continue
        except Exception as e:
            print(f"⚠️ Browser cookies error: {str(e)}")
    else:
        print("☁️ Cloud environment detected - skipping browser cookies")
    
    return opts

def try_fast_extractors(url):
    """Try different extraction methods optimized for cloud"""
    
    is_cloud = is_cloud_environment()
    
    extractors = [
        # Method 1: iOS client (highest success rate)
        {
            'name': 'iOS Fast',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'player_skip': ['configs', 'webpage'],
                        'innertube_key': [get_random_api_key()],
                        'player_params': ['CgIQBg%3D%3D'],
                    }
                }
            }
        },
        
        # Method 2: Android client
        {
            'name': 'Android Fast', 
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'innertube_key': [get_random_api_key()],
                        'player_params': ['CgIQBg%3D%3D'],
                    }
                }
            }
        },
        
        # Method 3: TV embedded (only if first two fail)
        {
            'name': 'TV Fast',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv_embedded'],
                        'player_skip': ['configs'],
                        'innertube_key': [get_random_api_key()],
                    }
                }
            }
        },
    ]
    
    # Limit attempts in cloud environment
    max_attempts = 2 if is_cloud else 3
    
    for i, extractor in enumerate(extractors[:max_attempts]):
        try:
            print(f"🔄 Trying {extractor['name']} ({i+1}/{max_attempts})...")
            
            # Combine base options with extractor-specific options
            ydl_opts = get_optimized_ydl_opts()
            
            # Merge extractor-specific options
            if 'extractor_args' in extractor['opts']:
                ydl_opts['extractor_args']['youtube'].update(extractor['opts']['extractor_args']['youtube'])
            
            # Shorter delay in cloud environment
            delay = random.uniform(1, 2) if is_cloud else random.uniform(2, 4)
            print(f"⏱️ Cloud-optimized delay: {delay:.1f}s...")
            time.sleep(delay)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    api_key_short = ydl_opts['extractor_args']['youtube']['innertube_key'][0][:20]
                    print(f"✅ Success with {extractor['name']} using API key: {api_key_short}...")
                    return info, extractor['name']
                    
        except Exception as e:
            print(f"❌ {extractor['name']} failed: {str(e)}")
            continue
    
    return None, None

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video information using cloud-optimized extraction"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
            
        print(f"🔍 Getting info for video: {video_id}")
        print(f"🔑 Using cloud-optimized extraction with API rotation")
        
        # Try fast extractors optimized for cloud
        info, method = try_fast_extractors(url)
        
        if info:
            return jsonify({
                'title': info.get('title', 'Unknown Title'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'video_id': video_id,
                'extraction_method': method,
                'available_formats': len(info.get('formats', [])),
                'cloud_optimized': True,
                'success': True
            })
        else:
            return jsonify({
                'error': 'Unable to extract video information',
                'suggestion': 'Video may be private, age-restricted, or heavily protected',
                'tried_methods': 'iOS Fast, Android Fast, TV Fast with API rotation',
                'success': False
            }), 400
            
    except Exception as e:
        print(f"❌ Cloud-optimized video info error: {str(e)}")
        return jsonify({'error': f'Cloud extraction failed: {str(e)}'}), 500

@app.route('/api/convert', methods=['POST'])
def convert_video():
    """Start video conversion using cloud-optimized methods"""
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
        
        print(f"🚀 Starting cloud-optimized conversion: {format_type.upper()} @ {quality.upper()}")
        print(f"📹 URL: {url}")
        print(f"🛡️ Using API rotation + fast extraction")
        
        # Start conversion in background thread
        thread = threading.Thread(
            target=perform_conversion_fast,
            args=(conversion_id, url, format_type, quality)
        )
        thread.start()
        
        return jsonify({
            'conversion_id': conversion_id,
            'status': 'started',
            'message': 'Cloud-optimized conversion started with API rotation',
            'features': ['api_rotation', 'fast_extraction', 'cloud_optimized']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_conversion_fast(conversion_id, url, format_type, quality):
    """Perform conversion with cloud-optimized methods"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        conversion_status[conversion_id].status = "Initializing cloud conversion..."
        
        # Quality selector with smart approach
        if quality == 'best':
            format_selector = 'best[height<=1080]/best[height<=720]/best'
        else:
            height = quality.replace('p', '')
            format_selector = f'best[height<={height}]/bestvideo[height<={height}]+bestaudio/best[height<=720]'
        
        print(f"🎯 Using cloud format selector: {format_selector}")
        
        # Filename template
        quality_suffix = f"_{quality}" if quality != 'best' else "_best"
        filename_template = f'%(title)s{quality_suffix}.%(ext)s'
        
        # Fast extraction methods for download
        is_cloud = is_cloud_environment()
        extractors = [
            {'name': 'iOS Cloud', 'client': ['ios']},
            {'name': 'Android Cloud', 'client': ['android']}, 
        ]
        
        # Limit to 2 attempts in cloud
        max_attempts = 2 if is_cloud else 3
        
        for i, extractor in enumerate(extractors[:max_attempts]):
            try:
                conversion_status[conversion_id].status = f"Trying {extractor['name']} extraction..."
                print(f"🔄 Download attempt {i+1}/{max_attempts} with {extractor['name']} client")
                
                # Build optimized yt-dlp options
                ydl_opts = get_optimized_ydl_opts()
                ydl_opts.update({
                    'format': format_selector,
                    'outtmpl': os.path.join(temp_dir, filename_template),
                    'progress_hooks': [lambda d: progress_hook({**d, 'conversion_id': conversion_id})],
                    'extractor_args': {
                        'youtube': {
                            'player_client': extractor['client'],
                            'innertube_key': [get_random_api_key()],  # Fresh API key
                            'player_params': ['CgIQBg%3D%3D'],
                        }
                    }
                })
                
                # Format-specific settings
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
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': format_type,
                    }]
                
                conversion_status[conversion_id].status = f"Downloading with {extractor['name']}..."
                
                # Cloud-optimized delay
                delay = random.uniform(1, 2) if is_cloud else random.uniform(3, 5)
                print(f"⏱️ Cloud delay: {delay:.1f}s for attempt {i+1}")
                time.sleep(delay)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Check if download succeeded
                all_files = os.listdir(temp_dir)
                video_files = [f for f in all_files if not f.endswith('.info.json')]
                
                if video_files:
                    print(f"✅ Cloud download success with {extractor['name']}")
                    break
                else:
                    print(f"❌ No files with {extractor['name']}")
                    continue
                    
            except Exception as e:
                print(f"❌ {extractor['name']} failed: {str(e)}")
                continue
        else:
            raise Exception("All cloud extraction methods failed")
        
        # Process downloaded files
        conversion_status[conversion_id].status = "Processing downloaded files..."
        
        all_files = os.listdir(temp_dir)
        video_files = [f for f in all_files if not f.endswith('.info.json')]
        
        if video_files:
            main_file = max(video_files, key=lambda f: os.path.getsize(os.path.join(temp_dir, f)))
            conversion_status[conversion_id].file_path = os.path.join(temp_dir, main_file)
            
            file_size_mb = os.path.getsize(conversion_status[conversion_id].file_path) / 1024 / 1024
            
            print(f"🎉 Cloud conversion complete: {main_file}")
            print(f"📊 Final file size: {file_size_mb:.1f}MB")
            
            conversion_status[conversion_id].status = f"Cloud conversion complete - {file_size_mb:.1f}MB"
            conversion_status[conversion_id].progress = 100
        else:
            raise Exception("No video file found after cloud conversion")
        
    except Exception as e:
        conversion_status[conversion_id].error = str(e)
        conversion_status[conversion_id].status = f"Cloud conversion error: {str(e)}"
        print(f"❌ Cloud conversion error: {str(e)}")

@app.route('/api/status/<conversion_id>', methods=['GET'])
def get_conversion_status(conversion_id):
    """Get conversion status"""
    if conversion_id not in conversion_status:
        return jsonify({'error': 'Conversion not found'}), 404
        
    status = conversion_status[conversion_id]
    
    file_size_mb = None
    if status.file_path and os.path.exists(status.file_path):
        file_size_mb = os.path.getsize(status.file_path) / 1024 / 1024
    
    return jsonify({
        'progress': status.progress,
        'status': status.status,
        'error': status.error,
        'completed': status.progress >= 100 and not status.error,
        'file_available': status.file_path is not None,
        'file_size_mb': round(file_size_mb, 1) if file_size_mb else None,
        'cloud_optimized': True
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
    return jsonify({
        'status': 'healthy', 
        'message': 'Cloud-Optimized YouTube Converter API',
        'environment': 'cloud' if is_cloud_environment() else 'local',
        'features': ['api_key_rotation', 'fast_extraction', 'cloud_optimized', 'no_browser_cookies']
    })

if __name__ == '__main__':
    print("🚀 Starting Cloud-Optimized YouTube Converter Backend...")
    print("📡 API available at: https://convert-youtube.onrender.com")
    print("☁️ Cloud environment optimizations enabled!")
    print("🔑 API key rotation system active!")
    print("📱 iOS/Android fast clients enabled!")
    print("⚡ Reduced delays for cloud deployment!")
    print("🚫 Browser cookies disabled for cloud!")
    print("🎯 Fast extraction methods prioritized!")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
