# Backend Deployment via GitHub Actions

## ✅ Created: GitHub Actions Workflow
File: `.github/workflows/azure-backend-deploy.yml`

This workflow will automatically deploy your FastAPI backend to Azure App Service when you push changes to the `backend/` folder.

---

## 🔑 Step 1: Get Publish Profile from Azure Portal

### Option A: Using Azure Portal (Easiest)
1. Open: https://portal.azure.com
2. Go to: **App Services** → **link2hire-api**
3. Click: **Get publish profile** (in the toolbar at top)
4. A file `link2hire-api.PublishSettings` will download
5. Open it with Notepad and **copy the entire contents**

### Option B: Using Azure CLI
Run this command and copy the output:
```powershell
az webapp deployment list-publishing-profiles `
  --name link2hire-api `
  --resource-group lin2hire-rg `
  --xml
```

---

## 🔐 Step 2: Add Publish Profile to GitHub Secrets

1. Open: https://github.com/abdullahfirdowsi/link2hire/settings/secrets/actions/new

2. Create new secret:
   - **Name:** `AZURE_WEBAPP_PUBLISH_PROFILE`
   - **Value:** Paste the entire publish profile XML

3. Click: **Add secret**

---

## 🚀 Step 3: Commit and Push Workflow

```powershell
git add .github/workflows/azure-backend-deploy.yml
git commit -m "ci: add backend deployment workflow"
git push origin main
```

This will trigger the backend deployment automatically.

---

## 📊 Step 4: Monitor Deployment

1. Go to: https://github.com/abdullahfirdowsi/link2hire/actions
2. You'll see: **Deploy FastAPI Backend to Azure App Service**
3. Wait ~2-3 minutes for deployment to complete

---

## ✅ After Deployment

Your backend will be live at:
- **API:** https://link2hire-api.azurewebsites.net
- **Docs:** https://link2hire-api.azurewebsites.net/docs
- **Health:** https://link2hire-api.azurewebsites.net/health

---

## 🔄 Future Deployments

From now on, whenever you push changes to `backend/`:
1. GitHub Actions automatically detects the change
2. Builds and deploys to Azure App Service
3. No manual steps needed!

---

## 💡 Manual Trigger

You can also manually trigger deployment:
1. Go to: https://github.com/abdullahfirdowsi/link2hire/actions
2. Select: **Deploy FastAPI Backend to Azure App Service**
3. Click: **Run workflow** → **Run workflow**
