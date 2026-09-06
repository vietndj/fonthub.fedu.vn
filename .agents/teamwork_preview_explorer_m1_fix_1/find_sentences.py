import json

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

# Vietnamese complete pangrams:
# Let's craft natural sentences that cover specific missing sets:
# Missing lower: 'ằ', 'ẵ', 'ặ', 'ẫ', 'e', 'è', 'ễ', 'ỉ', 'ĩ', 'ỏ', 'õ', 'ũ', 'ử', 'ỳ', 'ỹ', 'ỵ'

# Let's test a complete pangram in Vietnamese:
pangram_lower = (
    "Do bạch hồng tượng trưng cho tình yêu thảo mộc ngát hương của vợ chàng quỷ xứ, "
    "kẻ đã cởi phăng áo vét xám để bơi qua khúc sông sâu thẳm lấp lánh ánh vàng. "
    "Mỗi ngày mẹ dẫn bé chắp cánh ước mơ, ngắm nhìn đàn ngỗng trắng lượn quanh ngõ hẹp vắng vẻ. "
    "Đêm hè trăng sáng rực rỡ, gió lay kẽ lá reo vui nhẹ nhàng êm dịu, tiếng sáo diều vi vu bay bổng. "
    "Thầy giáo dục lòng kiên nhẫn, dạy trò giữ gìn vẻ đẹp thuần khiết của tiếng mẹ đẻ qua bao thế hệ. "
    "Nắng ấm áp sưởi ấm mảnh vườn xanh mướt, hoa đỗ quyên nở rộ khoe sắc thắm đón chào xuân sang."
)

missing_lower = [ch for ch in VIETNAMESE_LOWERCASE if ch not in pangram_lower]
print("Missing in pangram_lower:", missing_lower)
