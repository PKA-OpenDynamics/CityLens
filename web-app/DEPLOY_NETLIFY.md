# Deploy CityLens Mobile Web App lên Netlify

## Bước 1: Chuẩn Bị Project

### 1.1. Kiểm tra dependencies
```bash
cd web-app
npm install
```

### 1.2. Test build locally
```bash
npm run build:web
```
Build output sẽ ở folder `web-build/`

## Bước 2: Tạo Tài Khoản Netlify

1. Truy cập: https://www.netlify.com
2. Sign up/Login với GitHub account
3. Authorize Netlify để access GitHub repos

## Bước 3: Deploy Qua Netlify Dashboard

### Cách 1: Deploy từ GitHub (Khuyến nghị)

**3.1. Push code lên GitHub:**
```bash
cd /Users/vudangkhoa/Working/CityLens
git add netlify.toml
git commit -m "feat: Add Netlify config for web-app deployment"
git push origin khoadev_features
```

**3.2. Trên Netlify Dashboard:**
1. Click **"Add new site"** → **"Import an existing project"**
2. Chọn **"GitHub"**
3. Tìm và chọn repository: **PKA-OpenDynamics/CityLens**
4. Authorize nếu được yêu cầu

**3.3. Configure build settings:**
```
Site name: citylens-mobile-app (hoặc tên bạn muốn)
Branch to deploy: khoadev_features (hoặc develop/main)
Base directory: web-app
Build command: npm run build:web
Publish directory: web-app/web-build
```

**3.4. Thêm Environment Variables:**
Click **"Add environment variables"** và thêm:
```
TOMTOM_API_KEY = your_tomtom_api_key
WEATHER_API_BASE_URL = https://lonely-collection-netscape-pichunter.trycloudflare.com
REPORTS_API_BASE_URL = https://lonely-collection-netscape-pichunter.trycloudflare.com/api
```

**3.5. Deploy:**
- Click **"Deploy site"**
- Netlify sẽ tự động build và deploy
- Chờ 2-5 phút

### Cách 2: Deploy Manual (Nhanh hơn cho test)

**3.1. Build locally:**
```bash
cd web-app
npm run build:web
```

**3.2. Deploy qua Netlify CLI:**
```bash
# Install Netlify CLI (nếu chưa có)
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd web-app
netlify deploy --prod --dir=web-build
```

**3.3. Hoặc drag & drop:**
1. Trên Netlify Dashboard, click **"Sites"** → **"Add new site"** → **"Deploy manually"**
2. Kéo thả folder `web-build/` vào

## Bước 4: Cấu Hình Domain (Optional)

**4.1. Custom subdomain:**
1. Trên site settings → **"Domain management"**
2. Click **"Options"** → **"Edit site name"**
3. Đặt tên: `citylens-mobile` → URL: `citylens-mobile.netlify.app`

**4.2. Custom domain:**
1. Click **"Add custom domain"**
2. Nhập domain: `app.citylens.com`
3. Follow hướng dẫn config DNS

## Bước 5: Cấu Hình Environment Variables

**Trên Netlify Dashboard:**
1. Site settings → **"Environment variables"**
2. Click **"Add a variable"** cho mỗi biến sau:

```
TOMTOM_API_KEY
- Value: your_actual_api_key
- Scopes: All

WEATHER_API_BASE_URL
- Value: https://lonely-collection-netscape-pichunter.trycloudflare.com
- Scopes: Production

REPORTS_API_BASE_URL
- Value: https://lonely-collection-netscape-pichunter.trycloudflare.com/api
- Scopes: Production
```

**Lưu ý:** Cloudflare tunnel URLs sẽ thay đổi mỗi khi restart. Cho production, nên dùng:
- Named Cloudflare tunnel
- Hoặc VPS với IP tĩnh
- Hoặc domain tên miền

## Bước 6: Trigger Deploy

**Tự động:**
- Mỗi khi push code lên branch đã config, Netlify tự động build & deploy

**Thủ công:**
1. Trên Netlify Dashboard → Site overview
2. Click **"Trigger deploy"** → **"Deploy site"**

