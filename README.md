# Image Upload Flask App

A Flask web application that allows users to upload JPG/PNG images to Azure Blob Storage and displays all uploaded images in a responsive gallery.

## Features

- 🖼️ Upload JPG, JPEG, and PNG images (max 10MB)
- ☁️ Stores images in Azure Blob Storage
- 🖥️ Responsive image gallery with thumbnails
- 🔒 Secure file handling with validation
- 🎨 Clean, modern UI with CSS Grid
- ⚡ Flash messages for user feedback
- 🔑 Support for both public and private blob containers
- 🔐 SAS token generation for private containers

## Requirements

- Python 3.10+ (3.13+ preferred)
- Azure Storage Account
- Azure Blob Container

## Installation & Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd image-app
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and configure your Azure Storage settings:

```bash
cp .env.example .env
```

Edit `.env` with your Azure Storage details:

```env
# Primary configuration (recommended)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=your_account_name;AccountKey=your_account_key;EndpointSuffix=core.windows.net

# Alternative configuration
# AZURE_STORAGE_ACCOUNT=your_storage_account_name
# AZURE_STORAGE_KEY=your_storage_account_key

# Container settings
AZURE_BLOB_CONTAINER=uploads
AZURE_PUBLIC_CONTAINER=false

# Flask settings
FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_DEBUG=true
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Azure Storage Setup

### 1. Create Storage Account

1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new Storage Account
3. Note the account name and access key

### 2. Get Connection String

**Option A: Connection String (Recommended)**
1. Go to your Storage Account → Access Keys
2. Copy the connection string
3. Set `AZURE_STORAGE_CONNECTION_STRING` in `.env`

**Option B: Account Name + Key**
1. Set `AZURE_STORAGE_ACCOUNT` to your storage account name
2. Set `AZURE_STORAGE_KEY` to your access key

### 3. Container Configuration

**Public Container (easier setup):**
1. Create a container in your storage account
2. Set container access level to "Blob (anonymous read access for blobs only)"
3. Set `AZURE_PUBLIC_CONTAINER=true` in `.env`

**Private Container (more secure):**
1. Create a container with private access
2. Set `AZURE_PUBLIC_CONTAINER=false` in `.env`
3. App will generate SAS tokens for image access

## Project Structure

```
image-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
├── templates/
│   └── index.html        # Main page template
├── Dockerfile            # Docker configuration (optional)
└── README.md            # This file
```

## API Endpoints

- `GET /` - Home page with upload form and image gallery
- `POST /upload` - Handle image upload to Azure Blob Storage

## Security Features

- File extension validation (only .jpg, .jpeg, .png)
- MIME type validation (image/jpeg, image/png)
- File size limit (10MB)
- Secure filename generation with UUID
- No hardcoded secrets
- SAS tokens for private container access
- HTTPS-only SAS URLs

## Error Handling

- Invalid file types → 400 with flash message
- File too large → 400 with flash message  
- Azure connection errors → Flash message with retry suggestion
- General exceptions → Graceful error handling

## Development

### Local Development

```bash
# Install in development mode
pip install -e .

# Run with debug mode
export FLASK_DEBUG=true  # Linux/Mac
set FLASK_DEBUG=true     # Windows
python app.py
```

### Testing Azure Connection

The app will test Azure connectivity on startup and exit with an error if misconfigured.

## Docker Deployment (Optional)

```bash
# Build image
docker build -t image-upload-app .

# Run container
docker run -p 5000:5000 --env-file .env image-upload-app
```

## Production Deployment

### Environment Variables

Set these in your production environment:

```env
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_BLOB_CONTAINER=uploads
AZURE_PUBLIC_CONTAINER=false
FLASK_SECRET_KEY=<strong-random-secret>
FLASK_DEBUG=false
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

### Azure App Service Deployment

1. Create an Azure App Service (Python 3.10+)
2. Configure environment variables in App Service settings
3. Deploy code via Git, GitHub Actions, or ZIP deployment
4. Set startup command: `gunicorn --bind 0.0.0.0:8000 app:app`

## Troubleshooting

### Common Issues

**"Azure Storage credentials not configured"**
- Check your `.env` file exists and has correct values
- Verify connection string format
- Ensure no extra spaces in environment variables

**"Import flask could not be resolved"**
- Activate your virtual environment
- Install requirements: `pip install -r requirements.txt`

**Images not loading**
- Check container exists in Azure Storage
- Verify `AZURE_PUBLIC_CONTAINER` setting matches your container access level
- For private containers, ensure account key is correct for SAS generation

**File upload fails**
- Check file size (max 10MB)
- Verify file extension (.jpg, .jpeg, .png)
- Check Azure Storage account permissions

### Logs

Check application logs for detailed error information:

```bash
python app.py
# Look for startup messages and error details
```

## License

MIT License - see LICENSE file for details
