# 🎙️ Podcast Episode Downloader

A powerful Python script to download all episodes from any podcast RSS feed with resume capability, parallel downloads, and progress tracking.

## ✨ Features

- **📡 RSS Feed Support** - Works with any podcast RSS feed (Apple Podcasts, Spotify-hosted, Listen Notes, etc.)
- **⚡ Parallel Downloads** - Download multiple episodes simultaneously (configurable)
- **🔄 Resume Capability** - Interrupted downloads can be resumed; only new episodes are downloaded on subsequent runs
- **📊 Progress Bars** - Visual download progress with estimated time remaining
- **💾 Persistent Tracking** - Keeps a database of downloaded episodes to avoid re-downloading
- **🎯 Selective Download** - Limit downloads to first N episodes for testing
- **📁 Organized Storage** - Automatically names files by episode number and title
- **🛡️ Error Handling** - Gracefully handles network issues and server errors

---

## 📋 Prerequisites

- **Python 3.7 or higher** - [Download Python](https://www.python.org/downloads/)
- **Internet connection** - For downloading episodes
- **Sufficient disk space** - Podcast episodes are typically 20–100 MB each

---

## 🔧 Installation

### 1. Save the Script

Create a new file called `podcast_downloader.py` and paste the script code into it.

### 2. Install Required Packages

Open a terminal/command prompt and run:

```bash
# Required package
pip install requests

# Optional but recommended (adds progress bars)
pip install tqdm

# Optional (caches feed requests for faster repeated runs)
pip install requests-cache
```

### 3. Verify Installation

```bash
python podcast_downloader.py --help
```

You should see the help menu with all available options.

---


## 🔍 How to Find a Podcast RSS Feed Using Listen Notes

Many podcast platforms (especially Spotify) do not publicly display RSS feed URLs. Fortunately, Listen Notes makes it easy to find them.

### Step 1: Open Listen Notes

Visit:

```text
https://www.listennotes.com
```

### Step 2: Search for the Podcast

1. Enter the podcast name into the search bar.
2. Press **Enter** or click the search icon.

Examples:

- The Joe Rogan Experience
- Serial
- Stuff You Should Know

### Step 3: Select the Correct Podcast

1. Browse the search results.
2. Verify the podcast artwork and title.
3. Click the podcast name to open its dedicated page.

### Step 4: Locate the RSS Feed

On the podcast page, look for the **RSS icon (📶)**.

It is usually located:

- Near the top of the page next to Apple Podcasts and Spotify links
- Next to a **Subscribe** button
- In the sidebar on desktop layouts

### Step 5: Copy the RSS Feed URL

Click the RSS icon.

Depending on the podcast, your browser may:

- Open a page containing raw XML
- Display the RSS feed URL in a popup
- Download an XML file

Copy the URL from the browser address bar.

Common RSS feed formats include:

```text
https://feeds.simplecast.com/xxxxx
https://feeds.megaphone.fm/xxxxxxxx
https://anchor.fm/s/xxxxxxxx/podcast/rss
https://feeds.buzzsprout.com/xxxxxxxx.rss
https://podcastname.libsyn.com/rss
```

### Example

If you wanted to download a podcast called **Example Podcast**:

1. Search for it on Listen Notes.
2. Open the podcast page.
3. Click the RSS icon (📶).
4. Copy the RSS feed URL.
5. Use it with the downloader:

```bash
python podcast_downloader.py "RSS_FEED_URL"
```
## 🚀 Quick Start

Example:

```bash
python podcast_downloader.py "https://feeds.simplecast.com/xxxxx"
```

The script will:

1. Fetch the RSS feed
2. List all found episodes
3. Download missing episodes to a folder called `podcast_downloads`

---

## 📖 Command Line Options

| Option | Short | Description | Example |
|----------|--------|-------------|----------|
| `--dir` | `-d` | Download directory (default: `podcast_downloads`) | `-d "MyPodcast"` |
| `--workers` | `-w` | Number of parallel downloads (default: `3`) | `-w 5` |
| `--limit` | `-l` | Download only first N episodes | `-l 10` |
| `--force` | — | Redownload even if already downloaded | `--force` |

---

## 💡 Usage Examples

### Download to a Specific Folder

```bash
python podcast_downloader.py "RSS_URL" -d "MyFavoritePodcast"
```

### Faster Downloads with 5 Parallel Connections

```bash
python podcast_downloader.py "RSS_URL" -w 5
```

### Test with Only First 2 Episodes

```bash
python podcast_downloader.py "RSS_URL" -l 2
```

### Force Re-download All Episodes

```bash
python podcast_downloader.py "RSS_URL" --force
```

### Combine Multiple Options

```bash
python podcast_downloader.py "RSS_URL" -d "TechPodcast" -w 4 -l 50
```

---

## 🎯 How It Works

### First Run

- Parses the RSS feed to find all episode MP3 URLs
- Creates a download folder (default: `podcast_downloads`)
- Downloads all episodes (or up to `--limit`)
- Creates a database file (`.downloaded_episodes.txt`) tracking successful downloads

### Subsequent Runs

- Checks which episodes are already downloaded
- Only downloads new episodes (unless `--force` is used)
- Resumes any incomplete downloads

### File Organization

Files are named using episode numbers when available:

```text
001 - Episode Title.mp3
```

Without episode numbers:

```text
Episode Title (first 50 chars).mp3
```

Special characters in titles are automatically sanitized.

---

## 📁 Output Structure

After downloading, you'll have:

```text
podcast_downloads/
├── .downloaded_episodes.txt
├── 001 - Welcome to the Show.mp3
├── 002 - Interview with Expert.mp3
├── 003 - Deep Dive Topic.mp3
└── ...
```

### Tracking File

**`.downloaded_episodes.txt`** stores information about downloaded episodes.

⚠️ Do not delete this file if you want resume functionality to continue working.

---

## ⚠️ Important Notes

### Legal & Ethical Use

- Only download podcasts you have the right to download.
- Use for personal, offline listening only.
- Don't redistribute copyrighted content.
- Respect the podcast creator's work.

### Server Courtesy

- Don't use too many parallel workers (stick to 3–5).
- Excessive parallel downloads may get your IP blocked.
- Consider the podcast host's bandwidth.

### Storage Space

- A typical podcast episode: **20–100 MB**
- 100 episodes ≈ **2–10 GB**
- Ensure you have enough free space before downloading large catalogs.

---

## 🐛 Troubleshooting

### "No module named 'requests'"

```bash
pip install requests
```

### "Error Fetching RSS Feed"

- Verify the RSS URL is correct.
- Try opening the URL in a web browser to confirm it's accessible.
- Some podcasts may require a VPN if region-locked.

### Downloads Are Very Slow

- Reduce the number of parallel workers:

```bash
-w 2
```

- Check your internet connection.
- Try downloading at off-peak hours.

### "Connection reset by peer" Errors

- The podcast server may be rate-limiting you.
- Wait a few minutes and try again with fewer workers.
- The script will automatically retry interrupted downloads.

### Script Was Interrupted (`Ctrl+C`)

Simply run the same command again.

The script will:

- Resume partially downloaded files.
- Skip already downloaded episodes.
- Continue from where it left off.

### Episodes Not Downloading

- Check if the MP3 URLs are still valid.
- Some podcasts may expire older episodes.
- Try using:

```bash
--force
```

to re-attempt failed downloads.

---

## 🔄 Updating Your Podcast Collection

To get new episodes after the initial download, simply run:

```bash
python podcast_downloader.py "RSS_URL"
```

The script will:

- Skip all previously downloaded episodes.
- Download only episodes published since your last run.

### Automation

You can automate updates using:

- **cron jobs** (Linux/macOS)
- **Task Scheduler** (Windows)

to run the script weekly.

---

## 🧪 Testing Without Downloading Everything

To verify everything works without downloading an entire catalog:

```bash
python podcast_downloader.py "RSS_URL" -l 1
```

This downloads just the first episode as a test.

---

## 📞 Getting Help

If you encounter issues:

### Verify the RSS Feed

Open the RSS URL in a web browser.

You should see XML content.

### Test with a Known Working Feed

```bash
python podcast_downloader.py "https://feeds.megaphone.fm/ESP7315293072" -l 1
```

---

## 📄 License

This script is provided for personal use only.

Please respect podcast copyrights and applicable terms of service.

---

## 🙏 Acknowledgments

- Uses **requests** for HTTP downloads.
- Optional **tqdm** support for beautiful progress bars.
- Inspired by podcast enthusiasts everywhere.

---

# Happy Listening! 🎧
