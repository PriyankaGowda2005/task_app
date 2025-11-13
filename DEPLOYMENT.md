# Quick Deployment Guide to Vercel

## Files Created

✅ **vercel.json** - Vercel configuration
✅ **api/index.py** - Serverless function handler  
✅ **requirements.txt** - Python dependencies
✅ **.vercelignore** - Files to exclude
✅ **settings.py** - Updated for production

## Quick Start

### 1. Install Vercel CLI (Optional)

```bash
npm install -g vercel
```

### 2. Navigate to Project

```bash
cd task_proj
```

### 3. Deploy

```bash
vercel
```

Or deploy via Vercel Dashboard:

1. Go to https://vercel.com
2. Click "New Project"
3. Import your Git repository
4. Set **Root Directory** to `task_proj`
5. Deploy!

### 4. Set Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

```
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=*.vercel.app,yourdomain.com
```

**Generate SECRET_KEY:**

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## ⚠️ IMPORTANT: Database Setup

**SQLite will NOT work on Vercel!** You need a cloud database:

### Option 1: Vercel Postgres (Easiest)

1. Vercel Dashboard → Storage → Create Postgres Database
2. Add to `requirements.txt`: `psycopg2-binary`
3. Update `settings.py` DATABASES section (see below)

### Option 2: Supabase (Free tier)

1. Sign up at https://supabase.com
2. Create project and get connection string
3. Add to `requirements.txt`: `psycopg2-binary`
4. Update `settings.py` DATABASES section

### Database Settings Update

Replace the DATABASES section in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DATABASE', ''),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}
```

Then add database credentials as environment variables in Vercel.

## Post-Deployment

1. **Run Migrations:**

   ```bash
   vercel exec python manage.py migrate
   ```

2. **Create Superuser:**
   ```bash
   vercel exec python manage.py createsuperuser
   ```

## Troubleshooting

- **500 Errors**: Check function logs in Vercel dashboard
- **Database Errors**: Verify connection string and environment variables
- **Static Files**: Should be handled automatically, but check `STATIC_ROOT` setting

## Need Help?

See `README_VERCEL.md` for detailed instructions.
