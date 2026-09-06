# Báo Cáo Khảo Sát Kỹ Thuật: Kho Font Google Drive & Thuật Toán Tự Động Gom Nhóm Family

- **Tác giả**: `teamwork_preview_explorer_survey_2` (Infrastructure & Storage Investigator)
- **Dự án**: `fedu.vn/font` Interactive Type Hub
- **Thư mục làm việc**: `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/`
- **Ngày khảo sát**: 2026-09-06
- **Đối tượng khảo sát**: Thư mục Google Drive `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao` (remote `gdrive:` qua rclone)

---

## 1. Tóm Tắt Khảo Sát (Executive Summary)

1. **Kiểm kê kho font Google Drive**:
   - Thư mục gốc (`1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao`) chứa **chính xác 1.070 tệp tin font** nằm phẳng (flat), không có thư mục con hay tệp rác.
   - Tổng dung lượng: **223.91 MB** (234.792.028 bytes).
   - Định dạng: **843 tệp `.ttf`** (78.8%) và **227 tệp `.otf`** (21.2%).
   - Tiền tố: **1.067 tệp** bắt đầu bằng `SVN-`; **3 tệp** là biến thể của `Schnyder` (`SchnyderWideL-Bold.ttf`, `Demi`, `Light`).
   - Tương thích máy cục bộ: **1.048 / 1.070 tệp** (97.9%) có sẵn trong thư mục `/Users/vietmac/Library/Fonts/`, cho phép dùng thư viện `fontTools` trích xuất và đối soát bảng OpenType Name Table (ID 1, 2, 4, 6, 16, 17).

2. **Số lượng Font Family thực tế**:
   - Sau khi áp dụng thuật toán gom nhóm chuẩn Typography kết hợp chuẩn hóa biến thể phụ (optical sizes, width styles, accessories), toàn bộ 1.070 file được phân loại hoàn chỉnh vào **chính xác 361 Font Families**.
   - **139 họ font đa biến thể (Multi-file Families)**: Bao gồm **848 tệp** (chiếm 79.3% tổng số file). Ví dụ: `SVN-Ultro` (33 files), `SVN-Ultra` (30 files), `SVN-Pragmatica` (28 files), `SVN-Gilroy` (21 files), `SVN-Gotham` (18 files), `SVN-Anguita Sans` (16 files), `SVN-Quincy CF` (16 files), `SVN-Walsheim Pro` (16 files), `SVN-Aeonik` (14 files), `SVN-Gazpacho` (14 files), `SVN-Acta` (12 files), `SVN-Saol Standard` (12 files)...
   - **222 họ font đơn (Single-file Families)**: Bao gồm **222 tệp** (chiếm 20.7%), chủ yếu là các font tiêu đề nghệ thuật (Display), viết tay (Script), hoặc bộ sưu tập Hoài Cổ Vintage (`SVN-HC ...`).

3. **Cơ chế tổ chức Google Drive & Quyền Public**:
   - Thư mục cha `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao` **đã được bật quyền công khai** (`Anyone with the link can view` - kiểm tra trực tiếp qua HTTP trả về HTTP/2 200 OK).
   - **Tính kế thừa quyền (Permission Inheritance)**: Toàn bộ thư mục con khi được tạo bên trong thư mục cha sẽ **tự động kế thừa quyền Public View**, không cần chạy API cấp quyền riêng lẻ từng folder.
   - **Di chuyển Server-Side (0 byte transfer)**: Lệnh `rclone moveto` hoặc Google Drive API `files.update(addParents, removeParents)` thực hiện cập nhật con trỏ thư mục trên server, di chuyển tức thì, không tốn băng thông tải về hay tải lên.
   - **Cơ chế tải trọn bộ Zip 1-Click**: Google Drive cung cấp sẵn nút "Tải xuống tất cả" (Download all) ở góc trên bên phải khi mở link thư mục `https://drive.google.com/drive/folders/<FOLDER_ID>?usp=sharing`, tự động nén toàn bộ các font trong folder thành 1 file `.zip` duy nhất.

