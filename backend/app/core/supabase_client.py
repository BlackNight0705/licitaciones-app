from supabase import create_client
from backend.app.core.config import settings

supabase = create_client(settings.STORAGE_URL, settings.STORAGE_KEY)
