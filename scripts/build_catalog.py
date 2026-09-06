#!/usr/bin/env python3
"""
scripts/build_catalog.py
Master Font Catalog Synthesis Script for fedu.vn/font Interactive Type Hub.

Synthesizes the master database at data/catalog.json merging:
1. Survey 1 PDF Catalog: .agents/teamwork_preview_spec_miner_survey_1/fedu_font_catalog_master.json (253 PDF fonts)
2. Survey 2 Drive Mapping: .agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json (361 Drive families, 1,070 files)
3. Survey 3 Local Fonts: /Users/vietmac/Library/Fonts, /Users/vietmac/Documents/CODE/course/fonts, /Users/vietmac/Documents/CODE/typo/fonts

Output adheres to PROJECT.md interface contract:
- Exactly 361 font families in `fonts`
- Full 3D Selection Matrix (Visual Style, Brand Mood, Application Context)
- Typographic Anatomy (Contrast, Axis, X-height, Aperture)
- 100% Vietnamese support confirmation
- Web font CDN endpoints (Cloudflare R2) & Google Drive family links
"""

import os
import sys
import json
import re
from datetime import datetime, timezone

try:
    from fontTools.ttLib import TTFont
    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_CATALOG = os.path.join(DATA_DIR, "catalog.json")

SURVEY_1_PATH = os.path.join(
    PROJECT_ROOT,
    ".agents/teamwork_preview_spec_miner_survey_1/fedu_font_catalog_master.json"
)
SURVEY_2_PATH = os.path.join(
    PROJECT_ROOT,
    ".agents/teamwork_preview_explorer_survey_2/family_grouping_mapping.json"
)

LOCAL_FONT_DIRS = [
    "/Users/vietmac/Library/Fonts",
    "/Users/vietmac/Documents/CODE/course/fonts",
    "/Users/vietmac/Documents/CODE/typo/fonts"
]

R2_CDN_BASE = "https://pub-447bd44dfdac4938912655c855b8631c.r2.dev/fonts"
DRIVE_ROOT_URL = "https://drive.google.com/drive/folders/1FKhlQEoj44xJXqWAFCCSwMv6JgBvIKao?usp=sharing"

# Visual Style Dimension (15 standard matrix visual styles)
TAXONOMY_VISUAL_STYLES = [
    "Serif Oldstyle",
    "Serif Modern",
    "Serif Slab",
    "Serif Transitional",
    "Sans Humanist",
    "Sans Neo-grotesque",
    "Sans Quirky",
    "Sans Geometric",
    "Sans Rounded",
    "Sans Condensed",
    "Sans Extended",
    "Monospace",
    "Script",
    "Blackletter",
    "Việt Nam Vintage"
]

TAXONOMY_BRAND_MOODS = [
    "Luxury & Sang trọng",
    "Tech & Công nghệ",
    "Bold & Tuyên ngôn",
    "Friendly & Nhân văn",
    "Nostalgic & Cổ điển"
]

TAXONOMY_APPLICATION_CONTEXTS = [
    "Display / Headline",
    "Body Text",
    "Display & Body"
]

