import json

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

bold_pool = [
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
]

bold_text = " ".join(bold_pool)
missing_upper = [ch for ch in VIETNAMESE_UPPERCASE if ch not in bold_text]
print("Missing upper in 10 bold sentences:", missing_upper)
