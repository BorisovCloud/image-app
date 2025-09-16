import os
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.core.exceptions import AzureError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Flask configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

# Azure configuration
AZURE_STORAGE_ACCOUNT_NAME = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
AZURE_STORAGE_ACCOUNT_URL = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
AZURE_CONTAINER_NAME = os.getenv('AZURE_BLOB_CONTAINER', 'uploads')
AZURE_PUBLIC_CONTAINER = os.getenv('AZURE_PUBLIC_CONTAINER', 'false').lower() == 'true'

# Managed Identity configuration
AZURE_CLIENT_ID = os.getenv('AZURE_CLIENT_ID')  # User-assigned managed identity client ID
USE_MANAGED_IDENTITY = os.getenv('USE_MANAGED_IDENTITY', 'true').lower() == 'true'

# Fallback to connection string/keys for local development
AZURE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_KEY')

# Allowed image extensions and MIME types
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
MIME_TYPES = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}

def get_blob_service_client():
    """Initialize and return BlobServiceClient using Managed Identity or fallback credentials"""
    try:
        if USE_MANAGED_IDENTITY:
            # Use Managed Identity for authentication
            if AZURE_CLIENT_ID:
                # User-assigned managed identity
                credential = ManagedIdentityCredential(client_id=AZURE_CLIENT_ID)
                logger.info("Using user-assigned managed identity for authentication")
            else:
                # System-assigned managed identity or DefaultAzureCredential chain
                credential = DefaultAzureCredential()
                logger.info("Using DefaultAzureCredential for authentication")
            
            # Determine account URL
            if AZURE_STORAGE_ACCOUNT_NAME:
                account_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            else:
                raise ValueError("AZURE_STORAGE_ACCOUNT_URL or AZURE_STORAGE_ACCOUNT_NAME must be provided for managed identity")
            
            return BlobServiceClient(account_url=account_url, credential=credential)
        
        else:
            # Fallback to connection string or account key for local development
            if AZURE_CONNECTION_STRING:
                logger.info("Using connection string for authentication")
                return BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
            elif AZURE_STORAGE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY:
                account_url = f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
                logger.info("Using account key for authentication")
                return BlobServiceClient(account_url=account_url, credential=AZURE_ACCOUNT_KEY)
            else:
                raise ValueError("Azure Storage credentials not configured properly")
                
    except Exception as e:
        logger.error(f"Failed to initialize Azure Blob Service Client: {e}")
        raise

def ensure_container_exists():
    """Ensure the blob container exists, create if it doesn't"""
    try:
        blob_service_client = get_blob_service_client()
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
        
        if not container_client.exists():
            container_client.create_container()
            logger.info(f"Created container: {AZURE_CONTAINER_NAME}")
        
        return container_client
    except AzureError as e:
        logger.error(f"Azure error ensuring container exists: {e}")
        raise
    except Exception as e:
        logger.error(f"Error ensuring container exists: {e}")
        raise

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Get file extension in lowercase"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def get_content_type(filename):
    """Get content type based on file extension"""
    ext = get_file_extension(filename)
    return MIME_TYPES.get(ext, 'application/octet-stream')

def generate_unique_filename(original_filename):
    """Generate a unique filename with UUID prefix"""
    secure_name = secure_filename(original_filename).lower()
    unique_id = uuid4().hex
    return f"{unique_id}_{secure_name}"

def extract_account_key_from_connection_string(connection_string):
    """Extract account key from Azure Storage connection string"""
    try:
        parts = connection_string.split(';')
        for part in parts:
            if part.startswith('AccountKey='):
                return part.split('=', 1)[1]
        return None
    except Exception:
        return None

def blob_url(blob_name):
    """Generate URL for blob (public or SAS)"""
    try:
        blob_service_client = get_blob_service_client()
        blob_client = blob_service_client.get_blob_client(
            container=AZURE_CONTAINER_NAME, 
            blob=blob_name
        )
        
        if AZURE_PUBLIC_CONTAINER:
            return blob_client.url
        else:
            # For private containers, we need to generate SAS tokens
            if USE_MANAGED_IDENTITY:
                # When using managed identity, we need to use user delegation key for SAS
                try:
                    # Get user delegation key (valid for up to 7 days)
                    user_delegation_key = blob_service_client.get_user_delegation_key(
                        key_start_time=datetime.utcnow(),
                        key_expiry_time=datetime.utcnow() + timedelta(hours=1)
                    )
                    
                    # Generate SAS token using user delegation key
                    from azure.storage.blob import generate_blob_sas, UserDelegationKey
                    
                    sas_token = generate_blob_sas(
                        account_name=blob_client.account_name,
                        container_name=AZURE_CONTAINER_NAME,
                        blob_name=blob_name,
                        user_delegation_key=user_delegation_key,
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(hours=1),
                        protocol="https"
                    )
                    return f"{blob_client.url}?{sas_token}"
                    
                except Exception as e:
                    logger.error(f"Failed to generate SAS with user delegation key: {e}")
                    logger.info("Falling back to direct blob URL (may not work for private containers)")
                    return blob_client.url
            else:
                # Use account key method for SAS generation
                account_key = AZURE_ACCOUNT_KEY
                
                # If no explicit account key, try to extract from connection string
                if not account_key and AZURE_CONNECTION_STRING:
                    account_key = extract_account_key_from_connection_string(AZURE_CONNECTION_STRING)
                
                if account_key:
                    sas_token = generate_blob_sas(
                        account_name=blob_client.account_name,
                        container_name=AZURE_CONTAINER_NAME,
                        blob_name=blob_name,
                        account_key=account_key,
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(hours=1),
                        protocol="https"
                    )
                    return f"{blob_client.url}?{sas_token}"
                else:
                    logger.error(f"Cannot generate SAS token - no account key available")
                    return "#"
                    
    except Exception as e:
        logger.error(f"Error generating blob URL for {blob_name}: {e}")
        return "#"