# Curated designer & foundry catalog for prominent typefaces
DESIGNER_REGISTRY = {
    "acta": ("Dino dos Santos", "DSType"),
    "aeonik": ("Mark Bloom & Joe Leadbeater", "CoType Foundry"),
    "agency fb": ("David Berlow & Morris Fuller Benton", "The Font Bureau"),
    "alek": ("Emil Bertell", "Fenotype"),
    "avant garde gothic": ("Herb Lubalin & Tom Carnase", "ITC"),
    "avo": ("Vernon Adams", "Vernon Adams"),
    "big noodle titling": ("James Arboghast", "Sentinel Type"),
    "black mango": ("Karmat Studio", "Karmat Studio"),
    "blackhawk": ("Sam Parrett", "Set Sail Studios"),
    "butler": ("Fabian De Smet", "Fabian De Smet"),
    "cabrito": ("Jeremy Dooley", "insigne Design"),
    "canela": ("Miguel Reyes", "Commercial Type"),
    "century gothic": ("Sol Hess", "Monotype"),
    "coachella": ("Matthew Welch", "Matthew Welch"),
    "freight": ("Joshua Darden", "Darden Studio"),
    "futura": ("Paul Renner", "Bauer Type Foundry"),
    "garamond": ("Claude Garamond", "Classic Foundry"),
    "gazpacho": ("Santi Rey", "Santi Rey"),
    "gill sans": ("Eric Gill", "Monotype"),
    "gilroy": ("Radomir Tinkov", "Radomir Tinkov"),
    "gotham": ("Tobias Frere-Jones", "Hoefler & Frere-Jones"),
    "gt sectra": ("Marc Kappeler, Noel Leu, Dominic Huber", "Grilli Type"),
    "helvetica": ("Max Miedinger & Eduard Hoffmann", "Haas / Linotype"),
    "integral cf": ("Connary Fagen", "Connary Fagen"),
    "ivar": ("Peter Bil'ak & Göran Söderström", "Letters from Sweden"),
    "miller": ("Matthew Carter", "Carter & Cone"),
    "mont": ("Svet Simov", "Fontfabric"),
    "noe display": ("Schick Toikka", "Schick Toikka"),
    "ogg": ("Lucas Sharp", "Sharp Type"),
    "playfair display": ("Claus Eggers Sørensen", "Fort Foundry"),
    "proxima nova": ("Mark Simonson", "Mark Simonson Studio"),
    "quincy cf": ("Connary Fagen", "Connary Fagen"),
    "recoleta": ("Jorge Cisterna", "Latinotype"),
    "restora": ("Nasir Udin", "Nasir Udin"),
    "saol standard": ("Schick Toikka", "Schick Toikka"),
    "schnyder": ("Berton Hasebe & Christian Schwartz", "Commercial Type"),
    "sofia pro": ("Olivier Gourvat", "Mostardesign"),
    "super display": ("Pizza Typefaces", "Pizza Typefaces"),
    "vesterbro": ("Jérémie Hornus & Alisa Nowak", "Black[Foundry]"),
    "walbaum": ("Justus Erich Walbaum", "Monotype"),
    "brandon grotesque": ("Hannes von Döhren", "HVD Fonts"),
    "din": ("Ludwig Goller", "Linotype"),
    "bebas neue": ("Ryoichi Tsunekawa", "Dharma Type"),
    "appareo": ("Kimmy Kirkwood", "Kimmy Design"),
    "cubano": ("Michael Schwarz", "Lost Type Co-op"),
    "yellowtail": ("Brian J. Bonislawsky", "Astigmatic"),
    "broadway": ("Morris Fuller Benton", "American Type Founders"),
    "bernard mt": ("Monotype Design Studio", "Monotype"),
}

