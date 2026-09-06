import json

with open('/Users/vietmac/Documents/CODE/fedu-font/data/catalog.json') as f:
    cat = json.load(f)

VIETNAMESE_LOWERCASE = [
    'a', 'à', 'á', 'ả', 'ã', 'ạ',
    'ă', 'ằ', 'ắ', 'ẳ', 'ẵ', 'ặ',
    'â', 'ầ', 'ấ', 'ẩ', 'ẫ', 'ậ',
    'e', 'è', 'é', 'ẻ', 'ẽ', 'ẹ',
    'ê', 'ề', 'ế', 'ể', 'ễ', 'ệ',
    'i', 'ì', 'í', 'ỉ', 'ĩ', 'ị',
    'o', 'ò', 'ó', 'ỏ', 'õ', 'ọ',
    'ô', 'ồ', 'ố', 'ổ', 'ỗ', 'ộ',
    'ơ', 'ờ', 'ớ', 'ở', 'ỡ', 'ợ',
    'u', 'ù', 'ú', 'ủ', 'ũ', 'ụ',
    'ư', 'ừ', 'ứ', 'ử', 'ữ', 'ự',
    'y', 'ỳ', 'ý', 'ỷ', 'ỹ', 'ỵ',
    'đ'
]

VIETNAMESE_UPPERCASE = [
    'A', 'À', 'Á', 'Ả', 'Ã', 'Ạ',
    'Ă', 'Ằ', 'Ắ', 'Ẳ', 'Ẵ', 'Ặ',
    'Â', 'Ầ', 'Ấ', 'Ẩ', 'Ẫ', 'Ậ',
    'E', 'È', 'É', 'Ẻ', 'Ẽ', 'Ẹ',
    'Ê', 'Ề', 'Ế', 'Ể', 'Ễ', 'Ệ',
    'I', 'Ì', 'Í', 'Ỉ', 'Ĩ', 'Ị',
    'O', 'Ò', 'Ó', 'Ỏ', 'Õ', 'Ọ',
    'Ô', 'Ồ', 'Ố', 'Ổ', 'Ỗ', 'Ộ',
    'Ơ', 'Ờ', 'Ớ', 'Ở', 'Ỡ', 'Ợ',
    'U', 'Ù', 'Ú', 'Ủ', 'Ũ', 'Ụ',
    'Ư', 'Ừ', 'Ứ', 'Ử', 'Ữ', 'Ự',
    'Y', 'Ỳ', 'Ý', 'Ỷ', 'Ỹ', 'Ỵ',
    'Đ'
]

# Bold & Tuyên ngôn sentences in ALL-CAPS:
# We need to ensure that the chosen pool size N for Bold satisfies:
# Every uppercase letter in VIETNAMESE_UPPERCASE is in at least one sentence whose index is hit!
# Let's test pool size 8 or 10 for Bold:
# At size 8, all indices 0..7 are hit!
# So if the 8 sentences in Bold collectively contain all 73 uppercase characters, 100% of uppercase characters will be present in the 361 fonts!

bold_pool = [
    "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM — ĐỘC LẬP TỰ DO HẠNH PHÚC",
    "BẢN LĨNH TIÊN PHONG BỨT PHÁ MỌI GIỚI HẠN VÀ CHINH PHỤC ĐỈNH CAO",
    "KIẾN TẠO CHUẨN MỰC MỚI CỦA SỰ HOÀN HẢO TRONG NGHỆ THUẬT THỊ GIÁC",
    "ĐẮP XÂY KỶ NGUYÊN HÙNG CƯỜNG VÀ THỊNH VƯỢNG CHO ĐẤT NƯỚC VIỆT NAM",
    "NGẪM NGHĨ KỸ CÀNG VỀ MỸ THUẬT VÀ LỄ HỘI DÂN TỘC TRUYỀN THỐNG",
    "GIỮ GÌN CHỮ VIẾT TỈ MỈ RÕ RÀNG TRONG TỪNG NÉT VẼ ĐỒ HỌA CHUYÊN NGHIỆP",
    "ẴM BỒNG TRẺ THƠ VƯỢT QUA VŨ BÃO VÀ GIÓ XOÁY NGHIỆT NGÃ ĐỂ ĐẾN BẾN BỜ BÌNH YÊN",
    "KỴ BINH VÀ CHIẾN MÃ VƯỢT ĐÈO DỐC HIỂM TRỞ ĐẬP TAN MỌI NỖI SỢ HÃI VÀ CẰN CỖI"
]

# Let's check which uppercase characters are in bold_pool:
bold_text = " ".join(bold_pool)
missing_upper_in_bold = [ch for ch in VIETNAMESE_UPPERCASE if ch not in bold_text]
print("Missing upper in 8 bold sentences:", missing_upper_in_bold)
