# Azure Deployment Guide for Link2Hire

## Current Deployment Status

### ✅ Backend (Azure App Service)
- **URL**: https://link2hire-api.azurewebsites.net
- **Runtime**: Python (FastAPI)
- **Region**: Southeast Asia
- **Status**: Deployed

### 🚧 Frontend (Azure Static Web Apps)
- **GitHub Repo**: https://github.com/abdullahfirdowsi/link2hire
- **Branch**: main
- **Status**: Configured, waiting for deployment

---

## Step 1: Configure Backend CORS

Your backend needs to allow requests from the Azure Static Web App.

### Update Backend Environment Variables

In your **Azure App Service** configuration:

1. Go to **Azure Portal** → **App Services** → **link2hire-api**
2. Navigate to **Configuration** → **Application settings**
3. Add/Update the following variable:

```
API_CORS_ORIGINS=https://your-static-web-app.azurestaticapps.net,http://localhost:4200
```

**Replace** `your-static-web-app.azurestaticapps.net` with your actual Static Web App URL.

### Get Your Static Web App URL

1. Go to **Azure Portal** → **Static Web Apps** → your app
2. Copy the **URL** (e.g., `https://nice-beach-123456789.4.azurestaticapps.net`)
3. Add it to the `API_CORS_ORIGINS` in App Service configuration

---

## Step 2: Configure GitHub Secrets

The GitHub Actions workflow needs a deployment token.

### Get Azure Static Web Apps API Token

1. Go to **Azure Portal** → **Static Web Apps** → your app
2. Navigate to **Manage deployment token**
3. Copy the **API token**

### Add Secret to GitHub

1. Go to **GitHub** → your repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AZURE_STATIC_WEB_APPS_API_TOKEN`
5. Value: Paste the token from Azure
6. Click **Add secret**

---

## Step 3: Verify File Configuration

### ✅ Files Already Configured

1. **frontend/src/environments/environment.prod.ts**
   ```typescript
   export const environment = {
     production: true,
     apiUrl: 'https://link2hire-api.azurewebsites.net'
   };
   ```

2. **.github/workflows/azure-static-web-apps.yml**
   - GitHub Actions workflow for automatic deployment

3. **frontend/staticwebapp.config.json**
   - API proxy configuration (optional)
   - Routes `/api/*` to backend

### Output Path Correction

Your Angular build outputs to `dist/link2hire-frontend` (not `dist/frontend`).

The workflow file has been configured correctly with:
```yaml
output_location: "dist/link2hire-frontend"
```

---

## Step 4: Deploy Frontend

### Option 1: Trigger GitHub Actions (Recommended)

Make a small change and push to trigger deployment:

```powershell
# Navigate to project root
cd C:\Projects\Personal\link2hire-v1

# Make sure you're on main branch
git checkout main
git pull origin main

# Make a small change to trigger deployment
echo "# Azure Deployment" >> AZURE_DEPLOYMENT.md

# Commit and push
git add .
git commit -m "chore: trigger Azure Static Web Apps deployment"
git push origin main
```

### Option 2: Manual Build and Deploy

If you prefer manual deployment:

```powershell
cd frontend
npm install
npm run build -- --configuration production

# The build output will be in: frontend/dist/link2hire-frontend
```

Then upload via Azure Portal.

---

## Step 5: Verify Deployment

### Check GitHub Actions

1. Go to your GitHub repository
2. Click on **Actions** tab
3. You should see the workflow running
4. Wait for it to complete (usually 2-5 minutes)

### Check Azure Static Web App

1. Go to **Azure Portal** → **Static Web Apps**
2. Your app should show **Status: Ready**
3. Click on the **URL** to open your app

### Test Backend Connection

1. Open your Static Web App URL
2. Open browser DevTools (F12) → Network tab
3. Try to perform a job processing action
4. Verify API calls to `https://link2hire-api.azurewebsites.net` succeed

---

## Step 6: Configure API Proxy (Optional)

If you want to use `/api/*` instead of hardcoding the backend URL:

### Update Frontend Service

Edit `frontend/src/app/services/job.service.ts`:

```typescript
// Change from:
private apiUrl = this.environment.apiUrl;

// To:
private apiUrl = '/api';  // Will be proxied to backend
```

### Update Backend CORS

Add the Static Web App URL to `API_CORS_ORIGINS` as shown in Step 1.

---

## Troubleshooting

### CORS Errors

**Symptom**: Browser console shows CORS policy errors

**Solution**:
1. Verify `API_CORS_ORIGINS` in Azure App Service includes your Static Web App URL
2. Restart the App Service after changing configuration
3. Clear browser cache

### GitHub Actions Fails

**Symptom**: Workflow fails with authentication error

**Solution**:
1. Verify `AZURE_STATIC_WEB_APPS_API_TOKEN` secret is set correctly
2. Check the token hasn't expired (regenerate if needed)
3. Ensure workflow file has correct permissions

### Build Fails

**Symptom**: Angular build fails in GitHub Actions

**Solution**:
1. Test build locally: `cd frontend && npm run build -- --configuration production`
2. Fix any build errors
3. Commit and push fixes

### App Shows 404

**Symptom**: Static Web App loads but shows 404 on routes

**Solution**:
- `staticwebapp.config.json` is configured with `navigationFallback`
- Ensure this file is in the `frontend/` directory
- Rebuild and redeploy

---

## Quick Commands Reference

```powershell
# Test frontend build locally
cd frontend
npm install
npm run build -- --configuration production

# Check build output
ls dist/link2hire-frontend

# Trigger deployment
git add .
git commit -m "chore: update configuration"
git push origin main

# Check backend health
curl https://link2hire-api.azurewebsites.net/health
```

---

## Environment URLs

| Environment | URL |
|-------------|-----|
| **Backend** | https://link2hire-api.azurewebsites.net |
| **Frontend** | https://[your-app].azurestaticapps.net |
| **API Docs** | https://link2hire-api.azurewebsites.net/docs |
| **Health Check** | https://link2hire-api.azurewebsites.net/health |

---

## Next Steps After Deployment

1. **Test all features**
   - Job extraction
   - Classification
   - LinkedIn post generation
   - Multi-role handling

2. **Monitor logs**
   - Azure App Service → **Log stream**
   - Static Web App → **Application Insights** (if enabled)

3. **Set up custom domain** (optional)
   - Configure in Azure Static Web Apps
   - Update CORS settings accordingly

4. **Enable HTTPS** (already enabled by default on Azure)

5. **Set up monitoring**
   - Application Insights for both services
   - Alert rules for errors

---

## Cost Monitoring

- **Azure Static Web Apps**: Free tier (100 GB bandwidth/month)
- **Azure App Service**: ~$13-50/month depending on tier
- **Azure OpenAI**: Pay-per-use (~$10-50/month estimated)
- **MongoDB Atlas**: Free tier (512MB)

**Total Estimated**: $23-100/month

---

**Deployment Date**: March 2026  
**Last Updated**: March 5, 2026