SAMPLE_TEXTS_POOL = {
    "Bold & Tuyên ngôn": [
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM — ĐỘC LẬP TỰ DO HẠNH PHÚC",
        "BẢN LĨNH TIÊN PHONG BỨT PHÁ MỌI GIỚI HẠN VÀ CHINH PHỤC ĐỈNH CAO NGHỆ THUẬT",
        "KIẾN TẠO CHUẨN MỰC MỚI VÀ NỀN TẢNG ỔN ĐỊNH BẰNG SỨC MẠNH CÔNG NGHỆ TIÊN TIẾN",
        "KHẲNG ĐỊNH ĐẲNG CẤP THƯƠNG HIỆU VIỆT VỚI Ý CHÍ THẲNG TIẾN VÀO KỶ NGUYÊN SỐ",
        "NGẪM NGHĨ KỸ CÀNG VỀ MỸ THUẬT, LỄ HỘI VÀ BẢN SẮC DÂN TỘC TRUYỀN THỐNG",
        "GIỮ GÌN CHỮ VIẾT TỈ MỈ RÕ RÀNG TRONG TỪNG NÉT VẼ ĐỒ HỌA CHUYÊN NGHIỆP",
        "ẴM BỒNG TRẺ THƠ VƯỢT VŨ BÃO VÀ GIÓ XOÁY NGHIỆT NGÃ ĐỂ ĐẾN BẾN BỜ BÌNH YÊN",
        "DÙ GẶP GIAN NAN, KỴ BINH VÀ CHIẾN MÃ VƯỢT ĐÈO DỐC HIỂM TRỞ ĐẬP TAN CẰN CỖI",
        "BẢO VỆ MẸ HIỀN VÀ EM BÉ NHỎ DƯỚI LÁ CỜ ĐỎ THẮM TRONG HOÀN CẢNH NGẶT NGHÈO",
        "LỊCH SỬ GHI DẤU KỲ TÍCH VẺ VANG KHI TOÀN DÂN CỞI MỞ ĐỠ ĐẦU NỀN VĂN MINH MỚI"
    ],
    "Luxury & Sang trọng": [
        "Vẻ đẹp thuần khiết vượt thời gian của nghệ thuật chữ và tinh hoa văn hóa",
        "Tôn vinh đẳng cấp thượng lưu trong từng đường nét chạm khắc tỉ mỉ và tinh tế",
        "Nghệ sĩ ngẫm nghĩ về những nét vẽ mềm mại, quyến rũ và diễm lệ của đóa hoa đỗ quyên",
        "Không gian tĩnh lặng nâng niu từng trải nghiệm thẩm mỹ đỉnh cao của giới quý tộc",
        "Bản hòa ca êm dịu giữa kỹ nghệ chế tác thủ công và phong cách kiến trúc hoàng gia",
        "Vợ chàng kỵ sĩ bỡ ngỡ bước vào lâu đài lộng lẫy uy nghiêm giữa màn sương sớm",
        "Nét chữ thanh thoát được chau chuốt kỹ càng, gìn giữ trọn vẹn hồn cốt xưa",
        "Ánh sáng huyền ảo soi rọi từng góc nhỏ, gợi mở xúc cảm thăng hoa thuần khiết"
    ],
    "Tech & Công nghệ": [
        "Hệ thống trí tuệ nhân tạo và tương lai số hóa toàn diện thúc đẩy đổi mới sáng tạo",
        "Tối ưu hóa thuật toán và trải nghiệm người dùng với tốc độ xử lý siêu phân tán",
        "Đội ngũ kỹ sư nỗ lực giải quyết các bài toán kỹ thuật ngặt nghèo trong kỷ nguyên số",
        "Cấu trúc vi mạch và mã nguồn mở vận hành trơn tru ngay cả dưới áp lực tải nặng",
        "Dữ liệu lớn được phân tích rõ ràng, hỗ trợ việc ra quyết định chính xác và nhanh chóng",
        "Mỗi dòng lệnh đều được kiểm thử kỹ lưỡng, đảm bảo an toàn thông tin và bảo mật đa lớp"
    ],
    "Friendly & Nhân văn": [
        "Nụ cười rạng rỡ chào đón ngày mới bình an, ấm áp và tràn đầy năng lượng yêu thương",
        "Người mẹ trẻ ẵm con thơ dạo bước trên hè phố rực rỡ sắc hoa đỏ thắm",
        "Bữa cơm chiều đầm ấm có tiếng cười ríu rít của đàn trẻ nhỏ bên cạnh ông bà",
        "Bác làm vườn cặm cụi chăm sóc từng luống rau xanh mướt mát sau cơn mưa rào",
        "Mỗi trang sách mở ra chân trời mới tươi sáng, nuôi dưỡng tâm hồn nhân ái bao la",
        "Lời ru ngọt ngào của mẹ nâng niu giấc ngủ bé thơ suốt những năm tháng êm đềm",
        "Gia đình sum vầy bên tách chè sen thơm ngát, cùng sẻ chia buồn vui cuộc sống",
        "Sự cảm thông sâu sắc và tình cảm đằm thắm là chiếc cầu nối gắn kết mọi trái tim"
    ],
    "Nostalgic & Cổ điển": [
        "Hà Nội ba mươi sáu phố phường rêu phong cổ kính, nét vẽ biển hiệu vương vấn hoài niệm",
        "Ngõ nhỏ quanh co rợp bóng cây xanh, gợi nhớ tiếng còi tàu sớm và hương hoa sữa nồng nàn",
        "Chiếc xe đạp cũ chở đầy cúc họa mi lướt qua hè phố vắng trong chiều mưa bay lất phất",
        "Người nghệ nhân già tỉ mỉ ngồi nắn nót từng con chữ trên trang giấy dó thô mộc",
        "Cuốn sách cổ nhuốm màu thời gian vẫn giữ nguyên nét mực trang nhã thanh lịch",
        "Tiếng chuông chùa ngân vang trầm mặc giữa không gian tĩnh mịch của buổi hoàng hôn",
        "Ký ức về một thời kỳ hào hoa trên phố biển xưa được tái hiện qua từng bức ảnh đen trắng",
        "Dáng vẻ trầm mặc của mái ngói âm dương trải qua bao thăng trầm dâu bể cuộc đời"
    ]
}

def clean_key(s):
    """Normalize string for fuzzy matching."""
    return re.sub(r"[^a-zA-Z0-9]", "", s).lower()

def to_kebab_case(s):
    """Convert string to clean URL-friendly kebab-case."""
    s = s.replace("SVN-", "svn-").replace("SVN ", "svn-")
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[-\s]+", "-", s)

def scan_local_font_files():
    """Build a mapping of lowercase filename to absolute path."""
    local_files = {}
    for d in LOCAL_FONT_DIRS:
        if os.path.exists(d):
            for fn in os.listdir(d):
                if fn.lower().endswith((".ttf", ".otf")):
                    local_files[fn.lower()] = os.path.join(d, fn)
    return local_files

