# Troubleshooting Vercel 500 Error

## What Was Fixed

1. **Improved Error Handling**: The handler now catches and displays detailed error messages
2. **Database Configuration**: Updated to support PostgreSQL (required for Vercel)
3. **Better Request Handling**: Improved compatibility with Vercel's Python runtime
4. **Error Messages**: Now shows helpful HTML error pages instead of crashing silently

## Common Causes of 500 Errors

### 1. Database Connection Error (Most Common)

**Problem**: SQLite doesn't work on Vercel's read-only filesystem.

**Solution**: Set up PostgreSQL database:

#### Option A: Vercel Postgres (Easiest)
1. Go to Vercel Dashboard → Your Project → Storage
2. Click "Create Database" → Select "Postgres"
3. Copy the connection details
4. Add these environment variables in Vercel:
   - `POSTGRES_DATABASE`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_HOST`
   - `POSTGRES_PORT` (usually 5432)

#### Option B: Supabase (Free tier available)
1. Sign up at https://supabase.com
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string details
5. Add the same environment variables as above

### 2. Missing Environment Variables

**Required Environment Variables:**
- `SECRET_KEY` - Generate a new one (don't use the default!)
- `DEBUG=False` - Set to False for production
- `ALLOWED_HOSTS=*.vercel.app,yourdomain.com` - Add your Vercel domain

**How to set:**
1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add each variable
3. Redeploy

### 3. Missing Dependencies

**Check**: All packages are in `requirements.txt`

The file should include:
- Django==5.2.8
- psycopg2-binary==2.9.9 (for PostgreSQL)
- Other dependencies

### 4. Path Issues

**Check**: The handler file is at `api/index.py` (not in a subdirectory)

## How to Debug

### Step 1: Check Vercel Function Logs
1. Go to Vercel Dashboard → Your Project
2. Click on "Functions" tab
3. Click on the function that's failing
4. View the logs - they'll show the actual error

### Step 2: Test the Handler
The error page should now show:
- The exact error message
- A stack trace
- Common issues and solutions

### Step 3: Test Database Connection
If you see database errors:
1. Verify PostgreSQL environment variables are set
2. Test connection locally with the same credentials
3. Ensure database allows connections from Vercel IPs

## Quick Fix Checklist

- [ ] PostgreSQL database is set up
- [ ] All PostgreSQL environment variables are set in Vercel
- [ ] `SECRET_KEY` is set (and is a new, secure key)
- [ ] `DEBUG=False` is set
- [ ] `ALLOWED_HOSTS` includes your Vercel domain
- [ ] `requirements.txt` includes `psycopg2-binary`
- [ ] Code is pushed to GitHub
- [ ] Vercel has redeployed after changes

## After Fixing Database

Once PostgreSQL is configured:

1. **Run Migrations:**
   ```bash
   vercel exec python manage.py migrate
   ```
   Or use Vercel CLI:
   ```bash
   vercel --prod
   vercel exec python manage.py migrate
   ```

2. **Create Superuser:**
   ```bash
   vercel exec python manage.py createsuperuser
   ```

## Still Having Issues?

1. **Check the error page**: The new handler shows detailed error messages
2. **Check Vercel logs**: Dashboard → Functions → View Logs
3. **Test locally**: Run `vercel dev` to test locally
4. **Verify environment variables**: Make sure all are set correctly

## Test Endpoint

I've created `api/test.py` as a simple test. You can temporarily change `vercel.json` to route to it:

```json
{
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/test.py"
    }
  ]
}
```

This will help verify that Vercel Python runtime is working.