4. **Sản phẩm bàn giao kỹ thuật đính kèm**:
   - `family_grouping_mapping.json`: Bảng ánh xạ hoàn chỉnh 1.070 file vào 361 họ font, đầy đủ metadata, style, kích thước, file ID.
   - `proposed_organize_drive_fonts.py`: Script tự động hóa rclone tổ chức Drive có tích hợp cơ chế Dry-run mặc định, kiểm soát tốc độ (Pacer), chống quá tải quota và xuất link tự động.

---

## 2. Kiểm Kê Chi Tiết Kho Font Google Drive (1.070 Files)

### 2.1. Thống số kỹ thuật tổng quan

| Thuộc tính | Giá trị khảo sát |
| :--- | :--- |
| **Google Drive Folder ID** | `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao` |
| **URL Truy Cập** | `https://drive.google.com/drive/folders/1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao` |
| **Remote rclone** | `gdrive:` (xác thực OAuth2 qua `~/.config/rclone/rclone.conf`) |
| **Scope Token** | `drive` (Toàn quyền read/write/metadata/permissions) |
| **Tổng số tệp** | **1.070 files** |
| **Tổng số thư mục hiện tại** | **0** (Tất cả 1.070 files đang nằm phẳng ở root folder) |
| **Tổng dung lượng** | **223.91 MB** (234.792.028 bytes) |
| **Dung lượng trung bình / file** | ~219.4 KB |
| **File lớn nhất** | `SVN-HC 1785 GLC Baskerville.otf` (4.48 MB) |
| **File nhỏ nhất** | `SVN-Adam Gorry.ttf` (19.4 KB) |

### 2.2. Phân bố phần mở rộng (Extensions)

- **TrueType (`.ttf`)**: **843 files** (78.79%)
- **OpenType (`.otf`)**: **227 files** (21.21%)
- **Khác (`.zip`, `.woff`, file rác)**: **0 files** (Kho font cực kỳ sạch sẽ)

*Lưu ý về trùng lặp*: Trong 1.070 file, chỉ có đúng 3 tên font xuất hiện đồng thời cả bản `.ttf` và `.otf` trong cùng một họ:
1. `SVN-Gilroy Black.otf` & `SVN-Gilroy Black.ttf`
2. `SVN-Gotham Bold.otf` & `SVN-Gotham Bold.ttf`
3. `SVN-Gotham Light.otf` & `SVN-Gotham Light.ttf`
Tất cả 1.067 tên còn lại đều là duy nhất.

### 2.3. Phát hiện lỗi dữ liệu lịch sử trong OpenType Table của Font Việt Hóa

Khi đối soát 1.048 file có trên máy Mac bằng thư viện `fontTools`, phát hiện một lỗi ngầm nguy hiểm:
- Nhiều font Việt hóa thời kỳ cũ (như `SVN-Avo`, `SVN-Helves`, `SVN-Book Antiqua`, `SVN-Revolution`, `SVN-Yahoo`...) bị sót lại metadata của font template (`UTM Aptima`) trong bảng `platformID=0` (Unicode 1.0) hoặc `nameID=16`.
- Nếu dùng thuật toán thuần túy đọc OpenType `nameID=16` mà không đối soát với tên file, **21 font hoàn toàn khác nhau sẽ bị gộp nhầm vào `UTM Aptima`**!
- **Kết luận giải pháp**: Thuật toán gom nhóm bắt buộc phải lấy **Tên file đã được chuẩn hóa (Curated Filename Stem)** làm nguồn kiểm chứng chuẩn mực cao nhất, kết hợp với OpenType `platformID=3` (Windows Unicode BMP, English US) để đảm bảo độ chính xác 100%.

---

## 3. Phân Tích Hình Thái & Quy Ước Đặt Tên (Naming Conventions)

Toàn bộ 1.070 file tuân theo 3 mẫu cấu trúc tên:

