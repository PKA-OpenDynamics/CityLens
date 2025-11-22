# CityLens Web Dashboard

Dashboard quản lý cho hệ thống thành phố thông minh CityLens.

## Công nghệ

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **UI Library**: Material-UI 5
- **State Management**: Zustand
- **Maps**: Mapbox GL JS
- **Charts**: Recharts
- **HTTP Client**: Axios

## Cài đặt

### Yêu cầu hệ thống

- Node.js 20+
- npm hoặc yarn

### Cài đặt từ mã nguồn

```bash
# Di chuyển đến thư mục
cd web-dashboard

# Cài đặt dependencies
npm install

# Copy file cấu hình
cp .env.example .env
# Chỉnh sửa .env với thông tin của bạn

# Chạy development server
npm run dev
```

Ứng dụng sẽ chạy tại: http://localhost:3000

## Build cho production

```bash
npm run build
```

File build sẽ được tạo trong thư mục `dist/`

## Chạy với Docker

```bash
docker build -t citylens-web .
docker run -p 80:80 citylens-web
```

## Cấu trúc thư mục

```
web-dashboard/
├── src/
│   ├── components/    # React components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── store/         # State management
│   ├── hooks/         # Custom hooks
│   ├── types/         # TypeScript types
│   ├── utils/         # Utility functions
│   ├── theme.ts       # MUI theme
│   ├── App.tsx        # Main app component
│   └── main.tsx       # Entry point
├── public/            # Static assets
└── package.json       # Dependencies
```

## License

MIT License - xem file [LICENSE](../LICENSE)
