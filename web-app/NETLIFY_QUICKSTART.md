# Quick Start - Deploy Web App to Netlify

## 📋 Checklist Nhanh

### ✅ Bước 1: Chuẩn bị (Đã xong)
- [x] `netlify.toml` đã được tạo
- [x] `package.json` đã có script `build:web`
- [x] Code đã push lên GitHub

### 🚀 Bước 2: Deploy trên Netlify (5 phút)

1. **Truy cập Netlify:** https://app.netlify.com
2. **Login** với GitHub account
3. **Click "Add new site" → "Import an existing project"**
4. **Chọn GitHub → Chọn repo "PKA-OpenDynamics/CityLens"**
5. **Configure:**
   ```
   Site name: citylens-mobile-app
   Branch: develop
   Base directory: web-app
   Build command: npm run build:web
   Publish directory: web-app/web-build
   ```
6. **Add environment variables:**
   - `TOMTOM_API_KEY` = your_api_key
   - `WEATHER_API_BASE_URL` = https://lonely-collection-netscape-pichunter.trycloudflare.com
   - `REPORTS_API_BASE_URL` = https://lonely-collection-netscape-pichunter.trycloudflare.com/api
7. **Click "Deploy site"**

### ⏳ Bước 3: Chờ build (2-3 phút)
- Xem build logs để theo dõi progress
- Nếu có lỗi, check logs và fix

### ✅ Bước 4: Test
- Mở URL: `https://citylens-mobile-app.netlify.app`
- Test login, map, reports

---

## 🔧 Nếu Có Lỗi

**Build failed?**
```bash
cd web-app
npm install
npm run build:web
# Nếu local build OK → Check Netlify logs
```

**API không hoạt động?**
- Check environment variables trên Netlify
- Đảm bảo backend đang chạy
- Check CORS settings

**404 khi refresh?**
- Đã có redirect trong `netlify.toml`
- Nếu vẫn lỗi, check publish directory

---

## 📚 Docs Đầy Đủ
Xem: `web-app/DEPLOY_NETLIFY.md`

---

**Thời gian deploy:** ~5-10 phút  
**Cost:** Free tier Netlify (100GB bandwidth/tháng)
