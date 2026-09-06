# Original User Request

## 2026-09-06T05:48:20Z

# Teamwork Project: fedu.vn/font Interactive Type Hub

Xây dựng hệ thống thư viện quản lý, trải nghiệm và tải font trực tuyến tại `fedu.vn/font` (Web tĩnh độc lập HTML/CSS/JS thuần + CDN R2/GitHub Pages), bóc tách danh mục từ tài liệu "Font LIst - 2022.pdf" và kho font cục bộ/Google Drive của anh Việt, tự động đóng gói 1.070 file rời rạc trong folder Drive thành từng thư mục con theo Family có link public tải trọn bộ zip, và cho phép xem trước trực tiếp tương tác (Type Tester) mà không phụ thuộc cài đặt máy tính.

Working directory: `/Users/vietmac/Documents/CODE/fedu-font`
Integrity mode: development

## Context & Resources
- File tài liệu PDF phân tích gốc: `/Users/vietmac/Downloads/Font LIst - 2022.pdf`
- Thư mục Google Drive chứa 1.070 font gốc: `https://drive.google.com/drive/folders/1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao?usp=drive_link` (Folder ID: `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`). Công cụ CLI `rclone` đã cấu hình remote `gdrive:` và token Google Drive có sẵn trong hệ thống (`~/.config/`).
- Kho font cục bộ trên máy Mac: `/Users/vietmac/Documents/CODE/typo/fonts/`, `/Users/vietmac/Documents/CODE/course/fonts/`, `/Users/vietmac/Library/Fonts/`.
- Mã nguồn trang quản lý font trước đây của anh Việt: `/Users/vietmac/Documents/CODE/font-manager/` (repo `vietndj/chonchu`).

## Requirements

### R1. Bóc Tách & Tái Cấu Trúc Danh Mục Font (Vượt Qua Giới Hạn PDF Cũ)
- Bóc tách toàn diện 20 trang tài liệu `Font LIst - 2022.pdf` (gồm 4 nhóm cốt lõi: Serif, Sans Serif, Monospace/Script/Blackletter, và Bộ sưu tập Vintage Sài Gòn Oldstyle) kết hợp toàn bộ kho font thực tế trên máy và Google Drive.
- Tái cấu trúc theo **Ma Trận Tuyển Chọn 3 Chiều**:
  1. *Phân loại thị giác*: Serif (Oldstyle, Modern, Slab, Italic), Sans Serif (Humanist, Geometric, Neo-grotesque, Condensed, Extended), Monospace, Script, Việt Nam Vintage.
  2. *Tâm lý & Tính cách thương hiệu (Mood/Vibe)*: Luxury & Sang trọng, Tech & Công nghệ, Bold & Tuyên ngôn, Friendly & Nhân văn, Nostalgic & Cổ điển.
  3. *Ngữ cảnh ứng dụng thực chiến*: Display / Headline (tiêu đề nổi bật, poster, thumbnail) vs Body text (đọc văn bản dài, phụ đề, paragraph).
- Mỗi font có đầy đủ metadata: Tên font, Nhà thiết kế/Foundry, Nhận định của Đạo diễn/Designer từ tài liệu gốc, Phân tích độ tương phản/trục nghiêng/x-height, Tình trạng hỗ trợ tiếng Việt.

### R2. Hệ Thống Type Tester Trực Tuyến Độc Lập (Không Phụ Thuộc Cài Đặt)
- Cơ chế Web Font rendering: Host font file trực tuyến (hoặc chuyển đổi WOFF2 siêu nhẹ / nạp động qua OpenType.js), đảm bảo học viên mở web trên bất kỳ máy tính hay điện thoại nào cũng hiển thị đúng 100% font chữ mà không cần cài font vào hệ điều hành.
- Bộ công cụ tương tác Type Tester chuyên nghiệp:
  - Cho phép học viên tự nhập chuỗi văn bản tiếng Việt có dấu bất kỳ để kiểm tra thẩm mỹ và độ tương thích dấu tiếng Việt tức thì.
  - Bộ điều khiển linh hoạt: Cỡ chữ (Font size 14px - 140px), Giãn dòng (Line-height), Khoảng cách ký tự (Letter-spacing/Kerning).
  - Tùy biến môi trường: Chuyển đổi Dark Mode (#121212) / Light Mode (#FFFFFF) / Neon Accent để đánh giá độ tương phản thị giác trong nhiều bối cảnh thiết kế.
  - Xem bảng ký tự Glyph / Ligatures và so sánh các biến thể độ dày (Weights: Thin -> Heavy, Regular, Italic).

### R3. Tự Động Gom Nhóm & Đóng Gói 1.070 Font Trên Google Drive Thành Thư Mục Family
- Chạy script tự động phân tích 1.070 file font rời rạc trong thư mục Google Drive gốc (`1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`).
- Gom nhóm các file cùng họ font thành từng thư mục con riêng biệt theo chuẩn Family (ví dụ: thư mục `SVN-Saol Standard/`, `SVN-Sequel/`, `SVN-Vanguard CF/`, `SVN-Walsheim Pro/`, `SVN-Integral CF/`, `SVN-Woodland/`...).
- Thiết lập quyền truy cập công khai (Public view/download) cho từng thư mục Family trên Google Drive để học viên có thể tải toàn bộ bộ font (.zip) chỉ với 1 click.
- Tự động đồng bộ link thư mục Google Drive tương ứng vào từng thẻ font trên trang web.

### R4. Xây Dựng Giao Diện Web Tĩnh Độc Lập & Triển Khai fedu.vn/font
- Kiến trúc Web tĩnh (HTML/CSS/JS thuần, tối ưu Mobile-First, tải trang < 1 giây, không phụ thuộc framework nặng).
- Thiết kế giao diện Dark Mode thanh lịch, chuẩn mực studio type quốc tế (lấy cảm hứng từ Grilli Type và Pangram Pangram).
- Hệ thống tìm kiếm tức thì (Instant Search) và bộ lọc nhanh đa tiêu chí (Category, Mood, Weight, Vietnamese support).
- Triển khai hosting đồng bộ vào hệ thống domain `fedu.vn/font` (hoặc GitHub Pages `vietndj/font` / `vietndj.github.io`).

## Acceptance Criteria

### Danh Mục Dữ Liệu
- [ ] Bóc tách đầy đủ toàn bộ các font có trong `Font LIst - 2022.pdf` và liên kết với kho font SVN thực tế.
- [ ] Dữ liệu hiển thị dạng JSON chuẩn, có đầy đủ tags: category, mood, use-case, weights, vietnamese_support, director_notes.

### Trải Nghiệm Type Tester
- [ ] Gõ thử văn bản tiếng Việt có dấu hoạt động mượt mà tức thì 100% trên giao diện mà không cần cài font vào máy khách.
- [ ] Bộ lọc đa chiều hoạt động tức thì (Category, Mood, Search) không làm giật lag hay tải lại trang.
- [ ] Thanh slider chỉnh size/kerning phản hồi thời gian thực (real-time).

### Đóng Gói & Tải Về Google Drive
- [ ] 1.070 file font trên Google Drive được sắp xếp gọn gàng vào các thư mục con theo từng Family.
- [ ] 100% thẻ font trên web đều có nút "Tải Trọn Bộ Family (.zip)" dẫn chính xác tới thư mục Google Drive được mở quyền public.
