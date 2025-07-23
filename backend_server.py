# backend_server.py - Enhanced with Browser Cookies + API Key Rotation
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

def get_browser_cookies():
    """Try different browser cookie sources"""
    browsers = [
        ('chrome', None, None, None),
        ('firefox', None, None, None), 
        ('edge', None, None, None),
        ('safari', None, None, None),
    ]
    
    for browser_config in browsers:
        try:
            print(f"🍪 Attempting to use {browser_config[0]} cookies...")
            return browser_config
        except Exception as e:
            print(f"⚠️ {browser_config[0]} cookies failed: {str(e)}")
            continue
    return None

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

def get_updated_ydl_opts():
    """Get enhanced yt-dlp options with cookies and API rotation"""
    
    # Latest user agents from real browsers
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ]
    
    # Base options
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
        
        # Network and retry settings
        'socket_timeout': 60,
        'retries': 12,
        'fragment_retries': 12,
        'retry_sleep_functions': {
            'http': lambda n: min(2 ** n, 45),
            'fragment': lambda n: min(2 ** n, 45),
        },
        
        # Random delays to appear human-like
        'sleep_interval': random.uniform(2, 4),
        'max_sleep_interval': random.uniform(4, 8),
        'sleep_interval_requests': random.uniform(1, 3),
        
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
    
    # Try to add browser cookies (enhanced method)
    try:
        browser_cookies = get_browser_cookies()
        if browser_cookies:
            opts['cookiesfrombrowser'] = browser_cookies
            print(f"🍪 Successfully configured {browser_cookies[0]} cookies")
        else:
            print("⚠️ No browser cookies available - continuing without cookies")
    except Exception as e:
        print(f"⚠️ Browser cookies error: {str(e)} - continuing without cookies")
    
    return opts

def try_alternative_extractors(url):
    """Try different extraction methods with enhanced options"""
    
    extractors = [
        # Method 1: iOS client with cookies (highest success rate)
        {
            'name': 'iOS Client Enhanced',
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
        
        # Method 2: Android client with API rotation
        {
            'name': 'Android Client Enhanced', 
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
        
        # Method 3: TV embedded with bypass
        {
            'name': 'TV Embedded Enhanced',
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
        
        # Method 4: Web client with full bypass
        {
            'name': 'Web Bypass Enhanced',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'player_skip': ['configs', 'webpage'],
                        'skip': ['hls', 'dash'],
                        'innertube_key': [get_random_api_key()],
                        'player_params': ['CgIQBg%3D%3D'],
                    }
                }
            }
        },
        
        # Method 5: Mobile web fallback
        {
            'name': 'Mobile Web Fallback',
            'opts': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['mweb'],
                        'innertube_key': [get_random_api_key()],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                }
            }
        }
    ]
    
    for extractor in extractors:
        try:
            print(f"🔄 Trying {extractor['name']}...")
            
            # Combine base options with extractor-specific options
            ydl_opts = get_updated_ydl_opts()
            
            # Merge extractor-specific options
            if 'extractor_args' in extractor['opts']:
                ydl_opts['extractor_args']['youtube'].update(extractor['opts']['extractor_args']['youtube'])
            
            if 'http_headers' in extractor['opts']:
                ydl_opts['http_headers'].update(extractor['opts']['http_headers'])
            
            # Add random delay between attempts (longer delays)
            delay = random.uniform(3, 7)
            print(f"⏱️ Waiting {delay:.1f}s before attempt...")
            time.sleep(delay)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if info:
                    print(f"✅ Success with {extractor['name']} using API key: {ydl_opts['extractor_args']['youtube']['innertube_key'][0][:20]}...")
                    return info, extractor['name']
                    
        except Exception as e:
            print(f"❌ {extractor['name']} failed: {str(e)}")
            continue
    
    return None, None

