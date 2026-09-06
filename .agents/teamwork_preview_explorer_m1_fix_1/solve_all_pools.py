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

# 10 sentences for Bold & Tuyên ngôn (size 10 guarantees 100% index hit)
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

# Sentences for Luxury & Sang trọng (8 sentences, 100% index hit for 51 fonts)
luxury_pool = [
    "Vẻ đẹp thuần khiết vượt thời gian của nghệ thuật chữ và tinh hoa văn hóa",
    "Tôn vinh đẳng cấp thượng lưu trong từng đường nét chạm khắc tỉ mỉ và tinh tế",
    "Nghệ sĩ ngẫm nghĩ về những nét vẽ mềm mại, quyến rũ và diễm lệ của đóa hoa đỗ quyên",
    "Không gian tĩnh lặng nâng niu từng trải nghiệm thẩm mỹ đỉnh cao của giới quý tộc",
    "Bản hòa ca êm dịu giữa kỹ nghệ chế tác thủ công và phong cách kiến trúc hoàng gia",
    "Vợ chàng kỵ sĩ bỡ ngỡ bước vào lâu đài lộng lẫy uy nghiêm giữa màn sương sớm",
    "Nét chữ thanh thoát được chau chuốt kỹ càng, gìn giữ trọn vẹn hồn cốt xưa",
    "Ánh sáng huyền ảo soi rọi từng góc nhỏ, gợi mở xúc cảm thăng hoa thuần khiết"
]

# Sentences for Tech & Công nghệ (6 sentences, 100% index hit for 23 fonts)
tech_pool = [
    "Hệ thống trí tuệ nhân tạo và tương lai số hóa toàn diện thúc đẩy đổi mới sáng tạo",
    "Tối ưu hóa thuật toán và trải nghiệm người dùng với tốc độ xử lý siêu phân tán",
    "Đội ngũ kỹ sư nỗ lực giải quyết các bài toán kỹ thuật ngặt nghèo trong kỷ nguyên số",
    "Cấu trúc vi mạch và mã nguồn mở vận hành trơn tru ngay cả dưới áp lực tải nặng",
    "Dữ liệu lớn được phân tích rõ ràng, hỗ trợ việc ra quyết định chính xác và nhanh chóng",
    "Mỗi dòng lệnh đều được kiểm thử kỹ lưỡng, đảm bảo an toàn thông tin và bảo mật đa lớp"
]

# Sentences for Friendly & Nhân văn (8 sentences, 100% index hit for 199 fonts)
friendly_pool = [
    "Nụ cười rạng rỡ chào đón ngày mới bình an, ấm áp và tràn đầy năng lượng yêu thương",
    "Người mẹ trẻ ẵm con thơ dạo bước trên hè phố rực rỡ sắc hoa đỏ thắm",
    "Bữa cơm chiều đầm ấm có tiếng cười ríu rít của đàn trẻ nhỏ bên cạnh ông bà",
    "Bác làm vườn cặm cụi chăm sóc từng luống rau xanh mướt mát sau cơn mưa rào",
    "Mỗi trang sách mở ra chân trời mới tươi sáng, nuôi dưỡng tâm hồn nhân ái bao la",
    "Lời ru ngọt ngào của mẹ nâng niu giấc ngủ bé thơ suốt những năm tháng êm đềm",
    "Gia đình sum vầy bên tách chè sen thơm ngát, cùng sẻ chia buồn vui cuộc sống",
    "Sự cảm thông sâu sắc và tình cảm đằm thắm là chiếc cầu nối gắn kết mọi trái tim"
]

# Sentences for Nostalgic & Cổ điển (8 sentences, 100% index hit for 45 fonts)
nostalgic_pool = [
    "Hà Nội ba mươi sáu phố phường rêu phong cổ kính, nét vẽ biển hiệu vương vấn hoài niệm",
    "Ngõ nhỏ quanh co rợp bóng cây xanh, gợi nhớ tiếng còi tàu sớm và hương hoa sữa nồng nàn",
    "Chiếc xe đạp cũ chở đầy cúc họa mi lướt qua hè phố vắng trong chiều mưa bay lất phất",
    "Người nghệ nhân già tỉ mỉ ngồi nắn nót từng con chữ trên trang giấy dó thô mộc",
    "Cuốn sách cổ nhuốm màu thời gian vẫn giữ nguyên nét mực trang nhã thanh lịch",
    "Tiếng chuông chùa ngân vang trầm mặc giữa không gian tĩnh mịch của buổi hoàng hôn",
    "Ký ức về một thời kỳ hào hoa trên phố biển xưa được tái hiện qua từng bức ảnh đen trắng",
    "Dáng vẻ trầm mặc của mái ngói âm dương trải qua bao thăng trầm dâu bể cuộc đời"
]

SAMPLE_TEXTS_POOL = {
    "Bold & Tuyên ngôn": bold_pool,
    "Luxury & Sang trọng": luxury_pool,
    "Tech & Công nghệ": tech_pool,
    "Friendly & Nhân văn": friendly_pool,
    "Nostalgic & Cổ điển": nostalgic_pool
}

def select_sample_text(mood, index):
    pool = SAMPLE_TEXTS_POOL.get(mood, SAMPLE_TEXTS_POOL["Bold & Tuyên ngôn"])
    return pool[index % len(pool)]

# Simulate catalog 361 fonts
simulated_samples = []
for idx, font in enumerate(cat['fonts']):
    mood = font.get('matrix_3d', {}).get('mood', 'Bold & Tuyên ngôn')
    st = select_sample_text(mood, idx)
    simulated_samples.append(st)

all_text = " ".join(simulated_samples)
missing_lower = [ch for ch in VIETNAMESE_LOWERCASE if ch not in all_text]
missing_upper = [ch for ch in VIETNAMESE_UPPERCASE if ch not in all_text]

print("=== 361 FONTS WITH OPTIMIZED POOLS ===")
print("Total fonts:", len(simulated_samples))
print("Missing lowercase characters count:", len(missing_lower))
if missing_lower:
    print("Missing lower:", missing_lower)
print("Missing uppercase characters count:", len(missing_upper))
if missing_upper:
    print("Missing upper:", missing_upper)
