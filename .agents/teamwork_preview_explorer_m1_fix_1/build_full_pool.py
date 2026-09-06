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

CANDIDATE_POOL = {
    "Bold & Tuyên ngôn": [
        "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
        "BẢN LĨNH TIÊN PHONG BỨT PHÁ MỌI GIỚI HẠN",
        "KIẾN TẠO CHUẨN MỰC MỚI CỦA SỰ HOÀN HẢO",
        "CHINH PHỤC ĐỈNH CAO NGHỆ THUẬT THỊ GIÁC",
        "ĐỘC LẬP - TỰ DO - HẠNH PHÚC",
        "ĐẮP XÂY KỶ NGUYÊN HÙNG CƯỜNG VÀ THỊNH VƯỢNG",
        "SỨC MẠNH VŨ BÃO VƯỢT THỬ THÁCH NGHIỆT NGÃ",
        "KỲ TÍCH KHỞI NGHIỆP TRÊN NỀN TẢNG CÔNG NGHỆ MỚI",
        "VỮNG BƯỚC TIẾN VÀO TƯƠNG LAI RỰC RỠ HUY HOÀNG",
        "KHẲNG ĐỊNH ĐẲNG CẤP THƯƠNG HIỆU QUỐC GIA VIỆT NAM",
        "VƯỢT QUA SÓNG GIÓ ĐỂ CHẠM TỚI THÀNH CÔNG RỰC RỠ",
        "HÀNH TRÌNH VẠN DẶM BẮT ĐẦU TỪ MỘT BƯỚC CHÂN NHỎ",
        "QUYẾT TÂM ĐỔI MỚI TOÀN DIỆN VÀ SÁNG TẠO ĐỘT PHÁ",
        "GIỮ VỮNG Ý CHÍ KIÊN CƯỜNG TRƯỚC MỌI KHÓ KHĂN",
        # All-caps sentences to cover all missing uppercase characters:
        "NGẪM NGHĨ KỸ CÀNG VỀ MỸ THUẬT VÀ LỄ HỘI DÂN TỘC TRUYỀN THỐNG",
        "GIỮ GÌN CHỮ VIẾT TỈ MỈ RÕ RÀNG TRONG TỪNG NÉT VẼ",
        "ẴM BỒNG TRẺ THƠ QUA VŨ BÃO VÀ GIÓ XOÁY NGHIỆT NGÃ",
        "TRƯỢT NGÃ RỒI ĐỨNG LÊN ĐẬP TAN NỖI SỢ HÃI",
        "KỴ BINH VÀ CHIẾN MÃ VƯỢT ĐÈO DỐC HIỂM TRỞ",
        "CẰN CỖI VẪN VƯƠN LÊN XANH TƯƠI MÃNH LIỆT",
        "HỖ TRỢ LẪN NHAU TRONG HOÀN CẢNH NGẶT NGHÈO VÀ ĐAU THƯƠNG",
        "LẪM LIỆT HIÊN NGANG TRƯỚC BÃO DÔNG VÀ THÁC LŨ HÙNG VĨ",
        "HÈ PHỐ ĐỎ THẮM HOA PHƯỢNG KHOE SẮC RỰC RỠ DƯỚI NẮNG VÀNG",
        "NGÕ NHỎ THỎ THẺ TIẾNG CHIM CA TRONG SỚM MAI THANH BÌNH",
        "VỢ CHỒNG BỠ NGỠ TRƯỚC KHÔNG GIAN BÈO DẠT MÂY TRÔI",
        "GÕ CỬA MỤC TIÊU LỚN LAO VỚI LÒNG BỀN BỈ VÀ DŨNG CẢM",
        "THẦM THÌ LỜI NÓI DỊU DÀNG VỀ NGHỈ NGƠI VÀ HỒI PHỤC",
        "HỖ TRỢ ĐỒNG BỘ ĐỂ VƯƠN TỚI ĐỈNH CAO DANH VỌNG",
        "BẢO VỆ MẸ HIỀN VÀ TỔ QUỐC THÂN YÊU VỚI TRỌN VẸN TRÁI TIM"
    ],
    "Luxury & Sang trọng": [
        "Vẻ đẹp thuần khiết vượt thời gian của nghệ thuật chữ",
        "Tôn vinh đẳng cấp thượng lưu và tinh hoa văn hóa",
        "Sự tinh tế trong từng đường nét và khoảng không gian",
        "Dấu ấn kiệt tác kiến tạo di sản thị giác trường tồn",
        "Hương sắc ngọc ngà, vẻ đẹp thanh tao thoát tục",
        "Bản hòa ca êm dịu của những đường cong mỹ miều và quyến rũ",
        "Nét vẽ thanh mảnh gợi cảm hứng hoàng gia sang trọng và quý phái",
        "Không gian tĩnh lặng nâng niu từng trải nghiệm thẩm mỹ đỉnh cao",
        "Diễm lệ và kiêu sa như đóa hoa đỗ quyên rạng rỡ trong sương sớm",
        "Ánh sáng lấp lánh phản chiếu chất liệu gấm nhung cao cấp",
        "Sự hòa quyện hoàn hảo giữa kỹ nghệ chế tác và cảm xúc thăng hoa",
        "Kiến trúc cổ điển mang linh hồn của thời đại hoàng kim rực rỡ",
        "Trang nhã, chuẩn mực và trường tồn cùng dòng chảy lịch sử",
        "Đẳng cấp thượng thừa được khẳng định qua từng chi tiết tỉ mỉ",
        # Sentences ensuring lowercase diacritics coverage:
        "Mỗi nét chữ thanh thoát đều được chăm chút tỉ mỉ và kỹ lưỡng",
        "Nghệ sĩ ngẫm nghĩ về những nét vẽ mềm mại đầy quyến rũ",
        "Lễ hội mùa xuân mang đến không khí tươi vui rộn rã khắp phố phường",
        "Cảm xúc bâng khuâng khi ngắm nhìn ngõ nhỏ rêu phong cổ kính",
        "Vợ chàng kỵ sĩ bỡ ngỡ bước vào lâu đài lộng lẫy uy nghiêm",
        "Gió hè thổi nhẹ qua kẽ lá, lay động những đóa hoa đỏ thắm",
        "Bản thiết kế đạt độ chuẩn xác cao, thể hiện rõ ràng từng tỷ lệ vàng",
        "Vẻ đẹp huyền bí của vũ trụ khơi gợi niềm đam mê khám phá bất tận",
        "Nét mực đen tuyền óng ả trên nền giấy dó trắng ngà truyền thống",
        "Phong cách tối giản nhưng chứa đựng chiều sâu triết lý nhân sinh",
        "Sự kết hợp hài hòa giữa truyền thống phương Đông và hiện đại phương Tây",
        "Mỗi con chữ là một tác phẩm điêu khắc thu nhỏ đầy mê hoặc"
    ],
    "Tech & Công nghệ": [
        "Hệ thống trí tuệ nhân tạo và tương lai số hóa toàn diện",
        "Tối ưu hóa thuật toán và trải nghiệm người dùng hiện đại",
        "Kết nối không giới hạn trong kỷ nguyên dữ liệu đám mây",
        "Cấu trúc vi mạch và kiến trúc điện toán phân tán",
        "Mã nguồn mở thúc đẩy đổi mới sáng tạo toàn cầu",
        "Nền tảng hạ tầng đám mây siêu phân tán với độ trễ cực thấp",
        "Xử lý dữ liệu lớn bằng mạng nơ-ron học sâu thế hệ mới",
        "An toàn thông tin và bảo mật đa lớp chuẩn mực quốc tế",
        "Chuyển đổi số toàn diện cho doanh nghiệp tiên phong công nghệ",
        "Tự động hóa quy trình nghiệp vụ với độ chính xác tuyệt đối",
        "Giải pháp lưu trữ phân tán bền vững và hiệu năng vượt trội",
        "Kỹ thuật xử lý tín hiệu số trong hệ thống truyền thông hiện đại",
        "Đột phá công nghệ lượng tử mở ra chân trời khoa học mới",
        "Tích hợp chuỗi khối và hợp đồng thông minh minh bạch an toàn",
        # Sentences with diacritics:
        "Đội ngũ kỹ sư nỗ lực giải quyết các bài toán kỹ thuật ngặt nghèo",
        "Mỗi dòng lệnh code đều được kiểm thử kỹ càng và tỉ mỉ từng chi tiết",
        "Dữ liệu lớn được phân tích rõ ràng giúp đưa ra quyết định chuẩn xác",
        "Kỷ nguyên số đòi hỏi tư duy đổi mới và năng lực thích ứng linh hoạt",
        "Giao diện trực quan hỗ trợ người dùng thao tác dễ dàng và thuận tiện",
        "Hệ điều hành vận hành trơn tru ngay cả trong điều kiện tải nặng",
        "Công nghệ vi xử lý tiết kiệm năng lượng và thân thiện với môi trường",
        "Sự hội tụ của trí tuệ nhân tạo và dữ liệu vi mô mang lại kỳ tích mới",
        "Cấu trúc dữ liệu dạng cây giúp việc tra cứu thông tin nhanh chóng hơn",
        "Mạng lưới kết nối xuyên biên giới xóa nhòa khoảng cách không gian"
    ],
    "Friendly & Nhân văn": [
        "Nụ cười rạng rỡ chào đón một ngày mới bình an và tràn đầy năng lượng",
        "Học ăn học nói, học gói học mở, yêu thương chan hòa",
        "Trúc xinh trúc mọc đầu đình, nét duyên thầm kín dịu dàng",
        "Gia đình sum vầy ấm áp bên mâm cơm chiều rộn rã tiếng cười",
        "Mỗi trang sách mở ra một chân trời mới tươi sáng và rộng mở",
        "Tình yêu thương lan tỏa xua tan đi bao giá lạnh cuộc đời",
        "Bàn tay mẹ dịu hiền vỗ về giấc ngủ êm đềm của đàn con thơ",
        "Lời ru êm ái ngọt ngào theo con đi suốt cuộc đời dài rộng",
        "Tiếng cười giòn tan của trẻ thơ thắp sáng niềm tin hy vọng",
        "Chia sẻ buồn vui bên chén trà thơm ngát ấm áp nghĩa tình",
        "Gần gũi và mộc mạc như bờ tre giếng nước mái đình làng quê xưa",
        "Lòng nhân ái bao la là chiếc cầu nối trái tim đến với trái tim",
        "Ánh mắt trìu mến thấu hiểu và sẻ chia những khó khăn cùng bè bạn",
        "Bình yên là khi tâm hồn được thư thái giữa thiên nhiên trong lành",
        # Sentences with full diacritics:
        "Người mẹ trẻ ẵm con thơ dạo bước trên con đường hoa rực rỡ",
        "Bữa cơm chiều đầm ấm có tiếng cười nói ríu rít của đàn trẻ nhỏ",
        "Bác làm vườn cặm cụi chăm sóc từng luống rau xanh mướt mát",
        "Những kỷ niệm tuổi thơ êm đềm như dòng suối nhỏ chảy qua năm tháng",
        "Món quà giản dị nhưng chan chứa tấm lòng chân thành và ấm áp",
        "Gió hè mát rượi thổi qua hiên nhà, mang theo hương sen thoang thoảng",
        "Tiếng đàn thánh thót ngân vang giữa đêm trăng thanh vắng êm dịu",
        "Cô giáo mỉm cười khích lệ khi thấy học trò tự tin vượt qua thử thách",
        "Sự cảm thông sâu sắc giúp xoa dịu những nỗi đau và mất mát",
        "Hạnh phúc đôi khi chỉ là một tách cà phê thơm ấm giữa sáng mùa đông"
    ],
    "Nostalgic & Cổ điển": [
        "Hà Nội ba mươi sáu phố phường rêu phong cổ kính ngàn năm",
        "Sài Gòn hoa lệ, nét chữ vẽ tay xưa vương vấn hoài niệm",
        "Gợi nhớ tiếng còi tàu sớm và hương hoa sữa nồng nàn góc phố",
        "Ký ức một thời hào hoa trên phố biển chiều mưa rơi lất phất",
        "Nét mực nghiên bút của một thời văn chương tao nhã thanh lịch",
        "Tiếng chuông chùa ngân nga trầm mặc giữa chiều thu sương giăng lối",
        "Mái ngói âm dương rêu phong nhuộm màu thời gian trăm năm cổ kính",
        "Chiếc xe đạp cũ chở đầy hoa cúc họa mi qua từng góc phố quen",
        "Hương cà phê phin đậm đà trong quán nhỏ góc ngõ chiều mưa bay",
        "Những bức thư tình viết tay trên giấy pơ-luya vàng ố màu kỷ niệm",
        "Tiếng rao đêm mộc mạc da diết vọng lại từ con ngõ dài hun hút",
        "Vẻ đẹp trầm mặc của kinh thành xưa qua bao thăng trầm biến đổi",
        "Chiếc máy hát đĩa than cũ kỹ ngân nga giai điệu tiền chiến da diết",
        "Ký ức Sài Gòn xưa sống lại qua từng nét chữ biển hiệu vẽ tay",
        # Sentences with diacritics:
        "Ngõ nhỏ quanh co rợp bóng cây xanh với những ngôi nhà cổ kính",
        "Hè phố rực rỡ ánh đèn vàng khi màn đêm buông xuống êm đềm",
        "Tiếng chim thỏ thẻ hót vang chào đón ánh bình minh ấm áp",
        "Người nghệ nhân già tỉ mỉ chạm khắc từng chi tiết trên mặt gỗ quý",
        "Vợ chồng già dắt tay nhau đi dạo bên bờ hồ lộng gió heo may",
        "Cuốn sách cũ kỹ nằm yên trên kệ gỗ thoang thoảng mùi giấy xưa",
        "Bức tranh sơn mài diễn tả cảnh sinh hoạt dân dã miền thôn quê",
        "Nỗi nhớ quê hương da diết dâng trào trong lòng người con xa xứ",
        "Cơn mưa rào đầu hạ tưới mát những hàng cây cằn cỗi sau mùa đông",
        "Giai điệu du dương của bản tình ca xưa làm thổn thức bao trái tim"
    ]
}

# Test all sentences together
all_text = ""
for mood, sents in CANDIDATE_POOL.items():
    for s in sents:
        all_text += " " + s

missing_lower = [ch for ch in VIETNAMESE_LOWERCASE if ch not in all_text]
missing_upper = [ch for ch in VIETNAMESE_UPPERCASE if ch not in all_text]

print("=== CANDIDATE POOL VERIFICATION ===")
print("Total sentences:", sum(len(s) for s in CANDIDATE_POOL.values()))
print("Missing lowercase characters count:", len(missing_lower))
if missing_lower:
    print("Missing lower:", missing_lower)
print("Missing uppercase characters count:", len(missing_upper))
if missing_upper:
    print("Missing upper:", missing_upper)
