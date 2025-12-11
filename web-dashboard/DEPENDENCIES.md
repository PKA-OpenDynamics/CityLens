# CityLens Web Dashboard - Dependencies

Tài liệu này liệt kê tất cả các thư viện và gói phần mềm được sử dụng trong dự án CityLens Web Dashboard.

## Phiên bản Runtime

- **Node.js**: 20+ (LTS khuyến nghị)
- **npm**: 10+

## Thư viện chính (Dependencies)

### Core Framework

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Next.js](https://nextjs.org/) | 14.2.33 | MIT | React framework với SSR/SSG |
| [React](https://react.dev/) | 18.3.1 | MIT | UI library |
| [React DOM](https://react.dev/) | 18.3.1 | MIT | React DOM renderer |
| [TypeScript](https://www.typescriptlang.org/) | 5.6.3 | Apache-2.0 | Type-safe JavaScript |

### UI & Styling

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Tailwind CSS](https://tailwindcss.com/) | 3.4.15 | MIT | Utility-first CSS |
| [Lucide React](https://lucide.dev/) | 0.460.0 | ISC | Icon library |
| [class-variance-authority](https://cva.style/) | 0.7.1 | Apache-2.0 | Component variants |
| [clsx](https://github.com/lukeed/clsx) | 2.1.1 | MIT | ClassName utility |
| [tailwind-merge](https://github.com/dcastil/tailwind-merge) | 2.5.5 | MIT | Tailwind class merging |
| [Framer Motion](https://www.framer.com/motion/) | 11.13.5 | MIT | Animation library |
| [next-themes](https://github.com/pacocoursey/next-themes) | 0.4.4 | MIT | Theme switching |

### Maps & Geospatial

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Leaflet](https://leafletjs.com/) | 1.9.4 | BSD-2-Clause | Interactive maps |
| [leaflet.markercluster](https://github.com/Leaflet/Leaflet.markercluster) | 1.5.3 | MIT | Marker clustering |

> **Lưu ý**: Dự án sử dụng Leaflet trực tiếp với custom React wrapper (`src/components/map/LeafletReactWrapper.tsx`) để đảm bảo tuân thủ giấy phép mã nguồn mở (Leaflet: BSD-2-Clause).

### Data & State Management

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Axios](https://axios-http.com/) | 1.7.9 | MIT | HTTP client |
| [Zustand](https://zustand-demo.pmnd.rs/) | 5.0.2 | MIT | State management |
| [Zod](https://zod.dev/) | 3.23.8 | MIT | Schema validation |

### Charts & Visualization

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [Recharts](https://recharts.org/) | 2.14.1 | MIT | Chart library |

### Utilities

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [date-fns](https://date-fns.org/) | 4.1.0 | MIT | Date utilities |
| [react-router-dom](https://reactrouter.com/) | 7.10.1 | MIT | Routing (backup) |

### Build Tools

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [PostCSS](https://postcss.org/) | 8.4.49 | MIT | CSS processing |
| [Autoprefixer](https://autoprefixer.github.io/) | 10.4.20 | MIT | CSS vendor prefixes |

## Development Dependencies

| Thư viện | Phiên bản | Giấy phép | Mô tả |
|----------|-----------|-----------|-------|
| [ESLint](https://eslint.org/) | 8.57.1 | MIT | JavaScript linter |
| [eslint-config-next](https://nextjs.org/docs/basic-features/eslint) | 14.2.33 | MIT | Next.js ESLint config |
| [Prettier](https://prettier.io/) | 3.4.2 | MIT | Code formatter |
| [prettier-plugin-tailwindcss](https://github.com/tailwindlabs/prettier-plugin-tailwindcss) | 0.6.9 | MIT | Tailwind class sorting |
| [@types/leaflet](https://www.npmjs.com/package/@types/leaflet) | 1.9.15 | MIT | Leaflet TypeScript types |

## Type Definitions

| Package | Phiên bản | Mô tả |
|---------|-----------|-------|
| @types/node | 22.10.2 | Node.js types |
| @types/react | 18.3.12 | React types |
| @types/react-dom | 18.3.1 | React DOM types |
| @types/leaflet | 1.9.15 | Leaflet types |
| @types/leaflet.markercluster | 1.5.6 | Marker cluster types |

## Cài đặt

```bash
# Cài đặt tất cả dependencies
npm install

# Hoặc với yarn
yarn install

# Hoặc với pnpm
pnpm install
```

## Build Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Format code
npm run format
```

## Tương thích giấy phép

Tất cả các thư viện được sử dụng đều có giấy phép tương thích với GPL-3.0:
- MIT License ✓
- BSD Licenses (2-Clause) ✓
- Apache-2.0 ✓
- ISC License ✓

Dự án CityLens Web Dashboard được phát hành theo giấy phép **GNU General Public License v3.0 (GPL-3.0)**.

## External Services

Dashboard kết nối với CityLens Backend API để lấy dữ liệu. Không có external service nào được gọi trực tiếp từ frontend.

### Map Tiles

| Provider | Mục đích | Giấy phép |
|----------|----------|-----------|
| [OpenStreetMap](https://www.openstreetmap.org/) | Base map tiles | ODbL |
| [CartoDB](https://carto.com/) | Light/Dark map themes | CC BY 3.0 |