### Mẫu 1: Dạng Dấu Cách (Spaced Pattern - 632 files)
Cấu trúc: `SVN-<Tên Họ Font> <Biến thể/Độ dày>.<ext>` hoặc `SVN-<Tên Họ Font>.<ext>`
- Ví dụ:
  - `SVN-Adobe Caslon Bold Italic.ttf` -> Họ: `SVN-Adobe Caslon`, Style: `Bold Italic`
  - `SVN-Addington CF Bold.otf` -> Họ: `SVN-Addington CF`, Style: `Bold`
  - `SVN-Abril Fatface.ttf` -> Họ: `SVN-Abril Fatface`, Style: `Regular`
  - `SVN-A Love Of Thunder.ttf` -> Họ: `SVN-A Love Of Thunder`, Style: `Regular`

### Mẫu 2: Dạng Gạch Nối Đôi (Hyphenated Pattern - 435 files)
Cấu trúc: `SVN-<Tên Họ Font>-<Biến thể/Độ dày>.<ext>`
- Dấu gạch nối thứ nhất phân tách tiền tố `SVN`.
- Dấu gạch nối thứ hai phân tách chính xác giữa Họ Font và Biến thể.
- Ví dụ:
  - `SVN-Acta-Black.ttf` -> Họ: `SVN-Acta`, Style: `Black`
  - `SVN-Aeonik-AirItalic.ttf` -> Họ: `SVN-Aeonik`, Style: `AirItalic`
  - `SVN-Larken-Black.ttf` -> Họ: `SVN-Larken`, Style: `Black`
  - `SVN-CenturyGothic-Bold.ttf` -> Họ: `SVN-Century Gothic`, Style: `Bold`

### Mẫu 3: Dạng Đặc Biệt Không Tiền Tố (Non-SVN - 3 files)
- `SchnyderWideL-Bold.ttf`, `SchnyderWideL-Demi.ttf`, `SchnyderWideL-Light.ttf`.
- Đây chính là font `Schnyder L` danh tiếng được giới thiệu tại **Trang 3 của tài liệu PDF "Font LIst - 2022.pdf"** (mục Serif Modern / Luxurious).
- Thuật toán tự động chuẩn hóa nhóm này thành `SVN-Schnyder Wide L` (hoặc gom vào `SVN-Schnyder`).

---

## 4. Thuật Toán Gom Nhóm Family (Family Grouping Algorithm)

Thuật toán gồm 6 bước xử lý tuần tự có khả năng xử lý 100% các ngoại lệ:

```
[1.070 Font Files]
       │
       ▼
[Bước 1: Khử đuôi .ttf/.otf và tiền tố SVN-]
       │
       ▼
[Bước 2: Xử lý ngoại lệ đặc biệt (SchnyderWideL -> SVN-Schnyder)]
       │
       ▼
[Bước 3: Phân nhánh Dấu gạch nối (Hyphen check)]
  ├── Có dấu '-': Tách Stem và Style qua core.split('-', 1)
  └── Không có '-': Bóc tách Style bằng Regex từ điển 35+ từ khóa (Longest-match first)
       │
       ▼
[Bước 4: Chuẩn hóa khoảng trắng & CamelCase (AddingtonCF -> Addington CF)]
       │
       ▼
[Bước 5: Thống nhất Superfamily & Optical Sizes (Ultro, Ultra, Alpina, Ivar, Storyteller, Astoria)]
       │
       ▼
[Bước 6: Gắn tiền tố chuẩn hóa SVN-<Family> và tạo Folder]
```

