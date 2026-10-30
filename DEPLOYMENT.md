# Deployment Guide for Fraud Detection Project

## ✅ Git Repository Setup - COMPLETED

The large dataset file has been successfully removed from Git history and the repository has been pushed to GitHub.

## ✅ Python Version Compatibility - FIXED

**Issue Resolved**: The initial deployment failed because scikit-learn 1.3.2 is incompatible with Python 3.13.4.

**Fix Applied**:
- Created `.python-version` file specifying Python 3.11.9
- Updated scikit-learn from 1.3.2 to 1.5.2 for better compatibility

The repository now includes the correct Python version configuration for Render.

### What was done:
1. ✅ Created `.gitignore` to exclude the `Data/` directory
2. ✅ Removed Git LFS configuration (not needed)
3. ✅ Cleaned Git history using `git filter-branch`
4. ✅ Force pushed to GitHub successfully
5. ✅ Repository is now ready for deployment

---

## 🚀 Deploy to Render

Follow these steps to deploy your fraud detection application on Render:

### Step 1: Create a New Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** button
3. Select **"Web Service"**

### Step 2: Connect Your Repository

1. Connect your GitHub account if not already connected
2. Find and select the repository: **`Jaouhar9/Fraud-detection`**
3. Click **"Connect"**

### Step 3: Configure the Web Service

Fill in the following settings:

| Setting | Value |
|---------|-------|
| **Name** | `fraud-detection` (or your preferred name) |
| **Region** | Choose closest to your location |
| **Branch** | `master` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | Leave empty (Render will auto-detect from Procfile) |
| **Instance Type** | `Free` (or choose paid for better performance) |

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Install dependencies from `requirements.txt`
   - Detect the `Procfile` and start the app with Gunicorn
   - Assign a public URL (e.g., `https://fraud-detection-xxxx.onrender.com`)

### Step 5: Wait for Deployment

- The deployment process takes 2-5 minutes
- You can monitor the build logs in real-time
- Once you see **"Your service is live 🎉"**, the app is ready!

### Step 6: Test Your Application

1. Click on the provided URL (e.g., `https://fraud-detection-xxxx.onrender.com`)
2. You should see the fraud detection form
3. Test with sample transaction data:

**Example Non-Fraudulent Transaction:**
- Amount: `1000`
- Old Balance Origin: `5000`
- New Balance Origin: `4000`
- Old Balance Destination: `0`
- New Balance Destination: `1000`
- Transaction Type: `PAYMENT`

**Example Fraudulent Transaction:**
- Amount: `500000`
- Old Balance Origin: `500000`
- New Balance Origin: `0`
- Old Balance Destination: `0`
- New Balance Destination: `0`
- Transaction Type: `TRANSFER`

---

## 📋 Project Configuration Summary

The following files have been configured for production deployment:

### `.python-version`
```
3.11.9
```
- Specifies Python 3.11.9 for Render (compatible with all dependencies)
- Prevents automatic use of Python 3.13 which has compatibility issues

### `requirements.txt`
- Updated **scikit-learn** to 1.5.2 (compatible with Python 3.11+)
- Added **Gunicorn** (production WSGI server)
- All ML dependencies included

### `Procfile`
```
web: gunicorn app:app
```
- Tells Render to use Gunicorn to serve the Flask app

### `app.py`
- Configured to read `PORT` from environment variables
- Set to bind to `0.0.0.0` (accepts external connections)
- Debug mode disabled for production

### `.gitignore`
- Excludes `Data/` directory (large dataset not needed for deployment)
- Excludes virtual environment and cache files

---

## 🔧 Troubleshooting

### If deployment fails:

1. **Check Build Logs**: Look for errors during `pip install`
2. **Verify Model Files**: Ensure `models/fraud_model.pkl` and `models/scaler.pkl` exist in the repository
3. **Check Python Version**: Render uses Python 3.7+ by default

### If the app doesn't load:

1. **Check Application Logs**: Click on "Logs" tab in Render dashboard
2. **Verify Model Loading**: Ensure the model files are accessible
3. **Check for Import Errors**: All dependencies should be in `requirements.txt`

### Common Issues:

- **"Module not found"**: Add missing package to `requirements.txt` and redeploy
- **"Model file not found"**: Verify model files are committed to Git
- **App crashes on startup**: Check logs for specific error messages

---

## 📝 Notes

- **Free Tier Limitation**: Render's free tier spins down after 15 minutes of inactivity. First request after inactivity may take 30-60 seconds.
- **Model Files**: The pre-trained model files (`fraud_model.pkl`, `scaler.pkl`) are included in the repository and will be deployed with the app.
- **Dataset**: The large training dataset is NOT included in deployment (not needed since model is already trained).

---

## ✨ Next Steps

Once deployed, you can:
- Share the Render URL with others to test the fraud detection system
- Monitor usage in the Render dashboard
- Upgrade to a paid plan for better performance and no spin-down
- Add custom domain if desired

**Your fraud detection app is now live! 🎉**