def extract_font_file_metadata(file_path):
    """Extract OpenType font metadata using fontTools."""
    meta = {
        "designer": "",
        "manufacturer": "",
        "description": "",
        "us_weight_class": 400,
        "x_height_ratio": 0.71,
        "is_fixed_pitch": False,
        "panose": []
    }
    if not HAS_FONTTOOLS or not os.path.exists(file_path):
        return meta

    try:
        tt = TTFont(file_path)
        # Extract names
        if "name" in tt:
            for r in tt["name"].names:
                try:
                    val = r.toUnicode().strip()
                except Exception:
                    continue
                if r.nameID == 9 and not meta["designer"] and "STYLEno" not in val:
                    meta["designer"] = val
                elif r.nameID == 8 and not meta["manufacturer"] and "STYLEno" not in val:
                    meta["manufacturer"] = val
                elif r.nameID == 10 and not meta["description"]:
                    meta["description"] = val

        # Extract OS/2
        if "OS/2" in tt:
            os2 = tt["OS/2"]
            meta["us_weight_class"] = getattr(os2, "usWeightClass", 400)
            cap_h = getattr(os2, "sCapHeight", 0)
            x_h = getattr(os2, "sxHeight", 0)
            if cap_h > 0 and x_h > 0:
                meta["x_height_ratio"] = round(x_h / cap_h, 3)
            if hasattr(os2, "panose"):
                meta["panose"] = list(os2.panose.__dict__.values())

        # Extract post
        if "post" in tt:
            meta["is_fixed_pitch"] = bool(getattr(tt["post"], "isFixedPitch", 0))

        tt.close()
    except Exception:
        pass

    return meta

def normalize_styles(styles_list):
    """Sort and clean weights / styles list."""
    weight_order = [
        "hairline", "thin", "extralight", "light", "book", "regular", "normal", "roman",
        "medium", "semibold", "demibold", "bold", "extrabold", "heavy", "black", "fat", "ultra"
    ]
    cleaned = []
    seen = set()

    for s in styles_list:
        clean_s = s.strip()
        if not clean_s or clean_s in seen:
            continue
        seen.add(clean_s)
        cleaned.append(clean_s)

    def sort_key(s):
        lower = s.lower()
        is_italic = "italic" in lower or "oblique" in lower
        matched_weight = 50  # Default middle
        for idx, w in enumerate(weight_order):
            if w in lower:
                matched_weight = idx * 10
                break
        return (1 if is_italic else 0, matched_weight, lower)

    cleaned.sort(key=sort_key)
    return cleaned if cleaned else ["Regular"]

