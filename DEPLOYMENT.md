# Deployment Guide: Backend on Render & Frontend Connection

This guide will walk you through deploying your backend to Render and connecting it to your frontend.

## Prerequisites

- A GitHub account (or GitLab/Bitbucket)
- A Render account (sign up at https://render.com)
- Your `API_KEY` for the Hack Club AI proxy service
- Git repository with your code

## Part 1: Prepare Your Code

### Backend Files (Already Created)

The following files have been created for you:

1. **`backend/app.py`** - FastAPI web server with `/chat` endpoint
2. **`backend/Procfile`** - Tells Render how to start your app
3. **`backend/runtime.txt`** - Specifies Python version
4. **`backend/render.yaml`** - Optional Render configuration
5. **`backend/requirements.txt`** - Updated with FastAPI dependencies

### Frontend Files

- **`frontend/app/page.tsx`** - Updated to call the backend API
- **`frontend/.env.example`** - Example environment variable file

## Part 2: Deploy Backend to Render

### Step 1: Push Your Code to GitHub

1. Initialize git (if not already done):
   ```bash
   cd /path/to/ftc-rag
   git init
   git add .
   git commit -m "Initial commit with backend API"
   ```

2. Create a repository on GitHub and push:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

### Step 2: Create a Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select your repository
4. Configure the service:
   - **Name**: `ftc-rag-backend` (or any name you prefer)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables

In the Render dashboard, go to your service → **Environment** tab and add:

- **Key**: `API_KEY`
- **Value**: Your Hack Club AI API key

Click **"Save Changes"**

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Wait for the build to complete (this may take 5-10 minutes on first build)
4. Once deployed, you'll see a URL like: `https://ftc-rag-backend.onrender.com`

### Step 5: Verify Backend is Working

1. Visit your backend URL: `https://your-app-name.onrender.com`
   - You should see: `{"message":"FTC RAG Backend API is running","status":"healthy"}`

2. Test the health endpoint: `https://your-app-name.onrender.com/health`

3. Test the chat endpoint (using curl or Postman):
   ```bash
   curl -X POST https://your-app-name.onrender.com/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the game about?"}'
   ```

## Part 3: Connect Frontend to Backend

### For Local Development

1. Create a `.env.local` file in the `frontend` directory:
   ```bash
   cd frontend
   cp .env.example .env.local
   ```

2. Update `.env.local` with your Render backend URL:
   ```
   NEXT_PUBLIC_API_URL=https://your-app-name.onrender.com
   ```

3. Start your frontend:
   ```bash
   npm run dev
   ```

### For Production Deployment (Vercel/Netlify/etc.)

#### Option A: Using Vercel (Recommended for Next.js)

1. Push your frontend code to GitHub
2. Go to https://vercel.com
3. Import your repository
4. Set the root directory to `frontend`
5. Add environment variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-app-name.onrender.com`
6. Deploy

#### Option B: Using Environment Variables in Frontend Hosting

When deploying your frontend anywhere, make sure to set:
- **NEXT_PUBLIC_API_URL**: Your Render backend URL (e.g., `https://ftc-rag-backend.onrender.com`)

## Part 4: Important Notes

### CORS Configuration

The backend has CORS enabled to allow requests from any origin. For production, you should restrict this:

In `backend/app.py`, update the CORS middleware:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Render Free Tier Limitations

- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Consider upgrading to paid tier for production

### File Size Considerations

- The `game_manual.pdf` file needs to be included in your repository
- Make sure it's not too large (Render has limits)
- If the PDF is large, consider using Git LFS or hosting it separately

### Building the Vector Index

On first startup, the backend will:
1. Download the sentence transformer model (~100MB)
2. Load and process the PDF
3. Create the vector index

This can take several minutes on the first deploy. The index is kept in memory, so after the first request, subsequent requests will be faster.

### Environment Variables

Backend needs:
- `API_KEY` - Your Hack Club AI API key

Frontend needs:
- `NEXT_PUBLIC_API_URL` - Your Render backend URL

## Troubleshooting

### Backend Won't Start

1. Check Render logs for errors
2. Verify `requirements.txt` includes all dependencies
3. Ensure `game_manual.pdf` is in the backend directory
4. Check that `API_KEY` environment variable is set

### Frontend Can't Connect to Backend

1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Check browser console for CORS errors
3. Verify backend URL is accessible (visit in browser)
4. Check that backend is not in "sleep" mode (first request may be slow)

### Slow Response Times

1. First request after deploy/spin-up will be slow (loading models)
2. Consider using Render's paid tier for always-on service
3. Check Render logs for timeout issues

## Testing Locally

Before deploying, test locally:

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn app:app --reload --port 8000
   ```

2. **Start Frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`

## Next Steps

- Set up continuous deployment (auto-deploy on git push)
- Configure custom domain for backend
- Add error monitoring (e.g., Sentry)
- Set up backend caching if needed
- Monitor Render dashboard for usage and performance

