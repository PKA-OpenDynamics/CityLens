# Video Demo cho Camera

## Hướng dẫn đặt video

Đặt 4 video demo (mỗi video 30 giây) vào thư mục này với tên:
- `camera1.mp4`
- `camera2.mp4`
- `camera3.mp4`
- `camera4.mp4`

## Mapping với Camera

### Hà Nội:
- **Khác Duy Tấn** → `camera1.mp4`
- **Vòng Xuyến Đào** → `camera2.mp4`
- **Ngã Tư Sở** → `camera3.mp4`
- **Cầu Nhật Tân** → `camera4.mp4`

### TP. Hồ Chí Minh:
- **Cầu Sài Gòn** → `camera1.mp4`
- **Ngã Sáu Gò Vấp** → `camera2.mp4`
- **Cầu Phú Mỹ** → `camera3.mp4`
- **Ngã Ba Hòa Hưng** → `camera4.mp4`

## Lưu ý

- Video nên có định dạng MP4 (H.264 codec) để tương thích tốt nhất
- Độ phân giải khuyến nghị: 640x480 hoặc 1280x720
- Dung lượng mỗi video: khoảng 5-10MB (cho 30s)
- Video sẽ tự động phát và lặp lại khi chọn camera

## Cách thay đổi đường dẫn video

Nếu bạn muốn đặt video ở nơi khác hoặc dùng URL từ server khác, chỉnh sửa file `MapScreen.web.tsx`:

```typescript
const CAMERA_VIDEO_MAP: Record<string, string> = {
  'Khác Duy Tấn': '/assets/videos/camera1.mp4', // hoặc URL đầy đủ
  // ...
};
```




