# URL Scanner for Google Search Console Best Practices

A free, open-source web application that analyzes websites against Google Search Console best practices, providing comprehensive SEO audits and actionable recommendations.

## Features

- **Technical SEO Analysis**: Robots.txt, sitemap validation, crawlability checks
- **Core Web Vitals**: LCP, INP, CLS measurements and optimization tips
- **Mobile-Friendliness**: Responsive design validation and mobile UX analysis
- **Performance Metrics**: Page speed analysis and performance recommendations
- **Security Checks**: HTTPS validation, SSL certificate verification
- **Multi-tenant Architecture**: Support for agencies managing multiple clients
- **Caching System**: Fast repeated analyses with intelligent cache management

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: React.js
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Analysis Engines**: Custom Python modules for each analysis aspect

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/url-scanner-gsc.git
cd url-scanner-gsc
```

2. Set up Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

5. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

6. Initialize the database:
```bash
python create_test_client.py
```

7. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5001`

## Configuration

### Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here  # IMPORTANT: Change this to a random secret key!

# Database Configuration
DATABASE_URL=sqlite:///database/app.db

# API Keys (Optional - app works without these)
FIRECRAWL_API_KEY=your-firecrawl-api-key  # Optional
APIFY_API_KEY=your-apify-api-key  # Optional fallback
PAGESPEED_API_KEY=your-pagespeed-api-key  # Optional

# Server Configuration
HOST=0.0.0.0
PORT=5001
DEBUG=True
```

**Important**: Always set a strong `SECRET_KEY` for production deployments!

### API Keys (Optional)

For enhanced crawling capabilities, you can add:
- [Firecrawl API](https://firecrawl.dev) - Primary web crawler
- [Apify](https://apify.com) - Fallback crawler

The application works without these APIs but with limited crawling features.

## Usage

1. **Single URL Analysis**: Enter a URL in the dashboard to analyze
2. **Batch Analysis**: Upload multiple URLs for bulk processing
3. **View Results**: Get detailed reports with:
   - Compliance scores
   - Issue identification
   - Actionable recommendations
   - Priority rankings

## API Documentation

### Endpoints

- `POST /api/analysis/analyze` - Analyze a single URL
- `GET /api/analysis/results/{url}` - Get analysis results
- `GET /api/clients` - List all clients (multi-tenant)
- `POST /api/clients` - Create new client

### Example Request

```bash
curl -X POST http://localhost:5001/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Project Structure

```
url-scanner-gsc/
├── src/
│   ├── models/         # Database models
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   └── engines/        # Analysis engines
├── static/             # Frontend build
├── database/           # SQLite database
├── tests/              # Test suite
├── main.py             # Application entry point
└── requirements.txt    # Python dependencies
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `python -m pytest`
5. Submit a pull request

## Roadmap

- [ ] Google Search Console API integration
- [ ] Enhanced performance monitoring
- [ ] Competitor analysis features
- [ ] Scheduled monitoring
- [ ] Email alerts for issues
- [ ] Export to PDF reports
- [ ] WordPress/CMS plugins

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/url-scanner-gsc/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/url-scanner-gsc/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/url-scanner-gsc/wiki)

## Acknowledgments

- Google Search Console documentation
- Core Web Vitals guidelines
- Open source community

---

**Note**: This tool is not affiliated with Google. It implements publicly documented best practices for search engine optimization.