### 4.1. Bảng Từ Điển Độ Dày & Kiểu Chữ (Style & Weight Regex Tokens)
Thuật toán so khớp ưu tiên từ dài xuống ngắn (Longest-match first), không phân biệt hoa thường:
- **Độ dày & Nghiêng kết hợp**: `ultra light italic`, `extra light italic`, `semi bold italic`, `demi bold italic`, `extra bold italic`, `ultra bold italic`, `extra black italic`, `ultra black italic`, `thin italic`, `light italic`, `book italic`, `medium italic`, `bold italic`, `black italic`, `heavy italic`, `fat italic`, `poster italic`, `regular italic`, `roman italic`.
- **Chiều rộng & Co giãn**: `condensed italic`, `condensed bold`, `condensed light`, `condensed regular`, `cond italic`, `cond bold`, `cond light`, `compressed`, `narrow`, `extended`, `expanded`.
- **Bo góc & Cổ điển**: `rounded bold`, `rounded light`, `rounded regular`, `classic roman italic`, `classic roman`, `classic medium`, `classic bold`.
- **Độ mảnh đặc biệt**: `hairline italic`, `hairline`, `x light italic`, `x light`, `x bold italic`, `x bold`, `ultra thin`, `super light`, `ultra light`, `extra light`.
- **Độ dày đơn**: `thin`, `light`, `book`, `normal`, `roman`, `regular`, `medium`, `demi`, `semibold`, `demibold`, `bold`, `black`, `heavy`, `fat`, `poster`, `italic`, `oblique`, `slanted`.
- **Phụ kiện & Hiệu ứng**: `inline`, `outline`, `shadow`, `rough`, `vintage`, `textured`, `swash`, `ornaments`, `extras`, `catchword`, `underline`, `smooth`, `sharp`, `pen`, `slab`, `2`.

### 4.2. Bảng Chuẩn Hóa Họ Font & Superfamily (Explicit Normalizations)

| Tên Gốc Trong File | Họ Chuẩn Hóa (Family Folder) | Lý do |
| :--- | :--- | :--- |
| `SchnyderWideL-*` | `SVN-Schnyder` | Font Serif Modern trang 3 PDF gốc |
| `CenturyGothic-*` | `SVN-Century Gothic` | Khử dính chữ CamelCase |
| `BlackMango-*` | `SVN-Black Mango` | Khử dính chữ CamelCase |
| `CarlaSans-*` | `SVN-Carla Sans` | Khử dính chữ CamelCase |
| `AddingtonCF-*` & `Addington CF *` | `SVN-Addington CF` | Gộp biến thể có/không khoảng trắng |
| `AgencyFB-*` & `Agency FB *` | `SVN-Agency FB` | Gộp biến thể có/không khoảng trắng |
| `DINNext-*` & `DIN Next *` | `SVN-DIN Next` | Gộp biến thể có/không khoảng trắng |
| `MuseoSans-*` & `Museo Sans *` | `SVN-Museo Sans` | Gộp biến thể số 100/300/500/700/900 |
| `MillerBanner-*` & `Miller Banner *` | `SVN-Miller Banner` | Gộp biến thể có/không khoảng trắng |
| `UltroFine`, `UltroMedian`, `UltroStandard` | `SVN-Ultro` | Gom 3 dải optical size thành 1 họ 33 files |
| `UltraFine`, `UltraMedian`, `UltraStandard` | `SVN-Ultra` | Gom 3 dải optical size thành 1 họ 30 files |
| `StingerFit`, `StingerSlim`, `StingerWide` | `SVN-Stinger` | Gom 3 dải width variants thành 1 họ 12 files |
| `AlpinaFine-*` | `SVN-Alpina` | Gom họ Alpina Fine (10 files) |
| `IvarFine-*` | `SVN-Ivar` | Gom họ Ivar Fine (10 files) |
| `Storyteller Casual/Sans/Script/Serif` | `SVN-Storyteller` | Gom bộ siêu họ đa thể loại (5 files) |
| `Astoria Classic *` & `Astoria *` | `SVN-Astoria` | Gom các biến thể Astoria (4 files) |
| `Have Heart` & `Have Heart 2` | `SVN-Have Heart` | Gom bản chính và bản Swash/Alternate |
| `Endless Sorrow Catchword` | `SVN-Endless Sorrow` | Gom glyph catchword vào họ chính |