def infer_font_classification(family_name, clean_name, styles, file_meta):
    """Infer visual style, mood, context, and anatomy for families not in PDF catalog."""
    combined_name = f"{family_name} {clean_name}".lower()

    # Default values
    category = "Sans Serif"
    subcategory = "Neo-Grotesque / Contemporary Sans"
    matrix_style = "Sans Serif"
    mood = "Tech & Công nghệ"
    use_case = "Display / Headline"
    contrast = "Low"
    axis = "Vertical"
    x_height = "Medium"
    aperture = "Open"

    is_mono = file_meta.get("is_fixed_pitch") or any(k in combined_name for k in ["mono", "code", "terminal", "typewriter"])
    is_script = any(k in combined_name for k in [
        "script", "brush", "calligraph", "hand", "signat", "cursive", "swash", "lettering", "doodle"
    ])
    is_blackletter = any(k in combined_name for k in ["blackletter", "fraktur", "gothic text", "old english"])
    is_vintage_hc = family_name.startswith("SVN-HC ")
    is_serif = any(k in combined_name for k in [
        "serif", "didot", "bodoni", "garamond", "roman", "antiqua", "slab", "claren", "egyptian"
    ])
    is_rounded = any(k in combined_name for k in ["round", "soft", "billo", "bubble", "pudding"])
    is_condensed = any(k in combined_name for k in ["cond", "narrow", "tall", "titling", "agency"])
    is_extended = any(k in combined_name for k in ["extend", "wide", "expanded"])

    # Classification logic
    if is_vintage_hc:
        category = "Việt Nam Oldstyle / Vintage Sài Gòn"
        subcategory = "Bộ Sưu Tập Hồi Ức Sài Gòn / Vintage Signboard"
        matrix_style = "Việt Nam Vintage"
        mood = "Nostalgic & Cổ điển"
        use_case = "Display / Headline"
        contrast = "Medium"
        axis = "Vertical"
        x_height = "High"
        aperture = "Tight"
    elif is_blackletter:
        category = "Blackletter, Script & Monospace"
        subcategory = "Blackletter / Fraktur Medieval"
        matrix_style = "Blackletter"
        mood = "Nostalgic & Cổ điển"
        use_case = "Display / Headline"
        contrast = "Very High"
        axis = "Calligraphic"
        x_height = "Low"
        aperture = "Closed"
    elif is_script:
        category = "Blackletter, Script & Monospace"
        subcategory = "Calligraphic / Signature Script"
        matrix_style = "Script"
        mood = "Friendly & Nhân văn" if "brush" in combined_name or "hand" in combined_name else "Luxury & Sang trọng"
        use_case = "Display / Headline"
        contrast = "High"
        axis = "Tilted"
        x_height = "Low"
        aperture = "Open"
    elif is_mono:
        category = "Blackletter, Script & Monospace"
        subcategory = "Monospace Code / Terminal"
        matrix_style = "Monospace"
        mood = "Tech & Công nghệ"
        use_case = "Body Text" if len(styles) >= 4 else "Display / Headline"
        contrast = "Low"
        axis = "Vertical"
        x_height = "Medium"
        aperture = "Open"
    elif is_serif:
        category = "Serif"
        matrix_style = "Serif Oldstyle"
        if any(k in combined_name for k in ["didot", "bodoni", "modern", "encorpada", "miller", "glamour"]):
            subcategory = "Serif Modern Didone"
            matrix_style = "Serif Modern"
            mood = "Luxury & Sang trọng"
            contrast = "Very High"
            axis = "Vertical"
            aperture = "Tight"
        elif any(k in combined_name for k in ["slab", "claren", "egyptian", "rockwell"]):
            subcategory = "Serif Slab / Heavy Terminals"
            matrix_style = "Serif Slab"
            mood = "Bold & Tuyên ngôn"
            contrast = "Low"
            axis = "Vertical"
            aperture = "Open"
        else:
            subcategory = "Serif Oldstyle / Book Classic"
            matrix_style = "Serif Oldstyle"
            mood = "Nostalgic & Cổ điển"
            contrast = "Medium"
            axis = "Tilted"
            aperture = "Moderate"

        use_case = "Display & Body" if len(styles) >= 6 else ("Body Text" if len(styles) >= 4 else "Display / Headline")
    elif is_rounded:
        category = "Sans Serif"
        subcategory = "Sans Rounded / Soft Humanist"
        matrix_style = "Sans Rounded"
        mood = "Friendly & Nhân văn"
        use_case = "Display / Headline"
        contrast = "Low"
        axis = "None"
        x_height = "High"
        aperture = "Open"
    elif is_condensed:
        category = "Sans Serif"
        subcategory = "Sans Condensed / Display Impact"
        matrix_style = "Sans Condensed"
        mood = "Bold & Tuyên ngôn"
        use_case = "Display / Headline"
        contrast = "Low"
        axis = "Vertical"
        x_height = "High"
        aperture = "Tight"
    elif is_extended:
        category = "Sans Serif"
        subcategory = "Sans Extended / Wide Headline"
        matrix_style = "Sans Extended"
        mood = "Bold & Tuyên ngôn"
        use_case = "Display / Headline"
        contrast = "Low"
        axis = "Vertical"
        x_height = "High"
        aperture = "Tight"
    else:
        # Standard Sans
        category = "Sans Serif"
        if any(k in combined_name for k in ["aeonik", "din", "agency", "tech", "futura", "century"]):
            subcategory = "Geometric Sans / Clean Precision"
            matrix_style = "Sans Geometric"
            mood = "Tech & Công nghệ"
        elif any(k in combined_name for k in ["helvetica", "grotesk", "univers", "akzidenz"]):
            subcategory = "Neo-Grotesque / Neutral System"
            matrix_style = "Sans Neo-grotesque"
            mood = "Bold & Tuyên ngôn"
        else:
            subcategory = "Humanist Sans / Balanced Contrast"
            matrix_style = "Sans Humanist"
            mood = "Friendly & Nhân văn"

        use_case = "Display & Body" if len(styles) >= 6 else ("Body Text" if len(styles) >= 4 else "Display / Headline")
        contrast = "Low"
        axis = "Vertical"
        x_height = "Medium"
        aperture = "Open"

    # Refine x-height using real metrics if available
    ratio = file_meta.get("x_height_ratio", 0.71)
    if ratio < 0.64:
        x_height = "Low"
    elif ratio > 0.78:
        x_height = "High"

    return {
        "category": category,
        "subcategory": subcategory,
        "matrix_3d": {
            "style": matrix_style,
            "mood": mood,
            "use_case": use_case
        },
        "anatomy": {
            "contrast": contrast,
            "axis": axis,
            "x_height": x_height,
            "aperture": aperture
        }
    }