## Bước 7: Kiểm Tra Deploy

**7.1. Check build logs:**
- Trên site overview, click vào deploy đang chạy
- Xem logs để debug nếu có lỗi

**7.2. Test website:**
- Mở URL: `https://your-site-name.netlify.app`
- Test các tính năng:
  - Login/Register
  - Map hiển thị
  - Gửi report
  - AI Assistant

## Troubleshooting

### Lỗi: "Build failed"

**Nguyên nhân:** Dependencies không đầy đủ hoặc lỗi build

**Giải pháp:**
```bash
# Clean và rebuild
cd web-app
rm -rf node_modules web-build
npm install
npm run build:web
```

Nếu build local OK nhưng Netlify fail:
1. Check Node version trên Netlify (phải >= 18)
2. Check environment variables

### Lỗi: "Page not found" khi refresh

**Nguyên nhân:** SPA routing không config

**Giải pháp:** Đã có trong `netlify.toml`:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Lỗi: "API calls failing"

**Nguyên nhân:** CORS hoặc environment variables sai

**Giải pháp:**
1. Check environment variables trên Netlify
2. Đảm bảo backend cho phép CORS từ Netlify domain
3. Test API endpoint bằng Postman

### Lỗi: "Expo web build failed"

**Nguyên nhân:** expo-cli không được install

**Giải pháp:** Build command phải là:
```bash
npx expo export:web
```

Hoặc update `package.json`:
```json
"build:web": "npx expo export:web"
```

## Best Practices

### 1. Separate environments:

**Development:**
```
Branch: develop
Site: citylens-mobile-dev.netlify.app
API: https://dev-backend.citylens.com
```

**Production:**
```
Branch: main
Site: citylens-mobile.netlify.app
API: https://api.citylens.com
```

### 2. Deploy previews:

Netlify tự động tạo preview cho mỗi PR:
- URL: `deploy-preview-123--citylens-mobile.netlify.app`
- Test trước khi merge

### 3. Continuous deployment:

```yaml
# netlify.toml
[build]
  ignore = "git diff --quiet HEAD^ HEAD -- web-app/"
```
Chỉ deploy khi có thay đổi trong `web-app/`

## Performance Optimization

### 1. Enable caching:
Đã config trong `netlify.toml`:
```toml
[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### 2. Enable compression:
Netlify tự động enable Gzip và Brotli

### 3. Optimize images:
```bash
# Install image optimizer
npm install --save-dev expo-optimize

# Run before build
npx expo-optimize
npm run build:web
```

## Monitoring

### 1. Analytics:
1. Site settings → **"Analytics"**
2. Enable Netlify Analytics ($9/tháng)

### 2. Function logs:
- Nếu dùng Netlify Functions
- Xem logs tại Functions tab

### 3. Uptime monitoring:
- Dùng services như UptimeRobot, Pingdom
- Alert qua email/Slack khi site down

## Cost

**Free tier (Netlify):**
- 100GB bandwidth/tháng
- 300 build minutes/tháng
- Unlimited sites
- HTTPS tự động

**Nếu vượt:**
- Pro plan: $19/tháng
- Hoặc optimize để giảm bandwidth

## Next Steps

1. ✅ Deploy web-app lên Netlify
2. ⏳ Setup custom domain
3. ⏳ Configure CD cho auto-deploy
4. ⏳ Setup staging environment
5. ⏳ Add monitoring & analytics

---

**Tóm tắt các lệnh cần chạy:**

```bash
# 1. Prepare
cd web-app
npm install

# 2. Build local (test)
npm run build:web

# 3. Commit config
cd ..
git add netlify.toml
git commit -m "feat: Add Netlify config"
git push origin khoadev_features

# 4. Deploy trên Netlify Dashboard
# → Import from GitHub
# → Configure build settings
# → Add environment variables
# → Deploy
```

**URL sau khi deploy:**
- Site sẽ có URL dạng: `https://citylens-mobile-<random>.netlify.app`
- Có thể đổi thành: `https://citylens-mobile.netlify.app`

Chúc bạn deploy thành công! 🚀
