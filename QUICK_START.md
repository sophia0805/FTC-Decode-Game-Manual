# Quick Start Guide

## Local Development Setup

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Create `.env` file** in the `backend` directory:
   ```
   API_KEY=your_api_key_here
   ```

3. **Run the backend**:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

   The backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Create `.env.local` file** in the `frontend` directory:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Run the frontend**:
   ```bash
   npm run dev
   ```

   The frontend will be available at: `http://localhost:3000`

## Testing the Connection

1. Open your browser to `http://localhost:3000`
2. Type a message in the chat
3. You should see the response from your backend

## Deploying to Render

See `DEPLOYMENT.md` for detailed instructions on deploying the backend to Render.

After deploying to Render:

1. Get your Render backend URL (e.g., `https://ftc-rag-backend.onrender.com`)
2. Update your frontend `.env.local` or production environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://ftc-rag-backend.onrender.com
   ```

## Environment Variables Summary

### Backend (`.env` file in `backend/` directory)
- `API_KEY` - Your Hack Club AI API key

### Frontend (`.env.local` file in `frontend/` directory)
- `NEXT_PUBLIC_API_URL` - Backend API URL
  - Local: `http://localhost:8000`
  - Production: `https://your-app-name.onrender.com`

