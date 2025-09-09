# Image Upload Flask Web Application

A Flask web application that allows users to upload JPG/PNG images to Azure Blob Storage and displays all uploaded images in a responsive gallery.

## 🎯 Features

- 🖼️ Upload JPG, JPEG, and PNG images (max 10MB)
- ☁️ Stores images in Azure Blob Storage
- 🖥️ Responsive image gallery with thumbnails
- 🔒 Secure file handling with validation
- 🎨 Clean, modern UI with CSS Grid
- ⚡ Flash messages for user feedback
- 🔑 Support for both public and private blob containers
- 🔐 SAS token generation for private containers

## 📋 Prerequisites

- Python 3.10+ (3.13+ preferred)
- Azure Storage Account (created via Terraform in `../terraform/`)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd webapp
pip install -r requirements.txt
```

### 2. Configure Environment

If you used Terraform to create Azure resources:
```bash
# From terraform directory
cd ../terraform
terraform output -raw env_file_content > ../webapp/.env
```

Or manually create `.env` from `.env.example`:
```bash
cp .env.example .env
# Edit .env with your Azure Storage details
```

### 3. Run Application

```bash
python app.py
```

Visit `http://localhost:5000`

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Azure Storage Configuration (choose one method)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

# OR use separate account/key
AZURE_STORAGE_ACCOUNT=your_storage_account_name
AZURE_STORAGE_KEY=your_storage_account_key

# Container settings
AZURE_BLOB_CONTAINER=uploads
AZURE_PUBLIC_CONTAINER=false

# Flask settings
FLASK_SECRET_KEY=your-super-secret-key-change-this-in-production
FLASK_DEBUG=true
```

### Container Access Types

**Private Container (AZURE_PUBLIC_CONTAINER=false):**
- More secure
- Requires SAS tokens for image access
- Recommended for production

**Public Container (AZURE_PUBLIC_CONTAINER=true):**
- Easier setup
- Direct blob URLs
- Good for development/testing

## 🐳 Docker Deployment

```bash
# Build image
docker build -t image-upload-app .

# Run container
docker run -p 5000:5000 --env-file .env image-upload-app
```

## 🔧 Development

### Local Development

```bash
# Install in development mode
pip install -e .

# Run with debug mode
export FLASK_DEBUG=true  # Linux/Mac
set FLASK_DEBUG=true     # Windows
python app.py
```

### File Structure

```
webapp/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── .env              # Your environment variables (create this)
├── templates/
│   └── index.html    # Main page template
├── Dockerfile        # Docker configuration
└── README.md        # This file
```

## 🛡️ Security Features

- File extension validation (only .jpg, .jpeg, .png)
- MIME type validation (image/jpeg, image/png)
- File size limit (10MB)
- Secure filename generation with UUID
- No hardcoded secrets
- SAS tokens for private container access
- HTTPS-only SAS URLs

## 📊 API Endpoints

- `GET /` - Home page with upload form and image gallery
- `POST /upload` - Handle image upload to Azure Blob Storage

## 🔍 Troubleshooting

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

## 🚀 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 app:app
```

### Azure App Service

1. Create an Azure App Service (Python 3.10+)
2. Configure environment variables in App Service settings
3. Deploy code via Git, GitHub Actions, or ZIP deployment
4. Set startup command: `gunicorn --bind 0.0.0.0:8000 app:app`

### Environment Variables for Production

```env
AZURE_STORAGE_CONNECTION_STRING=<your-connection-string>
AZURE_BLOB_CONTAINER=uploads
AZURE_PUBLIC_CONTAINER=false
FLASK_SECRET_KEY=<strong-random-secret>
FLASK_DEBUG=false
```

## 📈 Monitoring

The application includes comprehensive logging and error handling. For production monitoring, consider:

- Application Insights (created by Terraform)
- Azure Monitor
- Custom logging solutions

## 🔗 Related Documentation

- [Terraform Infrastructure](../terraform/README.md) - Azure resource provisioning
- [Main Project README](../README.md) - Overall project documentation