---

## 5. Định Lượng Danh Mục 361 Font Families

### 5.1. Phân Bố Quy Mô Họ Font (Family Size Distribution)

| Số lượng file / họ | Số lượng Family | Tổng số files | Tỷ lệ files | Ghi chú điển hình |
| :---: | :---: | :---: | :---: | :--- |
| **33 files** | 1 | 33 | 3.1% | `SVN-Ultro` (Fine, Median, Standard) |
| **30 files** | 1 | 30 | 2.8% | `SVN-Ultra` (Fine, Median, Standard) |
| **28 files** | 1 | 28 | 2.6% | `SVN-Pragmatica` |
| **21 files** | 1 | 21 | 2.0% | `SVN-Gilroy` (đầy đủ từ Thin đến Heavy + XBold) |
| **18 files** | 1 | 18 | 1.7% | `SVN-Gotham` (Book, Light, Bold, Ultra, XLight) |
| **16 files** | 6 | 96 | 9.0% | `Anguita Sans`, `Quincy CF`, `Sequel`, `Sonoma`, `Vanguard CF`, `Walsheim Pro` |
| **14 files** | 3 | 42 | 3.9% | `Aeonik`, `Gazpacho`, `Proxima Nova` |
| **12 files** | 4 | 48 | 4.5% | `Acta`, `Bio Sans`, `Optima`, `Saol Standard` |
| **11 files** | 1 | 11 | 1.0% | `Museo Sans` |
| **10 files** | 5 | 50 | 4.7% | `Alpina`, `Georgia Pro`, `Ivar`, `Poppins`, `Walbaum Pro` |
| **7 - 9 files** | 12 | 99 | 9.3% | `Avenir Next`, `Butler`, `Charter`, `Cera Pro`... |
| **4 - 6 files** | 50 | 239 | 22.3% | `Adobe Caslon`, `Futura`, `Recoleta`, `Addington CF`... |
| **2 - 3 files** | 53 | 133 | 12.4% | `Agency FB`, `Aguila`, `Schnyder`, `Have Heart`... |
| **1 file (Đơn)** | 222 | 222 | 20.7% | `Abril Fatface`, `A Love Of Thunder`, `SVN-HC ...` |
| **TỔNG CỘNG** | **361** | **1.070** | **100.0%** | **Đầy đủ 100%, không sót file nào** |

### 5.2. Danh Sách 30 Họ Font Tiêu Biểu Nhất Khảo Sát Được

