# YouTube to Doc MVP

A simplified MVP version of YouTube-to-Doc that converts YouTube videos into structured documentation by extracting transcripts.

## 🚀 Features

- **📺 YouTube Video Processing**: Extract video metadata and information
- **📝 Transcript Extraction**: Automatically extract video transcripts
- **🤖 AI-Friendly Output**: Generate structured markdown documentation
- **⚡ Fast Processing**: Efficient video processing
- **📱 Simple UI**: Clean, minimal interface

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.11+
- **Video Processing**: yt-dlp, pytube, youtube-transcript-api
- **Token Estimation**: tiktoken
- **Rate Limiting**: slowapi

## 📦 Installation

### Local Installation

```bash
# Clone the repository
git clone https://github.com/gitmvp-com/youtube-doc-mvp.git
cd youtube-doc-mvp

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🚀 Usage

1. Open your browser and navigate to `http://localhost:8000`
2. Enter a YouTube video URL
3. Click "Generate Documentation"
4. View the generated documentation

## 📋 Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home page with video processing form |
| `POST` | `/` | Process a YouTube video |
| `GET` | `/health` | Health check endpoint |

## 📝 Example Output

The generated documentation includes:

- **Video Metadata**: Title, duration, view count, channel info
- **Description**: Full video description
- **Transcript**: Complete video transcript
- **Token Estimation**: Estimated token count for LLM usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License

## 🙏 Acknowledgments

- Inspired by [YouTube-to-Doc](https://github.com/filiksyos/Youtube-to-Doc)
- Built with [FastAPI](https://fastapi.tiangolo.com/)

---

**Made for the AI and developer community**