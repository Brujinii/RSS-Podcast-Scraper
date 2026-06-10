#!/usr/bin/env python3
"""
Podcast Episode Downloader
Downloads all episodes from an RSS feed with resume capability and parallel downloads
"""

import os
import sys
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from pathlib import Path
import hashlib

# Optional: for progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Tip: Install 'tqdm' for progress bars: pip install tqdm")

# Optional: for faster downloads
try:
    import requests_cache
    REQUESTS_CACHE_AVAILABLE = True
except ImportError:
    REQUESTS_CACHE_AVAILABLE = False


class PodcastDownloader:
    def __init__(self, rss_url, download_dir="downloads", max_workers=3):
        self.rss_url = rss_url
        self.download_dir = Path(download_dir)
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; PodcastDownloader/1.0)'
        })
        
        # Create download directory if it doesn't exist
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # File to track downloaded episodes
        self.downloaded_db = self.download_dir / ".downloaded_episodes.txt"
        self.downloaded_episodes = self.load_downloaded_db()
        
    def load_downloaded_db(self):
        """Load list of already downloaded episodes"""
        if self.downloaded_db.exists():
            with open(self.downloaded_db, 'r') as f:
                return set(line.strip() for line in f)
        return set()
    
    def save_to_db(self, episode_url):
        """Mark episode as downloaded"""
        self.downloaded_episodes.add(episode_url)
        with open(self.downloaded_db, 'a') as f:
            f.write(f"{episode_url}\n")
    
    def get_podcast_episodes(self):
        """Parse RSS feed and extract episode information"""
        print(f"Fetching RSS feed: {self.rss_url}")
        
        try:
            response = self.session.get(self.rss_url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching RSS feed: {e}")
            return []
        
        # Parse XML
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"Error parsing RSS XML: {e}")
            return []
        
        # RSS feeds can use different namespaces
        namespaces = {
            'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'content': 'http://purl.org/rss/1.0/modules/content/',
            'podcast': 'https://podcastindex.org/namespace/1.0'
        }
        
        episodes = []
        
        # Find all item elements (episodes)
        for item in root.findall('.//item'):
            title = item.find('title')
            title_text = title.text if title is not None else "Unknown Title"
            
            # Clean title for filename (remove invalid characters)
            safe_title = "".join(c for c in title_text if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # Get enclosure (audio file URL)
            enclosure = item.find('enclosure')
            if enclosure is None:
                continue
                
            audio_url = enclosure.get('url')
            if not audio_url:
                continue
            
            # Get additional metadata
            pub_date = item.find('pubDate')
            pub_date_text = pub_date.text if pub_date is not None else ""
            
            # Get episode number if available
            episode_num = item.find('itunes:episode', namespaces)
            episode_num_text = episode_num.text if episode_num is not None else ""
            
            # Determine file extension (should be .mp3 but just in case)
            parsed_url = urlparse(audio_url)
            path = parsed_url.path
            ext = os.path.splitext(path)[1]
            if not ext or ext.lower() not in ['.mp3', '.m4a', '.mp4', '.mov']:
                ext = '.mp3'  # Default to mp3
            
            # Build filename
            if episode_num_text:
                filename = f"{episode_num_text.zfill(3)} - {safe_title}{ext}"
            else:
                # Use first 50 chars of title as filename
                short_title = safe_title[:50]
                filename = f"{short_title}{ext}"
            
            # Remove any problematic characters
            filename = filename.replace('/', '_').replace('\\', '_')
            
            episodes.append({
                'title': title_text,
                'url': audio_url,
                'filename': filename,
                'pub_date': pub_date_text,
                'episode_num': episode_num_text
            })
        
        print(f"Found {len(episodes)} episodes")
        return episodes
    
    def download_file(self, episode):
        """Download a single episode"""
        url = episode['url']
        filename = episode['filename']
        filepath = self.download_dir / filename
        
        # Check if already downloaded
        if url in self.downloaded_episodes:
            return {'status': 'skipped', 'title': episode['title'], 'reason': 'already downloaded'}
        
        # Check if file exists (resume capability)
        resume_byte_pos = 0
        if filepath.exists():
            resume_byte_pos = filepath.stat().st_size
            if resume_byte_pos > 0:
                print(f"Resuming: {filename} ({resume_byte_pos} bytes already downloaded)")
        
        # Set up headers for resume
        headers = {}
        if resume_byte_pos > 0:
            headers['Range'] = f'bytes={resume_byte_pos}-'
        
        try:
            # Download with streaming
            response = self.session.get(url, stream=True, headers=headers, timeout=60)
            response.raise_for_status()
            
            # Get total file size
            total_size = int(response.headers.get('content-length', 0))
            if resume_byte_pos > 0 and 'content-range' in response.headers:
                # Parse content-range to get total size
                content_range = response.headers['content-range']
                total_size = int(content_range.split('/')[-1])
            
            # Open file in append mode if resuming, else write mode
            mode = 'ab' if resume_byte_pos > 0 else 'wb'
            
            # Download with or without progress bar
            if TQDM_AVAILABLE and total_size > 0:
                with open(filepath, mode) as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, 
                             desc=filename[:50], initial=resume_byte_pos) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            else:
                with open(filepath, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                if not TQDM_AVAILABLE:
                    print(f"Downloaded: {filename}")
            
            # Mark as downloaded in database
            self.save_to_db(url)
            
            return {'status': 'success', 'title': episode['title'], 'file': filename}
            
        except requests.RequestException as e:
            return {'status': 'failed', 'title': episode['title'], 'error': str(e)}
        except Exception as e:
            return {'status': 'failed', 'title': episode['title'], 'error': f"Unexpected error: {e}"}
    
    def download_all(self, limit=None, skip_downloaded=True):
        """Download all episodes with parallel execution"""
        episodes = self.get_podcast_episodes()
        
        if not episodes:
            print("No episodes found. Check your RSS feed URL.")
            return
        
        # Filter out already downloaded if skip_downloaded is True
        if skip_downloaded:
            new_episodes = [ep for ep in episodes if ep['url'] not in self.downloaded_episodes]
            print(f"Episodes to download: {len(new_episodes)} (already have {len(episodes) - len(new_episodes)})")
        else:
            new_episodes = episodes
            print(f"Total episodes to download: {len(new_episodes)}")
        
        # Apply limit
        if limit:
            new_episodes = new_episodes[:limit]
            print(f"Limited to first {limit} episodes")
        
        if not new_episodes:
            print("No new episodes to download!")
            return
        
        print(f"\nDownloading {len(new_episodes)} episodes using {self.max_workers} workers...")
        print("-" * 60)
        
        # Download in parallel
        results = {'success': 0, 'failed': 0, 'skipped': 0}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_episode = {executor.submit(self.download_file, ep): ep for ep in new_episodes}
            
            for future in as_completed(future_to_episode):
                episode = future_to_episode[future]
                try:
                    result = future.result()
                    if result['status'] == 'success':
                        results['success'] += 1
                        print(f"✓ {result['title']}")
                    elif result['status'] == 'skipped':
                        results['skipped'] += 1
                        print(f"⤷ Skipped: {result['title']} ({result['reason']})")
                    else:
                        results['failed'] += 1
                        print(f"✗ Failed: {result['title']} - {result.get('error', 'Unknown error')}")
                except Exception as e:
                    results['failed'] += 1
                    print(f"✗ Error downloading {episode['title']}: {e}")
        
        # Print summary
        print("-" * 60)
        print(f"\nDownload Summary:")
        print(f"  ✓ Success: {results['success']}")
        print(f"  ✗ Failed: {results['failed']}")
        print(f"  ⤷ Skipped: {results['skipped']}")
        print(f"\nFiles saved to: {self.download_dir.absolute()}")


def main():
    parser = argparse.ArgumentParser(description='Download all episodes from a podcast RSS feed')
    parser.add_argument('rss_url', help='RSS feed URL of the podcast')
    parser.add_argument('-d', '--dir', default='podcast_downloads', 
                       help='Download directory (default: podcast_downloads)')
    parser.add_argument('-w', '--workers', type=int, default=3,
                       help='Number of parallel downloads (default: 3)')
    parser.add_argument('-l', '--limit', type=int, default=None,
                       help='Limit number of episodes to download (for testing)')
    parser.add_argument('--force', action='store_true',
                       help='Force download even if already downloaded')
    
    args = parser.parse_args()
    
    # Validate RSS URL
    if not args.rss_url.startswith(('http://', 'https://')):
        print("Error: RSS URL must start with http:// or https://")
        sys.exit(1)
    
    # Create downloader instance
    downloader = PodcastDownloader(
        rss_url=args.rss_url,
        download_dir=args.dir,
        max_workers=args.workers
    )
    
    # Start download
    try:
        downloader.download_all(limit=args.limit, skip_downloaded=not args.force)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user. Progress has been saved.")
        print("Run the script again to resume where you left off.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