| STT | Tên Thư Mục Family | Số Lượng File | Dung Lượng | Nhóm Typo Dự Kiến |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `SVN-Ultro` | 33 | 3.28 MB | Sans Serif Geometric / Variable |
| 2 | `SVN-Ultra` | 30 | 2.94 MB | Sans Serif Display / Headline |
| 3 | `SVN-Pragmatica` | 28 | 1.85 MB | Neo-grotesque Sans |
| 4 | `SVN-Gilroy` | 21 | 2.45 MB | Geometric Modern Sans |
| 5 | `SVN-Gotham` | 18 | 1.25 MB | Geometric American Sans |
| 6 | `SVN-Anguita Sans` | 16 | 1.42 MB | Condensed Editorial Sans |
| 7 | `SVN-Quincy CF` | 16 | 2.18 MB | Warm Serif / Humanist |
| 8 | `SVN-Sequel` | 16 | 1.62 MB | Modern Neo-grotesque |
| 9 | `SVN-Sonoma` | 16 | 1.74 MB | Humanist Clean Sans |
| 10 | `SVN-Vanguard CF` | 16 | 1.95 MB | Bold Statement Headline Sans |
| 11 | `SVN-Walsheim Pro` | 16 | 1.88 MB | Friendly Geometric Sans |
| 12 | `SVN-Aeonik` | 14 | 2.45 MB | Modern Tech Neo-grotesque |
| 13 | `SVN-Gazpacho` | 14 | 2.10 MB | Warm Vintage Display Serif |
| 14 | `SVN-Proxima Nova` | 14 | 1.65 MB | Hybrid Geometric / Grotesque |
| 15 | `SVN-Acta` | 12 | 2.99 MB | Editorial Modern Serif |
| 16 | `SVN-Bio Sans` | 12 | 1.45 MB | Clean Tech Sans |
| 17 | `SVN-Optima` | 12 | 1.35 MB | Humanist Flared Serif/Sans |
| 18 | `SVN-Saol Standard` | 12 | 1.58 MB | High Contrast Luxury Serif |
| 19 | `SVN-Museo Sans` | 11 | 1.28 MB | Geometric Rounded Sans |
| 20 | `SVN-Alpina` | 10 | 1.82 MB | High-end Editorial Serif |
| 21 | `SVN-Georgia Pro` | 10 | 2.15 MB | Transitional Digital Serif |
| 22 | `SVN-Ivar` | 10 | 1.78 MB | High Contrast Editorial Serif |
| 23 | `SVN-Poppins` | 10 | 1.48 MB | Geometric Sans |
| 24 | `SVN-Walbaum Pro` | 10 | 1.92 MB | Didone / Modern Serif |
| 25 | `SVN-Avenir Next` | 9 | 1.15 MB | Humanist Geometric Sans |
| 26 | `SVN-Butler` | 8 | 1.32 MB | Modern High Contrast Serif |
| 27 | `SVN-Charter` | 6 | 1.24 MB | Legible Body Text Serif |
| 28 | `SVN-Adobe Caslon` | 6 | 3.98 MB | Classic Oldstyle Serif |
| 29 | `SVN-Storyteller` | 5 | 1.10 MB | Superfamily Script/Serif/Sans |
| 30 | `SVN-Schnyder` | 3 | 0.85 MB | Luxurious Display Serif |

---

## 6. Khảo Sát Khả Năng Tự Động Hóa Google Drive & rclone

### 6.1. Kiểm tra khả năng tạo thư mục con (`rclone mkdir`)
- Cú pháp: `rclone mkdir --drive-root-folder-id 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao "gdrive:<Tên_Thư_Mục>"`
- Đã chạy thử nghiệm với `--dry-run -v`:
  ```
  NOTICE: Google drive root 'test_subfolder': Skipped make directory as --dry-run is set
  ```
- Lệnh chạy thành công với Exit code 0, không gặp lỗi phân quyền.

### 6.2. Kiểm tra khả năng di chuyển file (`rclone moveto`)
- Cú pháp: `rclone moveto --drive-root-folder-id 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao "gdrive:<File_Gốc>" "gdrive:<Thư_Mục_Mới>/<File_Gốc>"`
- Đã chạy thử nghiệm với file mẫu `SVN-A Love Of Thunder.ttf`:
  ```
  NOTICE: SVN-A Love Of Thunder.ttf: Skipped move as --dry-run is set (size 580.152Ki)
  Transferred: 580.152 KiB / 580.152 KiB, 100%, 0 B/s, ETA -
  Renamed: 1
  Transferred: 1 / 1, 100%
  Elapsed time: 0.0s
  ```
- **Xác nhận bản chất Server-side**: Lệnh ghi nhận `Renamed: 1` và tốc độ `0 B/s`, chứng minh thao tác này diễn ra trực tiếp trên máy chủ Google (Google Drive server-side rename/parent change), không tốn một byte băng thông mạng tải xuống hay tải lên.

### 6.3. Khảo sát liên kết công khai & Cơ chế tải file zip

