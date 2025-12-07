# Hướng dẫn Đóng góp cho CityLens

Cảm ơn bạn quan tâm đến việc đóng góp cho dự án CityLens! Tài liệu này cung cấp hướng dẫn và quy tắc để đóng góp vào dự án.

## Mục lục

- [Quy tắc ứng xử](#quy-tắc-ứng-xử)
- [Bắt đầu](#bắt-đầu)
- [Quy trình phát triển](#quy-trình-phát-triển)
- [Chuẩn code](#chuẩn-code)
- [Quy tắc commit](#quy-tắc-commit)
- [Quy trình Pull Request](#quy-trình-pull-request)
- [Báo cáo lỗi](#báo-cáo-lỗi)
- [Đề xuất tính năng](#đề-xuất-tính-năng)
- [Tài liệu](#tài-liệu)
- [Cộng đồng](#cộng-đồng)

## Quy tắc ứng xử

Dự án này và tất cả mọi người tham gia đều tuân theo [Quy tắc ứng xử](CODE_OF_CONDUCT.md). Bằng việc tham gia, bạn cam kết tuân thủ các quy tắc này. Vui lòng báo cáo hành vi không phù hợp cho người duy trì dự án.

## Bắt đầu

### Yêu cầu trước khi bắt đầu

Đảm bảo bạn đã cài đặt các công cụ sau:

**Backend:**
- Python 3.11 trở lên
- PostgreSQL 15 trở lên với extension PostGIS
- Redis 7 trở lên
- Apache Jena Fuseki hoặc GraphDB
- MongoDB 6 trở lên

**Web Dashboard:**
- Node.js 18 trở lên
- npm 9 trở lên

**Mobile App:**
- Flutter 3.x
- Dart 3.x

### Thiết lập môi trường phát triển

1. Fork repository trên GitHub
2. Clone fork của bạn về máy:
   ```bash
   git clone https://github.com/TEN_BAN/CityLens.git
   cd CityLens
   ```

3. Thêm upstream repository:
   ```bash
   git remote add upstream https://github.com/CHU_DU_AN_GOC/CityLens.git
   ```

4. Thiết lập backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Chỉnh sửa file .env với cấu hình của bạn
   alembic upgrade head
   ```

5. Thiết lập web dashboard:
   ```bash
   cd web-dashboard
   npm install
   cp .env.example .env
   # Chỉnh sửa file .env với cấu hình của bạn
   ```

6. Thiết lập mobile app:
   ```bash
   cd mobile-app
   flutter pub get
   ```

## Quy trình phát triển

### Tạo branch mới

Luôn tạo branch mới cho công việc của bạn:

```bash
git checkout -b feature/ten-tinh-nang
# hoặc
git checkout -b fix/sua-loi
# hoặc
git checkout -b docs/cap-nhat-tai-lieu
```

Quy tắc đặt tên branch:
- `feature/` - Tính năng mới
- `fix/` - Sửa lỗi
- `docs/` - Cập nhật tài liệu
- `refactor/` - Tái cấu trúc code
- `test/` - Thêm hoặc cập nhật tests
- `chore/` - Công việc bảo trì

### Thực hiện thay đổi

1. Thực hiện thay đổi trong branch của bạn
2. Viết hoặc cập nhật tests nếu cần
3. Đảm bảo tất cả tests đều pass
4. Cập nhật tài liệu nếu cần thiết
5. Tuân thủ chuẩn code được nêu dưới đây

### Kiểm tra thay đổi

**Backend:**
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=app --cov-report=html
```

**Web Dashboard:**
```bash
cd web-dashboard
npm test
npm run lint
```

**Mobile App:**
```bash
cd mobile-app
flutter test
flutter analyze
```

## Chuẩn code

### Python (Backend)

- Tuân theo hướng dẫn phong cách PEP 8
- Sử dụng Black để format code
- Sử dụng isort để sắp xếp imports
- Sử dụng mypy để kiểm tra type
- Viết docstrings cho tất cả functions và classes công khai (phong cách Google)
- Độ dài dòng tối đa: 100 ký tự

Ví dụ:
```python
from typing import List, Optional

def xu_ly_bao_cao(
    bao_cao_id: int,
    nguoi_dung_id: int,
    trang_thai: Optional[str] = None
) -> dict:
    """Xử lý báo cáo từ người dân và cập nhật trạng thái.
    
    Args:
        bao_cao_id: ID của báo cáo cần xử lý
        nguoi_dung_id: ID của người dùng xử lý báo cáo
        trang_thai: Trạng thái mới cho báo cáo (tùy chọn)
        
    Returns:
        Dictionary chứa dữ liệu báo cáo đã cập nhật
        
    Raises:
        ValueError: Nếu bao_cao_id không hợp lệ
        PermissionError: Nếu người dùng không có quyền
    """
    # Triển khai ở đây
    pass
```

Chạy formatters:
```bash
black app/
isort app/
mypy app/
```

### TypeScript/React (Web Dashboard)

- Tuân theo Airbnb JavaScript Style Guide
- Sử dụng Prettier để format code
- Sử dụng ESLint để kiểm tra code
- Viết JSDoc comments cho các hàm phức tạp
- Sử dụng functional components với hooks
- Sử dụng TypeScript strict mode

Ví dụ:
```typescript
interface DuLieuBaoCao {
  id: string;
  tieu_de: string;
  muc_do: 'thap' | 'trung_binh' | 'cao';
}

/**
 * Lấy dữ liệu báo cáo từ API
 * @param baoCaoId - ID của báo cáo cần lấy
 * @returns Promise resolve về dữ liệu báo cáo
 */
async function layBaoCao(baoCaoId: string): Promise<DuLieuBaoCao> {
  const response = await fetch(`/api/v1/reports/${baoCaoId}`);
  return response.json();
}
```

Chạy formatters:
```bash
npm run format
npm run lint
```

### Dart (Mobile App)

- Tuân theo Effective Dart
- Sử dụng `dart format` để format code
- Sử dụng `dart analyze` để phân tích tĩnh
- Viết documentation comments cho public APIs
- Độ dài dòng tối đa: 80 ký tự

Ví dụ:
```dart
/// Đại diện cho một báo cáo từ người dân trong hệ thống.
class BaoCao {
  /// Tạo instance báo cáo mới.
  BaoCao({
    required this.id,
    required this.tieuDe,
    required this.mucDo,
  });

  /// Mã định danh duy nhất cho báo cáo này.
  final String id;
  
  /// Tiêu đề của báo cáo.
  final String tieuDe;
  
  /// Mức độ nghiêm trọng của báo cáo.
  final MucDo mucDo;
}
```

Chạy formatters:
```bash
dart format lib/
dart analyze
```

## Quy tắc commit

Chúng tôi tuân theo đặc tả Conventional Commits.

### Định dạng commit message

```
<loai>(<pham-vi>): <tieu-de>

<noi-dung>

<footer>
```

### Các loại commit

- `feat`: Tính năng mới
- `fix`: Sửa lỗi
- `docs`: Chỉ thay đổi tài liệu
- `style`: Thay đổi không ảnh hưởng đến ý nghĩa của code
- `refactor`: Thay đổi code không sửa lỗi cũng không thêm tính năng
- `perf`: Thay đổi code cải thiện hiệu năng
- `test`: Thêm tests thiếu hoặc sửa tests hiện có
- `build`: Thay đổi ảnh hưởng đến hệ thống build hoặc dependencies
- `ci`: Thay đổi files và scripts cấu hình CI
- `chore`: Thay đổi khác không sửa src hoặc test files

### Phạm vi

Phạm vi nên là tên của module bị ảnh hưởng:

- `backend`
- `web`
- `mobile`
- `api`
- `db`
- `docs`

### Ví dụ

```
feat(backend): them endpoint tao entity NGSI-LD

Triển khai endpoint POST /ngsi-ld/v1/entities chấp nhận
dữ liệu entity tuân thủ NGSI-LD và lưu vào PostgreSQL
và GraphDB.

Closes #123
```

```
fix(web): sua loi hieu nang marker clustering

Sửa memory leak trong component marker clustering bằng cách
dọn dẹp event listeners đúng cách khi component unmount.

Fixes #456
```

```
docs(readme): cap nhat huong dan cai dat

Thêm các bước chi tiết để thiết lập GraphDB và làm rõ
yêu cầu extension PostGIS của PostgreSQL.
```

## Quy trình Pull Request

### Trước khi submit

1. Đảm bảo code của bạn tuân thủ chuẩn code
2. Chạy tất cả tests và đảm bảo chúng pass
3. Cập nhật tài liệu nếu cần
4. Cập nhật CHANGELOG.md với thay đổi của bạn
5. Rebase branch của bạn trên upstream main mới nhất:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

### Submit Pull Request

1. Push branch của bạn lên fork:
   ```bash
   git push origin feature/ten-tinh-nang
   ```

2. Vào repository gốc trên GitHub
3. Click "New Pull Request"
4. Chọn fork và branch của bạn
5. Điền vào PR template với:
   - Mô tả rõ ràng về thay đổi
   - Số issue liên quan
   - Screenshots (nếu có)
   - Kiểm tra đã thực hiện
   - Hoàn thành checklist

### Định dạng tiêu đề PR

Tuân theo định dạng giống commit messages:
```
feat(backend): them he thong xac thuc nguoi dung
```

### Quy trình review

1. Ít nhất một maintainer phải review và approve
2. Tất cả CI checks phải pass
3. Không có conflict với branch main
4. Tất cả review comments phải được giải quyết

### Sau khi được approve

- Maintainers sẽ merge PR của bạn
- Branch của bạn sẽ bị xóa
- Thay đổi sẽ được đưa vào release tiếp theo

## Báo cáo lỗi

### Trước khi submit báo cáo lỗi

1. Kiểm tra các issues hiện có
2. Kiểm tra tài liệu
3. Thử tái hiện với phiên bản mới nhất

### Cách submit báo cáo lỗi

Sử dụng template báo cáo lỗi và bao gồm:

1. **Tiêu đề**: Tiêu đề rõ ràng, mô tả
2. **Mô tả**: Mô tả chi tiết về lỗi
3. **Các bước tái hiện**:
   - Bước 1
   - Bước 2
   - Bước 3
4. **Hành vi mong đợi**: Điều gì nên xảy ra
5. **Hành vi thực tế**: Điều gì thực sự xảy ra
6. **Screenshots**: Nếu có
7. **Môi trường**:
   - Hệ điều hành: [ví dụ: Ubuntu 22.04]
   - Trình duyệt: [ví dụ: Chrome 120]
   - Phiên bản: [ví dụ: v1.0.0]
8. **Thông tin bổ sung**: Bất kỳ thông tin liên quan nào khác

## Đề xuất tính năng

### Trước khi submit đề xuất tính năng

1. Kiểm tra xem tính năng đã tồn tại chưa
2. Kiểm tra các đề xuất tính năng hiện có
3. Xem xét xem nó có phù hợp với phạm vi dự án không

### Cách submit đề xuất tính năng

Sử dụng template đề xuất tính năng và bao gồm:

1. **Tiêu đề**: Tiêu đề rõ ràng, mô tả
2. **Vấn đề**: Tính năng này giải quyết vấn đề gì?
3. **Giải pháp đề xuất**: Nó nên hoạt động như thế nào?
4. **Phương án thay thế**: Các giải pháp khác bạn đã xem xét
5. **Lợi ích**: Tại sao điều này có giá trị?
6. **Thông tin bổ sung**: Mockups, ví dụ, v.v.

## Tài liệu

### Các loại tài liệu

- **Code Comments**: Giải thích logic phức tạp
- **API Documentation**: Tài liệu hóa tất cả endpoints
- **Hướng dẫn người dùng**: Giúp người dùng hiểu tính năng
- **Hướng dẫn developer**: Giúp developers đóng góp

### Chuẩn tài liệu

- Viết bằng tiếng Việt rõ ràng, đơn giản
- Sử dụng ngữ pháp và chính tả đúng
- Bao gồm ví dụ code
- Giữ tài liệu cập nhật với thay đổi code
- Sử dụng Markdown để format

### Build tài liệu

```bash
# Backend API docs
cd backend
python -m mkdocs build

# Web dashboard docs
cd web-dashboard
npm run docs
```

## Cộng đồng

### Kênh giao tiếp

- **GitHub Issues**: Báo cáo lỗi và đề xuất tính năng
- **GitHub Discussions**: Câu hỏi và thảo luận chung
- **Pull Requests**: Review code và cộng tác

### Nhận trợ giúp

Nếu bạn cần trợ giúp:

1. Kiểm tra tài liệu
2. Tìm kiếm các issues hiện có
3. Hỏi trong GitHub Discussions
4. Tag maintainers nếu khẩn cấp

### Ghi nhận

Contributors sẽ được:
- Liệt kê trong CONTRIBUTORS.md
- Đề cập trong release notes
- Ghi công trong project README

## Giấy phép

Bằng việc đóng góp cho CityLens, bạn đồng ý rằng các đóng góp của bạn sẽ được cấp phép dưới GNU General Public License v3.0 (GPL-3.0). Xem file [LICENSE](LICENSE) để biết chi tiết.

## Câu hỏi?

Nếu bạn có câu hỏi về việc đóng góp, vui lòng:
1. Kiểm tra tài liệu này kỹ lưỡng
2. Tìm kiếm các issues và discussions hiện có
3. Tạo discussion mới nếu cần

Cảm ơn bạn đã đóng góp cho CityLens!