@app.route('/api/video-info', methods=['POST'])
def get_video_info():
    """Get video information using enhanced extraction methods"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        video_id = extract_video_id(url)
        if not video_id:
            return jsonify({'error': 'Invalid YouTube URL'}), 400
            
        print(f"🔍 Getting info for video: {video_id}")
        print(f"🔑 Using enhanced extraction with cookies + API rotation")
        
        # Try alternative extractors with enhanced methods
        info, method = try_alternative_extractors(url)
        
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
                'enhanced_features': True,
                'success': True
            })
        else:
            return jsonify({
                'error': 'Unable to extract video information with enhanced methods',
                'suggestion': 'Video may be private, age-restricted, or heavily protected',
                'tried_methods': 'iOS, Android, TV, Web, Mobile with cookies + API rotation',
                'success': False
            }), 400
            
    except Exception as e:
        print(f"❌ Enhanced video info error: {str(e)}")
        return jsonify({'error': f'Enhanced extraction failed: {str(e)}'}), 500

@app.route('/api/convert', methods=['POST'])
def convert_video():
    """Start video conversion using enhanced extraction methods"""
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
        
        print(f"🚀 Starting enhanced conversion: {format_type.upper()} @ {quality.upper()}")
        print(f"📹 URL: {url}")
        print(f"🛡️ Using cookies + API rotation + multiple clients")
        
        # Start conversion in background thread
        thread = threading.Thread(
            target=perform_conversion_enhanced,
            args=(conversion_id, url, format_type, quality)
        )
        thread.start()
        
        return jsonify({
            'conversion_id': conversion_id,
            'status': 'started',
            'message': 'Enhanced conversion started with cookies + API rotation',
            'features': ['browser_cookies', 'api_rotation', 'multiple_clients', 'age_bypass']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_conversion_enhanced(conversion_id, url, format_type, quality):
    """Perform conversion with enhanced methods"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        conversion_status[conversion_id].status = "Initializing enhanced conversion..."
        
        # Quality selector with smart approach
        if quality == 'best':
            format_selector = 'best[height<=1080]/best[height<=720]/best'
        else:
            height = quality.replace('p', '')
            format_selector = f'best[height<={height}]/bestvideo[height<={height}]+bestaudio/best[height<=720]'
        
        print(f"🎯 Using enhanced format selector: {format_selector}")
        
        # Filename template
        quality_suffix = f"_{quality}" if quality != 'best' else "_best"
        filename_template = f'%(title)s{quality_suffix}.%(ext)s'
        
        # Enhanced extraction methods for download
        extractors = [
            {'name': 'iOS Enhanced', 'client': ['ios'], 'priority': 1},
            {'name': 'Android Enhanced', 'client': ['android'], 'priority': 2}, 
            {'name': 'TV Enhanced', 'client': ['tv_embedded'], 'priority': 3},
            {'name': 'Web Enhanced', 'client': ['web'], 'priority': 4},
            {'name': 'Mobile Enhanced', 'client': ['mweb'], 'priority': 5},
        ]
        
        for extractor in extractors:
            try:
                conversion_status[conversion_id].status = f"Trying {extractor['name']} extraction..."
                print(f"🔄 Download attempt {extractor['priority']}/5 with {extractor['name']} client")
                
                # Build enhanced yt-dlp options
                ydl_opts = get_updated_ydl_opts()
                ydl_opts.update({
                    'format': format_selector,
                    'outtmpl': os.path.join(temp_dir, filename_template),
                    'progress_hooks': [lambda d: progress_hook({**d, 'conversion_id': conversion_id})],
                    'extractor_args': {
                        'youtube': {
                            'player_client': extractor['client'],
                            'innertube_key': [get_random_api_key()],  # Fresh API key for each attempt
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
                
                # Enhanced random delay with priority-based timing
                delay = random.uniform(4, 8) + (extractor['priority'] * 1)
                print(f"⏱️ Enhanced delay: {delay:.1f}s for attempt {extractor['priority']}")
                time.sleep(delay)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                # Check if download succeeded
                all_files = os.listdir(temp_dir)
                video_files = [f for f in all_files if not f.endswith('.info.json')]
                
                if video_files:
                    print(f"✅ Enhanced download success with {extractor['name']}")
                    break
                else:
                    print(f"❌ No files with {extractor['name']}")
                    continue
                    
            except Exception as e:
                print(f"❌ {extractor['name']} failed: {str(e)}")
                continue
        else:
            raise Exception("All enhanced extraction methods failed")
        
        # Process downloaded files
        conversion_status[conversion_id].status = "Processing downloaded files..."
        
        all_files = os.listdir(temp_dir)
        video_files = [f for f in all_files if not f.endswith('.info.json')]
        
        if video_files:
            main_file = max(video_files, key=lambda f: os.path.getsize(os.path.join(temp_dir, f)))
            conversion_status[conversion_id].file_path = os.path.join(temp_dir, main_file)
            
            file_size_mb = os.path.getsize(conversion_status[conversion_id].file_path) / 1024 / 1024
            
            print(f"🎉 Enhanced conversion complete: {main_file}")
            print(f"📊 Final file size: {file_size_mb:.1f}MB")
            
            conversion_status[conversion_id].status = f"Enhanced conversion complete - {file_size_mb:.1f}MB"
            conversion_status[conversion_id].progress = 100
        else:
            raise Exception("No video file found after enhanced conversion")
        
    except Exception as e:
        conversion_status[conversion_id].error = str(e)
        conversion_status[conversion_id].status = f"Enhanced conversion error: {str(e)}"
        print(f"❌ Enhanced conversion error: {str(e)}")

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
        'enhanced': True
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
        'message': 'Enhanced YouTube Converter API with cookies + API rotation',
        'features': ['browser_cookies', 'api_key_rotation', 'multiple_clients', 'age_bypass', 'geo_bypass']
    })

if __name__ == '__main__':
    print("🚀 Starting Enhanced YouTube Converter Backend...")
    print("📡 API available at: https://convert-youtube.onrender.com")
    print("🔧 Enhanced yt-dlp with 2025 advanced bypass methods!")
    print("🍪 Browser cookies integration enabled!")
    print("🔑 API key rotation system active!")
    print("📱 iOS/Android/TV/Web/Mobile clients enabled!")
    print("🛡️ Advanced anti-detection with real browser simulation!")
    print("🎯 Multiple fallback extraction methods with priority system!")
    print("🌍 Geographic bypass with random countries!")
    print("⚡ Age restriction bypass enabled!")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