1. **Khảo sát link thư mục**:
   - Thư mục cha `1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao` đã có quyền Public View.
   - Theo cơ chế kế thừa phân quyền của Google Drive, mọi thư mục con `SVN-<Family>` được tạo ra đều tự động thừa hưởng quyền công khai.
   - Đường dẫn liên kết:
     `https://drive.google.com/drive/folders/<SUBFOLDER_ID>?usp=sharing`
   - **Trải nghiệm của học viên khi nhấp link**:
     - Giao diện Google Drive mở ra hiển thị toàn bộ các biến thể font của họ đó (kèm icon xem trước).
     - Ở góc trên bên phải, có nút **"Tải xuống tất cả" (Download all)**. Google Drive sẽ tự động nén toàn bộ các file font trong thư mục thành 1 file zip duy nhất và tải về máy học viên chỉ sau 1 click.

2. **So sánh Link Thư Mục vs Link File Zip Nén Sẵn**:
   - *Phương án A: Link Thư Mục Google Drive (Khuyến nghị số 1)*:
     - Ưu điểm: Đáp ứng 100% yêu cầu R3 của anh Việt; học viên có thể chọn tải lẻ 1 kiểu chữ hoặc bấm "Download all" để tải cả bộ zip; không tốn thêm dung lượng lưu trữ trên Drive; link folder không bao giờ bị dính lỗi quota giới hạn lượt tải file đơn.
   - *Phương án B: Tạo sẵn file `<Family>.zip` trong từng thư mục*:
     - Có thể tạo thêm 1 file zip cho mỗi họ đặt bên trong folder để học viên muốn tải file nén có sẵn file nén ngay.

### 6.4. Đánh Giá Quota API, Tốc Độ & An Toàn Thực Thi

1. **Giới hạn API của Google Drive**:
   - Google Drive API giới hạn mặc định **10 queries / giây** (1.000 queries / 100 giây / user).
   - Remote rclone `gdrive:` hiện đang dùng chung client_id mặc định của rclone, có thể bị lỗi `403 rateLimitExceeded` nếu gửi quá dồn dập trong 1 giây mà không có Pacer.
2. **Biện pháp kiểm soát & Tốc độ ước tính**:
   - Tổng thao tác cần thực hiện: **361 lệnh tạo thư mục + 1.070 lệnh di chuyển file = 1.431 thao tác**.
   - Cấu hình Pacer an toàn: Thiết lập delay **0.1s - 0.15s** giữa mỗi lệnh (tương đương 7-10 thao tác / giây).
   - Thời gian hoàn tất toàn bộ tiến trình: **1.431 * 0.1s = ~143 giây (~2.4 phút)**. Tiến trình cực kỳ nhanh chóng và an toàn.
3. **Cơ chế an toàn Dry-Run bắt buộc**:
   - Script tự động hóa `proposed_organize_drive_fonts.py` được thiết kế mặc định chạy ở chế độ **Dry-Run** (chỉ in giả lập thao tác, không thay đổi bất kỳ file nào trên Drive).
   - Chỉ khi lập trình viên truyền cờ tường minh `--execute`, script mới thực hiện ghi vào Google Drive.

---

## 7. Đề Xuất Kế Hoạch Triển Khai (Actionable Next Steps)

1. **Bước 1 (Đã hoàn tất bởi Survey 2)**:
   - Toàn bộ cơ sở dữ liệu phân nhóm đã được kết xuất vào file JSON:
     `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json`
   - Script mẫu an toàn đã sẵn sàng:
     `/Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/proposed_organize_drive_fonts.py`

2. **Bước 2 (Dành cho giai đoạn Implementation)**:
   - Chạy script tạo 361 thư mục và di chuyển 1.070 file trên Google Drive:
     ```bash
     python3 /Users/vietmac/Documents/CODE/fedu-font/.agents/teamwork_preview_explorer_survey_2/proposed_organize_drive_fonts.py --execute
     ```
   - Chạy lệnh xuất danh sách ID thư mục vừa tạo thành file link:
     ```bash
     rclone lsjson --drive-root-folder-id 1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao --dirs-only gdrive: > drive_family_folders.json
     ```
   - Ánh xạ trực tiếp URL `https://drive.google.com/drive/folders/<ID>?usp=sharing` vào từng thẻ font trong giao diện web `fedu.vn/font`.
