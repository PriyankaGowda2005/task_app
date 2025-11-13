# Deploying Django to Vercel

This guide will help you deploy your Django task management application to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Git repository (GitHub, GitLab, or Bitbucket)
3. Vercel CLI (optional, for local deployment)

## Important Notes

⚠️ **Database Considerations:**

- SQLite (the default database) is **NOT recommended** for production on Vercel
- Vercel's serverless functions have a read-only filesystem, so SQLite won't work properly
- You'll need to use a cloud database like:
  - **PostgreSQL**: Vercel Postgres, Supabase, or Neon
  - **MySQL**: PlanetScale or other cloud MySQL providers

## Deployment Steps

### Method 1: Deploy via Vercel Dashboard (Recommended)

1. **Push your code to Git:**

   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel:**

   - Go to https://vercel.com
   - Click "New Project"
   - Import your Git repository
   - Vercel will auto-detect the configuration

3. **Configure Project Settings:**

   - **Root Directory**: Set to `task_proj` (if your project is in a subdirectory)
   - **Framework Preset**: Python
   - **Build Command**: Leave empty or use `python manage.py collectstatic --noinput`
   - **Output Directory**: Leave empty

4. **Set Environment Variables:**
   In Vercel dashboard → Settings → Environment Variables, add:

   ```
   SECRET_KEY=your-secret-key-here (generate a new one!)
   DEBUG=False
   ALLOWED_HOSTS=your-app.vercel.app,yourdomain.com
   ```

   **Generate a new SECRET_KEY:**

   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Deploy:**
   - Click "Deploy"
   - Wait for the build to complete

### Method 2: Deploy via Vercel CLI

1. **Install Vercel CLI:**

   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**

   ```bash
   vercel login
   ```

3. **Navigate to project directory:**

   ```bash
   cd task_proj
   ```

4. **Deploy:**

   ```bash
   vercel
   ```

5. **Set Environment Variables:**

   ```bash
   vercel env add SECRET_KEY
   vercel env add DEBUG
   vercel env add ALLOWED_HOSTS
   ```

6. **Deploy to production:**
   ```bash
   vercel --prod
   ```

## Database Setup

Since SQLite won't work on Vercel, you need to set up a cloud database:

### Option 1: Vercel Postgres (Recommended)

1. In Vercel dashboard, go to Storage → Create Database → Postgres
2. Copy the connection string
3. Update `settings.py` to use PostgreSQL:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': os.environ.get('POSTGRES_DATABASE'),
           'USER': os.environ.get('POSTGRES_USER'),
           'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
           'HOST': os.environ.get('POSTGRES_HOST'),
           'PORT': os.environ.get('POSTGRES_PORT', '5432'),
       }
   }
   ```
4. Add `psycopg2-binary` to `requirements.txt`
5. Run migrations after deployment

### Option 2: Supabase (Free tier available)

1. Create account at https://supabase.com
2. Create a new project
3. Get connection string from Settings → Database
4. Update `settings.py` similar to above
5. Add connection details as environment variables

## Post-Deployment Steps

1. **Run Migrations:**
   You'll need to run migrations after deployment. You can do this via:

   - Vercel CLI: `vercel exec python manage.py migrate`
   - Or create a one-time migration script

2. **Create Superuser:**

   ```bash
   vercel exec python manage.py createsuperuser
   ```

3. **Collect Static Files:**
   Static files should be collected during build, but you can verify in Vercel dashboard.

## Troubleshooting

- **500 Errors**: Check Vercel function logs in the dashboard
- **Database Errors**: Ensure database connection string is correct
- **Static Files Not Loading**: Verify `STATIC_ROOT` is set and files are collected
- **CSRF Errors**: Ensure `ALLOWED_HOSTS` includes your Vercel domain

## Files Created for Vercel

- `vercel.json`: Vercel configuration
- `vercel_handler.py`: Serverless function handler
- `requirements.txt`: Python dependencies
- `.vercelignore`: Files to exclude from deployment
- `settings.py`: Updated for production environment variables

## Support

For more information, visit:

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
