# Publishing Packages to GitHub Packages

Hướng dẫn publish các NPM packages của CityLens lên GitHub Packages.

## Yêu cầu

1. **GitHub Personal Access Token** với quyền:
   - `write:packages`
   - `read:packages`
   - `delete:packages` (optional)

2. **npm** đã được cài đặt

## Bước 1: Tạo GitHub Personal Access Token

1. Vào GitHub Settings: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Đặt tên: `CityLens Packages`
4. Chọn scopes:
   - ✅ `write:packages`
   - ✅ `read:packages`
   - ✅ `repo` (nếu repository private)
5. Click **"Generate token"**
6. **Lưu token** (chỉ hiện 1 lần!)

## Bước 2: Authenticate với GitHub Packages

```bash
npm login --registry=https://npm.pkg.github.com
```

Nhập thông tin:
- **Username**: your-github-username
- **Password**: your-personal-access-token (từ bước 1)
- **Email**: your-email@example.com

## Bước 3: Build và Publish

### Option 1: Publish tất cả packages (Khuyến nghị)

```bash
cd packages
./scripts/publish-all.sh
```

### Option 2: Publish từng package riêng lẻ

```bash
# citylens-utils
cd packages/citylens-utils
npm run build
npm publish

# citylens-geo-utils
cd ../citylens-geo-utils
npm run build
npm publish

# citylens-ngsi-ld
cd ../citylens-ngsi-ld
npm run build
npm publish
```

## Bước 4: Xác nhận Packages đã publish

1. Vào: https://github.com/PKA-OpenDynamics/CityLens/packages
2. Bạn sẽ thấy 3 packages:
   - `@pka-opendynamics/citylens-utils`
   - `@pka-opendynamics/citylens-geo-utils`
   - `@pka-opendynamics/citylens-ngsi-ld`

## Bước 5: Cài đặt từ GitHub Packages

Để sử dụng packages đã publish, người dùng cần tạo file `.npmrc`:

```bash
# .npmrc
@pka-opendynamics:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=YOUR_GITHUB_TOKEN
```

Sau đó cài đặt:

```bash
npm install @pka-opendynamics/citylens-utils
npm install @pka-opendynamics/citylens-geo-utils
npm install @pka-opendynamics/citylens-ngsi-ld
```

## Troubleshooting

### Lỗi 401 Unauthorized

```bash
# Re-authenticate
npm logout --registry=https://npm.pkg.github.com
npm login --registry=https://npm.pkg.github.com
```

### Lỗi 404 Not Found

Kiểm tra:
- Package name phải match với owner: `@pka-opendynamics/...`
- Repository URL đúng trong package.json
- Token có đủ quyền

### Lỗi "You cannot publish over the previously published versions"

Package đã được publish với version này. Tăng version:

```bash
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.0 → 1.1.0
npm version major  # 1.0.0 → 2.0.0
```

## Update Packages

Khi có thay đổi:

```bash
# 1. Tăng version
cd packages/citylens-utils
npm version patch  # hoặc minor/major

# 2. Build và publish
npm run build
npm publish
```

## Xóa Package Version

Nếu cần xóa version đã publish:

```bash
npm unpublish @pka-opendynamics/citylens-utils@1.0.0 --registry=https://npm.pkg.github.com
```

**Lưu ý**: Chỉ xóa được trong vòng 72 giờ sau khi publish.

## Automation với GitHub Actions

Tạo file `.github/workflows/publish-packages.yml` để tự động publish khi có tag:

```yaml
name: Publish Packages

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          registry-url: 'https://npm.pkg.github.com'
      
      - name: Install dependencies
        run: |
          cd packages/citylens-utils && npm install
          cd ../citylens-geo-utils && npm install
          cd ../citylens-ngsi-ld && npm install
      
      - name: Publish packages
        run: cd packages && ./scripts/publish-all.sh
        env:
          NODE_AUTH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Links

- **GitHub Packages**: https://github.com/PKA-OpenDynamics/CityLens/packages
- **Documentation**: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-npm-registry