def list_images():
    """List all image blobs in the container"""
    try:
        container_client = ensure_container_exists()
        images = []
        
        for blob in container_client.list_blobs():
            # Filter only image files
            blob_ext = get_file_extension(blob.name)
            if blob_ext in ALLOWED_EXTENSIONS:
                # Extract display name (remove UUID prefix)
                display_name = blob.name
                if '_' in blob.name:
                    display_name = '_'.join(blob.name.split('_')[1:])
                
                images.append({
                    'name': blob.name,
                    'display_name': display_name,
                    'url': blob_url(blob.name),
                    'last_modified': blob.last_modified.strftime('%Y-%m-%d %H:%M') if blob.last_modified else 'Unknown'
                })
        
        # Sort by last modified (newest first)
        images.sort(key=lambda x: x['last_modified'], reverse=True)
        return images
        
    except AzureError as e:
        logger.error(f"Azure error listing images: {e}")
        flash('Error loading images from Azure Storage', 'error')
        return []
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        flash('Error loading images', 'error')
        return []

@app.route('/')
def index():
    """Home page with upload form and image gallery"""
    images = list_images()
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload to Azure Blob Storage"""
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['image']
        
        # Check if file is selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Validate file extension
        if not allowed_file(file.filename):
            flash('Invalid file type. Only JPG, JPEG, and PNG files are allowed.', 'error')
            return redirect(url_for('index'))
        
        # Validate MIME type
        if file.mimetype not in ['image/jpeg', 'image/png']:
            flash('Invalid file format. Only JPEG and PNG images are allowed.', 'error')
            return redirect(url_for('index'))
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        content_type = get_content_type(file.filename)
        
        # Upload to Azure Blob Storage
        container_client = ensure_container_exists()
        blob_client = container_client.get_blob_client(unique_filename)
        
        # Reset file pointer and upload
        file.seek(0)
        blob_client.upload_blob(
            file.read(),
            content_type=content_type,
            overwrite=True
        )
        
        logger.info(f"Successfully uploaded {unique_filename} to Azure Blob Storage")
        flash(f'Image "{file.filename}" uploaded successfully!', 'success')
        
    except AzureError as e:
        logger.error(f"Azure error during upload: {e}")
        flash('Error uploading to Azure Storage. Please try again.', 'error')
    except Exception as e:
        logger.error(f"Error during upload: {e}")
        flash('Error uploading file. Please try again.', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File is too large. Maximum file size is 10 MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {e}")
    flash('An unexpected error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Validate configuration on startup
    try:
        if USE_MANAGED_IDENTITY:
            if not (AZURE_STORAGE_ACCOUNT_URL or AZURE_STORAGE_ACCOUNT_NAME):
                raise ValueError("AZURE_STORAGE_ACCOUNT_URL or AZURE_STORAGE_ACCOUNT_NAME must be provided for managed identity")
            logger.info("Using Managed Identity authentication")
        else:
            if not (AZURE_CONNECTION_STRING or (AZURE_STORAGE_ACCOUNT_NAME and AZURE_ACCOUNT_KEY)):
                raise ValueError("Azure Storage credentials not configured")
            logger.info("Using connection string/account key authentication")
        
        # Test Azure connection
        ensure_container_exists()
        logger.info(f"Successfully connected to Azure Storage, container: {AZURE_CONTAINER_NAME}")
        logger.info(f"Public container mode: {AZURE_PUBLIC_CONTAINER}")
        logger.info(f"Authentication method: {'Managed Identity' if USE_MANAGED_IDENTITY else 'Connection String/Account Key'}")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.error("Please check your Azure Storage configuration in .env file")
        exit(1)
    
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