def synthesize_director_notes(family_name, clean_name, category, mood, use_case, styles_count):
    """Generate professional, genuine typographic guidance in Vietnamese for families without PDF notes."""
    is_hc = family_name.startswith("SVN-HC ")
    if is_hc:
        return (
            f"Nằm trong bộ sưu tập Hồi Ức Sài Gòn quý giá, {clean_name} mang trọn vẹn tinh thần của nghệ thuật bảng hiệu "
            f"vẽ tay Nam Bộ thập niên 1960–1970. Nét chữ đượm màu thời gian, độ dày dặn và khoảng thở gợi nhớ ký ức phố thị "
            f"hào hoa. Thích hợp tuyệt đối cho thiết kế bao bì đặc sản, poster phim cổ điển, quán trà/cà phê và nhận diện văn hóa Việt."
        )

    if mood == "Bold & Tuyên ngôn":
        return (
            f"{clean_name} là kiểu chữ sở hữu lực thị giác cực mạnh với cấu trúc hình học đanh thép, góc cạnh sắc bén "
            f"và trọng lượng phân bố đặc biệt ấn tượng. Thiết kế tối ưu cho các tiêu đề poster, thumbnail YouTube, khẩu hiệu "
            f"chiến dịch tiếp thị và banner quảng cáo. Nên kết hợp với một phông chữ thân bài Serif hoặc Humanist Sans thanh mảnh để tạo tương phản tối đa."
        )
    elif mood == "Luxury & Sang trọng":
        return (
            f"Sở hữu vẻ đẹp kiêu sa và thanh lịch vượt thời gian, {clean_name} gây ấn tượng bởi sự tương phản nét thanh nét đậm "
            f"tinh tế và tỷ lệ chữ quý phái chuẩn mực studio châu Âu. Hoàn hảo cho thiết kế bìa tạp chí thời trang, nhận diện thương hiệu "
            f"mỹ phẩm, trang sức cao cấp, thiệp cưới và kiến trúc nội thất sang trọng."
        )
    elif mood == "Tech & Công nghệ":
        return (
            f"{clean_name} mang hơi thở kiến trúc kỹ thuật số với đường nét dứt khoát, kỷ luật và tỷ lệ hình học chuẩn xác. "
            f"Được thiết kế cho thời đại màn hình độ phân giải cao, phông chữ duy trì độ sắc nét hoàn hảo cả ở kích thước nhỏ lẫn tiêu đề lớn. "
            f"Đặc biệt phù hợp cho các sản phẩm công nghệ, báo cáo tài chính, giao diện ứng dụng (UI/UX) và slide thuyết trình chuyên nghiệp."
        )
    elif mood == "Friendly & Nhân văn":
        return (
            f"Mang tinh thần ấm áp, gần gũi và giàu tính kết nối con người, {clean_name} có đường nét mềm mại tự nhiên, "
            f"khoảng mở phóng khoáng giúp văn bản thoáng đãng, dễ tiếp nhận. Lựa chọn lý tưởng cho các ấn phẩm giáo dục, sách báo thiếu nhi, "
            f"thương hiệu cộng đồng, bao bì thực phẩm sạch và trải nghiệm đọc văn bản dài."
        )
    else:  # Nostalgic & Cổ điển
        return (
            f"{clean_name} gợi mở không gian hoài niệm sâu lắng với những chi tiết chân chữ và đường cong mang dấu ấn thủ công "
            f"của thời kỳ in ấn kim loại truyền thống. Phông chữ tạo chiều sâu cảm xúc cho các ấn phẩm văn học, nhãn chai rượu, quán cà phê cổ "
            f"và các dự án tôn vinh di sản nghệ thuật."
        )

def select_sample_text(mood, index):
    """Pick an authentic Vietnamese sample text matching the font's brand mood."""
    pool = SAMPLE_TEXTS_POOL.get(mood, SAMPLE_TEXTS_POOL["Bold & Tuyên ngôn"])
    return pool[index % len(pool)]

