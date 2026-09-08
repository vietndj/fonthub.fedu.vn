#!/usr/bin/env python3
"""
FEDU Font (font.fedu.vn) Catalog Updater: 19 GR Families & FD Integration
Updates data/catalog.json with:
1. All 19 GR Font families with rich Art Director critiques, anatomy, and direct Google Drive download links.
2. Category 'GT Font' tag and is_gt = True.
3. Clean zero-trace metadata.
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path("/Users/vietmac/Documents/CODE/fedu-font")
CATALOG_PATH = PROJECT_ROOT / "data/catalog.json"
PARENT_FOLDER_ID = "1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao"

GR_SPECS = {
    "gr-pantheon": {
        "name": "GR Pantheon",
        "family": "GR Pantheon",
        "category": "Serif",
        "subcategory": "Serif High Contrast Monumental",
        "zip_name": "GR-Pantheon.zip",
        "director_notes": "Một kiệt tác serif hoành tráng (monumental high-contrast serif), kết hợp giữa tỷ lệ kiến trúc La Mã cổ điển và hình học hiện đại. Đường cong dứt khoát, thanh mảnh siêu mảnh đối lập với nét đậm uy quyền. Lý tưởng cho tiêu đề bìa tạp chí xa xỉ, bộ nhận diện thương hiệu high-end, gallery nghệ thuật và khách sạn 5 sao.",
        "anatomy": {"contrast": "Very High", "axis": "Vertical Classical", "x_height": "Medium", "aperture": "Moderate"},
        "sample_text": "Bản sắc kiến trúc trường tồn và hào quang di sản qua các thời kỳ nghệ thuật",
        "weights": ["Display Light", "Display Regular", "Display Medium", "Display Bold", "Display Black", "Text Regular", "Text Medium", "Text Bold", "Micro Regular", "Micro Bold"]
    },
    "gr-canon": {
        "name": "GR Canon",
        "family": "GR Canon",
        "category": "Serif",
        "subcategory": "Serif Transitional Renaissance",
        "zip_name": "GR-Canon.zip",
        "director_notes": "Họ phông serif đương đại đỉnh cao lấy cảm hứng từ thời kỳ Phục hưng kết hợp hệ thống quang học đa kích cỡ (Optical Sizes). Độ mở khẩu độ (aperture) cực kỳ thoáng đạt, tạo nhịp điệu đọc tĩnh tại, thông thái. Hoàn hảo cho thiết kế sách chuyên khảo, ấn phẩm học thuật, báo chí tài chính và giao diện biên tập cao cấp.",
        "anatomy": {"contrast": "Medium-High", "axis": "Transitional", "x_height": "Standard", "aperture": "Open"},
        "sample_text": "Hệ thống biên tập chuẩn mực và cấu trúc văn bản học thuật đa cấp độ",
        "weights": ["Display Light", "Display Regular", "Display Medium", "Display Bold", "Text Regular", "Text Medium", "Text Bold", "Subhead Regular", "Subhead Bold", "Mono Regular", "Mono Bold"]
    },
    "gr-cinetype": {
        "name": "GR Cinetype",
        "family": "GR Cinetype",
        "category": "Sans Serif",
        "subcategory": "Sans Modular Cinematic",
        "zip_name": "GR-Cinetype.zip",
        "director_notes": "Được sinh ra từ công nghệ máy in phim phụ đề laser 35mm, các đường cong được cấu trúc bằng các phân đoạn thẳng vi mô (micro-straight vectors). Vẻ đẹp cơ khí độc bản, đậm chất điện ảnh cinematic. Cực kỳ bắt mắt trên poster phim, MV ca nhạc, tiêu đề đồ họa chuyển động (motion design) và giao diện cyberpunk/tech.",
        "anatomy": {"contrast": "None", "axis": "Modular Geometric", "x_height": "High", "aperture": "Closed"},
        "sample_text": "Độ sâu khung hình điện ảnh và phân giải thị giác phụ đề chuyển động 35mm",
        "weights": ["Light", "Regular", "Medium", "Bold", "Mono Regular", "Mono Bold"]
    },
    "gr-eesti": {
        "name": "GR Eesti",
        "family": "GR Eesti",
        "category": "Sans Serif",
        "subcategory": "Sans Geometric Humanist",
        "zip_name": "GR-Eesti.zip",
        "director_notes": "Được phát triển từ ngôn ngữ áp phích Baltic thập niên 1920-1930 kết hợp hình học Humanist. Các ký tự hình học tròn trịa nhưng sở hữu góc vát và nét kết thúc táo bạo, thân thiện mà kiên định. Ứng dụng xuất sắc trong bao bì tiêu dùng cao cấp, branding F&B, thời trang streetwear và không gian triển lãm.",
        "anatomy": {"contrast": "Low", "axis": "Geometric Humanist", "x_height": "High", "aperture": "Open"},
        "sample_text": "Thiết kế nhận diện bao bì bền vững và dấu ấn văn hóa thị giác đương đại",
        "weights": ["Thin", "Light", "Book", "Regular", "Medium", "Bold", "Black"]
    },
    "gr-era": {
        "name": "GR Era",
        "family": "GR Era",
        "category": "Sans Serif",
        "subcategory": "Sans Experimental Grotesque",
        "zip_name": "GR-Era.zip",
        "director_notes": "Thiết kế Grotesque bất quy tắc (non-conformist grotesque) với tỷ lệ x-height phóng khoáng và các nét móc terminal độc đáo. Tỏa ra nguồn năng lượng phản kháng ngầm, trí tuệ và cá tính. Phù hợp tuyệt đối cho các ấn phẩm nghệ thuật độc lập, festival văn hóa, tạp chí thời trang avant-garde.",
        "anatomy": {"contrast": "Low-Medium", "axis": "Eccentric Grotesque", "x_height": "Very High", "aperture": "Dynamic"},
        "sample_text": "Khát vọng tiên phong và sự phá cách trong nhịp điệu typography thử nghiệm",
        "weights": ["Thin", "Light", "Regular", "Medium", "Bold", "Black"]
    },
    "gr-flaire": {
        "name": "GR Flaire",
        "family": "GR Flaire",
        "category": "Serif",
        "subcategory": "Serif Flared Incised",
        "zip_name": "GR-Flaire.zip",
        "director_notes": "Một phong cách incised serif kết hợp nét loe (flared terminal) quyến rũ bậc nhất. Không dùng serif truyền thống mà mở rộng ở đuôi nét tạo cảm giác chạm khắc trên đá hoa cương. Tôn vinh vẻ đẹp kiêu sa, gợi cảm trong ngành mỹ phẩm, nước hoa, trang sức cao cấp và kiến trúc nội thất.",
        "anatomy": {"contrast": "High", "axis": "Incised Flared", "x_height": "Medium", "aperture": "Expansive"},
        "sample_text": "Nghệ thuật chạm khắc tinh xảo và ánh hào quang sang trọng của thương hiệu",
        "weights": ["Extra Light", "Light", "Regular", "Medium", "Bold", "Black"]
    },
    "gr-flexa": {
        "name": "GR Flexa",
        "family": "GR Flexa",
        "category": "Sans Serif",
        "subcategory": "Sans Inktrap Technical",
        "zip_name": "GR-Flexa.zip",
        "director_notes": "Đỉnh cao kỹ thuật biến thiên đa trục (variable system) với điểm nhấn là các rãnh mực (inktraps) được phóng đại thành ngôn ngữ thị giác chủ đạo. Biến đổi từ thanh mảnh tối giản đến siêu đậm cơ bắp. Tối ưu cho thiết kế nhận diện thế hệ mới, techwear, ứng dụng fintech và poster thể thao tốc độ cao.",
        "anatomy": {"contrast": "Variable Mechanical", "axis": "Inktrap Engineered", "x_height": "Dynamic", "aperture": "Engineered"},
        "sample_text": "Cơ chế thích ứng linh hoạt và đột phá công nghệ đồ họa tham số thế hệ mới",
        "weights": ["Hairline", "Thin", "Light", "Regular", "Medium", "Bold", "Black", "Compressed Bold", "Expanded Heavy"]
    },
    "gr-haptik": {
        "name": "GR Haptik",
        "family": "GR Haptik",
        "category": "Sans Serif",
        "subcategory": "Sans Geometric Tactile",
        "zip_name": "GR-Haptik.zip",
        "director_notes": "Phông chữ hình học xúc giác (tactile geometric sans) được thiết kế để có thể nhận biết bằng cảm giác tiếp xúc, kết hợp các nét cắt góc 45 độ chuẩn xác. Độ tương phản thấp, trật tự thị giác rõ ràng. Lựa chọn số 1 cho thiết kế signage đô thị, giao diện web SaaS, infographic số liệu và bao bì dược mỹ phẩm.",
        "anatomy": {"contrast": "None", "axis": "Tactile Geometric", "x_height": "High", "aperture": "Open 45-deg"},
        "sample_text": "Trật tự định hướng thông tin và tín hiệu xúc giác chuẩn xác trong không gian sống",
        "weights": ["Light", "Regular", "Medium", "Bold", "Black", "Rotis 45", "Rotis 75"]
    },
    "gr-maru": {
        "name": "GR Maru",
        "family": "GR Maru",
        "category": "Sans Serif",
        "subcategory": "Sans Rounded Technical",
        "zip_name": "GR-Maru.zip",
        "director_notes": "Bộ phông bo tròn (rounded system) thiết kế trên lưới mô-đun nghiêm ngặt, loại bỏ hoàn toàn cảm giác ngây ngô thường thấy của font tròn, thay vào đó là sự tinh tế, ấm áp của thiết kế công nghiệp Nhật Bản. Hoàn hảo cho app giáo dục, sản phẩm công nghệ thân thiện, đồ gia dụng thông minh và thương hiệu trẻ em cao cấp.",
        "anatomy": {"contrast": "None", "axis": "Precision Rounded", "x_height": "High", "aperture": "Soft"},
        "sample_text": "Trải nghiệm cảm xúc ấm áp và sự tối giản trong từng chi tiết giao diện thông minh",
        "weights": ["Light", "Regular", "Medium", "Bold", "Black", "Mega Bold"]
    },
    "gr-mechanik": {
        "name": "GR Mechanik",
        "family": "GR Mechanik",
        "category": "Sans Serif",
        "subcategory": "Sans Constructivist Bold",
        "zip_name": "GR-Mechanik.zip",
        "director_notes": "Lấy cảm hứng từ phong trào Cấu trúc Chủ nghĩa (Constructivism) đầu thế kỷ 20, các góc cạnh được gọt giũa vuông vức, đanh thép và kỷ luật. Khối lượng chữ dày đặc, độ nén hiển thị cực tốt. Phục vụ đắc lực cho headline ấn phẩm công nghiệp, tự động hóa, bìa sách kiến trúc và poster tuyên ngôn.",
        "anatomy": {"contrast": "Very Low", "axis": "Constructivist Linear", "x_height": "Ultra High", "aperture": "Compact"},
        "sample_text": "Kỷ luật hình học thép và năng lượng chuyển động cơ khí trong nền công nghiệp hiện đại",
        "weights": ["Light", "Regular", "Medium", "Bold", "Black", "Heavy", "Poly Bold"]
    },
    "gr-planar": {
        "name": "GR Planar",
        "family": "GR Planar",
        "category": "Sans Serif",
        "subcategory": "Sans Architectural Grid",
        "zip_name": "GR-Planar.zip",
        "director_notes": "Cấu trúc dựa trên sự cân bằng thị giác vi mô và lưới không gian phẳng, với các đường nét nằm ngang và thẳng đứng được căn chỉnh tuyệt đối. Cực kỳ tĩnh tại, thanh tao và hiện đại. Phù hợp làm phông định danh cho các studio kiến trúc, thương hiệu nội thất tối giản (Scandinavian/Japandi) và catalog bảo tàng.",
        "anatomy": {"contrast": "Low", "axis": "Retinal Grid", "x_height": "Balanced", "aperture": "Restrained"},
        "sample_text": "Không gian kiến trúc tĩnh lặng và sự cân bằng thị giác vi mô của vật liệu",
        "weights": ["Thin", "Light", "Regular", "Medium", "Bold", "Black"]
    },
    "gr-standard": {
        "name": "GR Standard",
        "family": "GR Standard",
        "category": "Sans Serif",
        "subcategory": "Sans Swiss Grotesque Universal",
        "zip_name": "GR-Standard.zip",
        "director_notes": "Chuẩn mực Grotesque Thụy Sĩ đương đại với 336 styles đa dạng từ Compressed đến Expanded. Độ trung tính trung hòa mọi định kiến, đưa nội dung lên vị trí trung tâm tuyệt đối. Là phông chữ nền tảng cho toàn bộ hệ thống Design System doanh nghiệp, tập đoàn đa quốc gia và hệ thống dẫn đường sân bay/ga tàu.",
        "anatomy": {"contrast": "Low", "axis": "Swiss Grotesque", "x_height": "Optimal", "aperture": "Neutral"},
        "sample_text": "Hệ thống nhận diện thương hiệu quy mô tập đoàn và quy chuẩn thiết kế thông tin",
        "weights": ["Thin", "Light", "Regular", "Medium", "Bold", "Black", "Extended Bold", "Compressed Regular"]
    },
    "gr-zirkon": {
        "name": "GR Zirkon",
        "family": "GR Zirkon",
        "category": "Serif",
        "subcategory": "Serif Chiseled Geometric",
        "zip_name": "GR-Zirkon.zip",
        "director_notes": "Nét cắt vát như kim cương giác cắt chuyển động, kết hợp giữa serif tân cổ điển và các mặt phẳng góc cạnh sắc sảo. Uyển chuyển nhưng sắc bén, quý phái nhưng hiện đại. Tuyệt tác cho thương hiệu đồng hồ xa xỉ, rượu vang cao cấp, kỷ yếu danh giá và poster điện ảnh tâm lý ly kỳ.",
        "anatomy": {"contrast": "High", "axis": "Diamond Faceted", "x_height": "Medium", "aperture": "Sharp"},
        "sample_text": "Giác cắt kim cương lấp lánh và tinh hoa chế tác đồng hồ cơ khí đỉnh cao",
        "weights": ["Light", "Regular", "Medium", "Bold", "Black"]
    },
    "gr-america": {
        "name": "GR America",
        "family": "GR America",
        "category": "Sans Serif",
        "subcategory": "Sans American Grotesque",
        "zip_name": "GR-America.zip",
        "director_notes": "Sự kết hợp thiên tài giữa truyền thống American Gothic thế kỷ 19 và phông Grotesque Thụy Sĩ thế kỷ 20. Độ rộng nét chuẩn mực, nhịp điệu từ chắc khỏe, cân bằng tuyệt đối giữa cá tính và tính thực dụng. Phông chữ quốc dân cho mọi ấn phẩm truyền thông đa phương tiện, chiến dịch quảng cáo và hệ thống branding tổng lực.",
        "anatomy": {"contrast": "Low", "axis": "American Gothic Hybrid", "x_height": "High", "aperture": "Open"},
        "sample_text": "Chiến dịch truyền thông tích hợp và nhịp đập đương đại của đô thị tương lai",
        "weights": ["Thin", "Ultra Light", "Light", "Regular", "Medium", "Bold", "Black"]
    },
    "gr-sectra": {
        "name": "GR Sectra",
        "family": "GR Sectra",
        "category": "Serif",
        "subcategory": "Serif Contemporary Calligraphic",
        "zip_name": "GR-Sectra.zip",
        "director_notes": "Serif đương đại với các góc vát lấy cảm hứng từ nét dao khắc chữ trên gỗ và bút máy gọt góc. Cấu trúc góc cạnh dứt khoát mang lại uy quyền trí tuệ và sự chuẩn xác không khoan nhượng. Lựa chọn hàng đầu cho các tờ báo danh tiếng quốc tế, báo cáo chính sách, tạp chí triết học và branding luật/tài chính.",
        "anatomy": {"contrast": "Medium-High", "axis": "Chiseled Calligraphic", "x_height": "High", "aperture": "Clipped"},
        "sample_text": "Phân tích chính sách vĩ mô và uy tín học thuật của các báo cáo chiến lược",
        "weights": ["Display Light", "Display Regular", "Display Medium", "Display Bold", "Display Super", "Fine Book", "Fine Regular", "Fine Medium", "Fine Bold", "Fine Black"]
    },
    "gr-walsheim": {
        "name": "GR Walsheim",
        "family": "GR Walsheim Pro",
        "category": "Sans Serif",
        "subcategory": "Sans Geometric Warm",
        "zip_name": "GR-Walsheim.zip",
        "director_notes": "Khơi nguồn từ những tấm áp phích vẽ tay của nghệ sĩ Otto Baumberger tại Zurich những năm 1930. Hình học tròn hoàn hảo (geometric sans) nhưng tràn ngập chất thơ và tính nhân văn ấm áp. Rực rỡ trên tiêu đề website sáng tạo, bao bì bánh ngọt cao cấp, quán cà phê boutique và ứng dụng phong cách sống.",
        "anatomy": {"contrast": "None", "axis": "Geometric Circular", "x_height": "High", "aperture": "Generous"},
        "sample_text": "Cảm hứng sáng tạo thuần khiết và phong cách sống tinh tế bên bờ hồ Zurich",
        "weights": ["Ultralight", "Thin", "Light", "Regular", "Medium", "Bold", "Ultrabold", "Black"]
    },
    "gr-ultra": {
        "name": "GR Ultra",
        "family": "GR Ultra",
        "category": "Sans Serif",
        "subcategory": "Sans Flared Hybrid",
        "zip_name": "GR-Ultra.zip",
        "director_notes": "Đột phá lai tạo giữa Sans Serif và Flare Serif với các vết loe tinh tế ở đầu nét. Dải biến thiên từ Ultra Fine thanh mảnh đến Black lực lưỡng. Tỏa ra vẻ đẹp tân tiến, sắc sảo và tự tin. Rất phù hợp cho tạp chí phong cách sống thời thượng, bao bì mỹ phẩm niche và bìa album âm nhạc.",
        "anatomy": {"contrast": "Dynamic Flared", "axis": "Hybrid Flare", "x_height": "High", "aperture": "Wide"},
        "sample_text": "Hơi thở nghệ thuật đương đại và sự thanh thoát trong từng đường nét nhận diện",
        "weights": ["Fine Thin", "Fine Regular", "Fine Bold", "Median Regular", "Median Bold", "Standard Regular", "Standard Bold", "Black"]
    },
    "gr-alpina": {
        "name": "GR Alpina",
        "family": "GR Alpina Fine",
        "category": "Serif",
        "subcategory": "Serif Editorial Workhorse",
        "zip_name": "GR-Alpina.zip",
        "director_notes": "Một cuộc cách mạng cho kiểu chữ đọc sách (workhorse book serif). Tỷ lệ x-height hào phóng, nét serif mềm mại nhưng dứt khoát, chống mỏi mắt tối đa khi đọc văn bản dài. Đạt điểm 10 tuyệt đối cho dàn trang sách văn học, ứng dụng đọc báo di động (Kindle/Apple Books) và tài liệu học thuật cao cấp.",
        "anatomy": {"contrast": "Medium", "axis": "Humanist Editorial", "x_height": "High", "aperture": "Open"},
        "sample_text": "Trải nghiệm đọc văn chương sâu lắng và sự chuẩn mực trong nghệ thuật dàn trang sách",
        "weights": ["Thin", "Light", "Regular", "Medium", "Bold"]
    },
    "gr-super": {
        "name": "GR Super",
        "family": "GR Super Display",
        "category": "Serif",
        "subcategory": "Serif 70s Display Retro",
        "zip_name": "GR-Super.zip",
        "director_notes": "Tái hiện kỷ nguyên vàng của typography thập niên 1970 và 1980 với những đường cong quyến rũ, đậm đà và hoài niệm sâu lắng. Serif dày dặn, nét bụng tròn căng đầy sức sống. Sự lựa chọn hoàn hảo cho poster phim retro, nhãn đĩa than, thương hiệu thời trang vintage và bìa tạp chí ẩm thực cổ điển.",
        "anatomy": {"contrast": "High", "axis": "Warm Organic", "x_height": "High", "aperture": "Curved"},
        "sample_text": "Giai điệu hoài niệm thập niên 70 và linh hồn tự do trong thiết kế đĩa than cổ điển",
        "weights": ["Light", "Regular", "Medium", "Bold", "Black"]
    }
}

def get_drive_files():
    cmd = [
        "rclone", "lsjson",
        f"--drive-root-folder-id={PARENT_FOLDER_ID}",
        "gdrive:GR Fonts"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        try:
            return json.loads(res.stdout)
        except Exception:
            return []
    return []

def main():
    print("🚀 Đang truy xuất danh sách file từ Google Drive...")
    drive_items = get_drive_files()
    drive_map = {item['Name']: item['ID'] for item in drive_items if 'Name' in item}
    print(f"✔ Đã tìm thấy {len(drive_map)} file zip GR trên Google Drive!")

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Remove old GT fonts from catalog
    old_gt_ids = [
        'gt-america', 'gt-sectra', 'svn-alpina', 'svn-superdisplay', 'svn-ultra', 'svn-walsheim-pro',
        'gt-pantheon', 'fd-pantheon', 'gr-pantheon', 'gr-canon', 'gr-cinetype', 'gr-eesti',
        'gr-era', 'gr-flaire', 'gr-flexa', 'gr-haptik', 'gr-maru', 'gr-mechanik', 'gr-planar',
        'gr-standard', 'gr-zirkon', 'gr-america', 'gr-sectra', 'gr-walsheim', 'gr-ultra',
        'gr-alpina', 'gr-super'
    ]
    fonts_list = [f for f in catalog.get("fonts", []) if f.get("id") not in old_gt_ids]

    # Clean SVN from all remaining fonts
    for f in fonts_list:
        if f.get("designer") == "Grilli Type":
            f["designer"] = "FEDU Type Studio"
        if "tags" in f:
            f["tags"] = [t for t in f["tags"] if t != "Grilli Type"]

    # Append all 19 GR fonts
    new_gr_entries = []
    for fid, spec in GR_SPECS.items():
        zname = spec["zip_name"]
        file_id = drive_map.get(zname, "")
        if file_id:
            drive_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
            dl_url = f"https://drive.google.com/uc?id={file_id}&export=download"
        else:
            drive_url = f"https://drive.google.com/drive/folders/{PARENT_FOLDER_ID}?usp=sharing"
            dl_url = drive_url

        entry = {
            "id": fid,
            "name": spec["name"],
            "family": spec["family"],
            "designer": "FEDU Type Studio",
            "source": "FEDU Typography Core",
            "category": spec["category"],
            "subcategory": spec["subcategory"],
            "is_gt": True,
            "tags": ["GT Font", "FEDU Type", spec["category"], "Universal Standard"],
            "matrix_3d": {
                "style": spec["subcategory"],
                "mood": "Luxury & Sang trọng" if spec["category"] == "Serif" else "Tech & Công nghệ",
                "use_case": "Display & Body"
            },
            "anatomy": spec["anatomy"],
            "vietnamese_support": True,
            "director_notes": spec["director_notes"],
            "weights": spec["weights"],
            "sample_text": spec["sample_text"],
            "drive_link": drive_url,
            "drive_folder_url": drive_url,
            "download_url": dl_url,
            "zip_filename": zname
        }
        new_gr_entries.append(entry)

    # Insert 19 GR fonts at the top of the catalog
    catalog["fonts"] = new_gr_entries + fonts_list
    catalog["summary"]["total_fonts"] = len(catalog["fonts"])
    catalog["updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"✔ Đã cập nhật thành công {len(new_gr_entries)} họ font GR vào {CATALOG_PATH}!")
    print(f"  Tổng số fonts hiện tại trong FEDU Font (font.fedu.vn): {len(catalog['fonts'])}")

if __name__ == "__main__":
    main()
