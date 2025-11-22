# Đóng góp cho CityLens

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án CityLens! Tài liệu này hướng dẫn cách bạn có thể tham gia.

## Cách bắt đầu

1. Fork repository
2. Clone về máy của bạn
3. Tạo branch mới cho thay đổi của bạn
4. Thực hiện thay đổi
5. Push và tạo Pull Request

## Quy tắc commit

Sử dụng format sau cho commit message:

```
<type>: <subject>

<body>
```

Types:
- `feat`: Tính năng mới
- `fix`: Sửa lỗi
- `docs`: Thay đổi documentation
- `style`: Format code
- `refactor`: Refactoring code
- `test`: Thêm tests
- `chore`: Thay đổi build, tools

Ví dụ:
```
feat: thêm chức năng báo cáo ngập nước

Cho phép người dùng báo cáo ngập nước với ảnh và độ sâu
```

## Code Style

### Python (Backend)
- Tuân theo PEP 8
- Sử dụng Black formatter
- Type hints bắt buộc
- Docstrings cho functions/classes

### TypeScript (Web)
- Tuân theo ESLint rules
- Sử dụng Prettier formatter
- Type annotations bắt buộc

### Dart (Mobile)
- Tuân theo Dart style guide
- Sử dụng dart format

## Testing

Tất cả code mới phải có tests:

```bash
# Backend
pytest tests/

# Web
npm test

# Mobile
flutter test
```

## Pull Request Process

1. Đảm bảo code pass tất cả tests
2. Cập nhật README nếu cần
3. Cập nhật CHANGELOG.md
4. Request review từ maintainers

## Báo cáo lỗi

Sử dụng GitHub Issues với template:

```markdown
**Mô tả lỗi**
Mô tả ngắn gọn về lỗi

**Cách tái hiện**
1. Bước 1
2. Bước 2

**Kết quả mong đợi**
Điều bạn mong đợi sẽ xảy ra

**Screenshots**
Nếu có

**Môi trường**
- OS: 
- Version:
```

## Đề xuất tính năng

Sử dụng GitHub Issues để đề xuất tính năng mới. Giải thích rõ:
- Vấn đề cần giải quyết
- Giải pháp đề xuất
- Lợi ích

## License

Bằng việc đóng góp, bạn đồng ý rằng code của bạn được phát hành dưới Apache 2.0 License.