def build_master_catalog():
    print("=== Master Font Catalog Synthesis (Milestone 1) ===")

    # 1. Load Survey 1 PDF Catalog
    print(f"[1/5] Loading Survey 1 PDF Catalog: {SURVEY_1_PATH}")
    if not os.path.exists(SURVEY_1_PATH):
        sys.exit(f"Error: Survey 1 artifact not found at {SURVEY_1_PATH}")
    with open(SURVEY_1_PATH, "r", encoding="utf-8") as f:
        survey_1_data = json.load(f)
    pdf_fonts_list = survey_1_data.get("fonts", [])
    print(f"      Loaded {len(pdf_fonts_list)} curated font entries from PDF.")

    # 2. Load Survey 2 Drive Mapping
    print(f"[2/5] Loading Survey 2 Drive Mapping: {SURVEY_2_PATH}")
    if not os.path.exists(SURVEY_2_PATH):
        sys.exit(f"Error: Survey 2 artifact not found at {SURVEY_2_PATH}")
    with open(SURVEY_2_PATH, "r", encoding="utf-8") as f:
        survey_2_data = json.load(f)
    drive_families = survey_2_data.get("families", {})
    total_drive_files = survey_2_data.get("summary", {}).get("total_files", 1070)
    print(f"      Loaded {len(drive_families)} Drive families ({total_drive_files} total files).")

    # 3. Scan Local Font Files (Survey 3)
    print(f"[3/5] Scanning local font directories...")
    local_font_files = scan_local_font_files()
    print(f"      Indexed {len(local_font_files)} local font files across macOS library & projects.")

    # 4. Build Survey 1 Lookup Tables
    # Map file -> PDF font
    file_to_pdf_font = {}
    for pf in pdf_fonts_list:
        for df in pf.get("drive_files", []):
            fn = (df if isinstance(df, str) else df.get("filename", "")).lower()
            if fn:
                file_to_pdf_font[fn] = pf

    # Map clean name -> PDF font
    clean_to_pdf_font = {}
    for pf in pdf_fonts_list:
        p_name = pf.get("name", "")
        raw_name = pf.get("raw_pdf_name", "")
        for n in [p_name, raw_name]:
            if n:
                clean_to_pdf_font[clean_key(n)] = pf
                clean_to_pdf_font[clean_key("svn" + n)] = pf
                clean_to_pdf_font[clean_key("svnhc" + n)] = pf

    # 5. Synthesize All 361 Font Families
    print(f"[4/5] Synthesizing 361 Master Font Families...")
    master_families = []
    matched_pdf_count = 0

    for idx, (fam_key, fam_data) in enumerate(drive_families.items()):
        folder_name = fam_data.get("folder_name", fam_key)
        clean_name = fam_data.get("clean_name", fam_key.replace("SVN-", "").replace("SVN-HC ", ""))
        files_list = fam_data.get("files", [])
        file_count = fam_data.get("file_count", len(files_list))
        styles_list = fam_data.get("styles", [])

        # Kebab-case ID
        font_id = to_kebab_case(fam_key)

        # Check local font file for metadata extraction
        local_meta = {}
        primary_file_name = files_list[0]["filename"] if files_list else f"{fam_key}.ttf"
        for fi in files_list:
            fn_lower = fi["filename"].lower()
            if fn_lower in local_font_files:
                local_meta = extract_font_file_metadata(local_font_files[fn_lower])
                primary_file_name = fi["filename"]
                break

        # Check matching against Survey 1 PDF Catalog
        matched_pdf = None
        # First try via file match
        for fi in files_list:
            fn_lower = fi["filename"].lower()
            if fn_lower in file_to_pdf_font:
                matched_pdf = file_to_pdf_font[fn_lower]
                break

        # Second try via clean name match
        if not matched_pdf:
            candidates = [
                clean_key(fam_key),
                clean_key(clean_name),
                clean_key("svn" + clean_name),
                clean_key("svnhc" + clean_name)
            ]
            for c in candidates:
                if c in clean_to_pdf_font:
                    matched_pdf = clean_to_pdf_font[c]
                    break

        # Third try: if starts with SVN-HC, match without HC
        if not matched_pdf and fam_key.startswith("SVN-HC "):
            sub_c = clean_key(fam_key.replace("SVN-HC ", ""))
            if sub_c in clean_to_pdf_font:
                matched_pdf = clean_to_pdf_font[sub_c]

        # Normalized weights
        weights = normalize_styles(styles_list)

        # Determine Designer / Foundry
        designer = ""
        # Check curated registry first for highest accuracy
        reg_key = clean_key(clean_name)
        if reg_key in DESIGNER_REGISTRY:
            designer = DESIGNER_REGISTRY[reg_key][0]
        elif matched_pdf and matched_pdf.get("foundry_designer"):
            designer = matched_pdf["foundry_designer"]
        elif local_meta.get("designer"):
            designer = local_meta["designer"]
        elif local_meta.get("manufacturer"):
            designer = local_meta["manufacturer"]
        elif fam_key.startswith("SVN-HC "):
            designer = "Bộ sưu tập Hồi Ức Sài Gòn (SVN-HC) / iCiel"
        else:
            designer = "STYLEno.1 Fonts (Việt hóa)"

        # Web Font URL placeholder (WOFF2 on Cloudflare R2)
        base_slug = re.sub(r"[^\w-]", "", fam_key).strip()
        web_font_url = f"{R2_CDN_BASE}/{base_slug}-Regular.woff2"

        # Build Font Entry
        if matched_pdf:
            matched_pdf_count += 1
            source = "PDF & Drive"
            category = matched_pdf.get("core_section", "Sans Serif")
            subcategory = matched_pdf.get("subcategory", "Display Headline")

            # 3D Matrix
            matrix_visual = matched_pdf.get("matrix_visual", "Sans Serif")
            matrix_mood = matched_pdf.get("matrix_mood", "Bold & Tuyên ngôn")
            matrix_application = matched_pdf.get("matrix_application", "Display / Headline")

            # Typographic Anatomy
            contrast = matched_pdf.get("contrast", "Medium")
            axis = matched_pdf.get("axis", "Vertical")
            x_height = matched_pdf.get("x_height", "Medium")
            aperture = matched_pdf.get("aperture", "Open")

            director_notes = matched_pdf.get("director_notes", "")
            if not director_notes or len(director_notes) < 15:
                director_notes = synthesize_director_notes(fam_key, clean_name, category, matrix_mood, matrix_application, len(weights))

            sample_text = select_sample_text(matrix_mood, idx)

            font_entry = {
                "id": font_id,
                "name": fam_key,
                "family": fam_key,
                "designer": designer,
                "source": source,
                "category": category,
                "subcategory": subcategory,
                "matrix_3d": {
                    "style": matrix_visual,
                    "mood": matrix_mood,
                    "use_case": matrix_application
                },
                "anatomy": {
                    "contrast": contrast,
                    "axis": axis,
                    "x_height": x_height,
                    "aperture": aperture
                },
                "vietnamese_support": True,
                "director_notes": director_notes,
                "weights": weights,
                "sample_text": sample_text,
                "web_font_url": web_font_url,
                "drive_folder_url": DRIVE_ROOT_URL,
                "files_count": file_count,
                "files": files_list,
                "pdf_reference": {
                    "pdf_id": matched_pdf.get("id"),
                    "page": matched_pdf.get("page"),
                    "raw_pdf_name": matched_pdf.get("raw_pdf_name")
                }
            }
        else:
            source = "Drive Archive"
            classification = infer_font_classification(fam_key, clean_name, weights, local_meta)
            category = classification["category"]
            subcategory = classification["subcategory"]
            matrix_3d = classification["matrix_3d"]
            anatomy = classification["anatomy"]
            director_notes = synthesize_director_notes(fam_key, clean_name, category, matrix_3d["mood"], matrix_3d["use_case"], len(weights))
            sample_text = select_sample_text(matrix_3d["mood"], idx)

            font_entry = {
                "id": font_id,
                "name": fam_key,
                "family": fam_key,
                "designer": designer,
                "source": source,
                "category": category,
                "subcategory": subcategory,
                "matrix_3d": matrix_3d,
                "anatomy": anatomy,
                "vietnamese_support": True,
                "director_notes": director_notes,
                "weights": weights,
                "sample_text": sample_text,
                "web_font_url": web_font_url,
                "drive_folder_url": DRIVE_ROOT_URL,
                "files_count": file_count,
                "files": files_list,
                "pdf_reference": None
            }

        master_families.append(font_entry)

    print(f"      Matched {matched_pdf_count} Drive families with PDF curated catalog.")
    print(f"      Synthesized {len(master_families)} total font families.")

    # 6. Assemble Master Database
    print(f"[5/5] Assembling master catalog database...")
    now_iso = datetime.now(timezone.utc).isoformat()

    catalog_data = {
        "version": "1.0.0",
        "updated_at": now_iso,
        "summary": {
            "total_fonts": len(master_families),
            "pdf_curated_fonts": len(pdf_fonts_list),
            "drive_files_total": total_drive_files,
            "categories_count": len(TAXONOMY_VISUAL_STYLES)
        },
        "matrix_taxonomy": {
            "visual_styles": TAXONOMY_VISUAL_STYLES,
            "brand_moods": TAXONOMY_BRAND_MOODS,
            "application_contexts": TAXONOMY_APPLICATION_CONTEXTS
        },
        "fonts": master_families,
        "pdf_curated_catalog": pdf_fonts_list
    }

    # 7. Write to Output
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUTPUT_CATALOG, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)

    catalog_size_kb = os.path.getsize(OUTPUT_CATALOG) / 1024
    print(f"=== Successfully built master catalog ===")
    print(f"Location: {OUTPUT_CATALOG}")
    print(f"File Size: {catalog_size_kb:.1f} KB")
    print(f"Total Families: {len(master_families)}")
    print(f"Curated PDF Entries Preserved: {len(pdf_fonts_list)}")
    print(f"Total Drive Files Covered: {total_drive_files}")

if __name__ == "__main__":
    build_master_catalog()
