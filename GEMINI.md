# Quy Tắc Tác Chiến Đội Ngũ Tự Trị Tuyệt Đối (Mantra TEAM :)
- **Mantra Tối Cao Bắt Buộc**: Khi yêu cầu của anh Việt bắt đầu bằng tiền tố `TEAM :` (hoặc chứa chữ `TEAM : ` ở đầu câu):
- **HÀNH ĐỘNG KỸ THUẬT BẮT BUỘC 100%**:
  1. **KÍCH HOẠT NGAY CÔNG CỤ `invoke_subagent`**:
     - Tuyệt đối KHÔNG được tự mình làm một mình một mạch.
     - Phải phân tách công việc và khởi tạo ngay ít nhất 2 subagents chạy song song:
       - **Subagent 1 (Lead Coder / Implementer)**: Chuyên trách viết mã nguồn, cấu hình, xử lý dữ liệu chính. (Role: `Lead Implementer`, Model: `inherit`, TypeName: `self`).
       - **Subagent 2 (Tester / Auditor / Verifier)**: Chuyên trách viết test, chạy test E2E, audit đối soát mã nguồn, kiểm tra giao diện/dữ liệu và bắt lỗi ngầm. (Role: `Quality Auditor`, Model: `inherit`, TypeName: `self`).
  2. **TRIẾT LÝ TỰ TRỊ OPUS (DIỆT TRỪ HỎI LẮT NHẮT)**:
     - **Tự Duyệt Kế Hoạch 100%**: Tuyệt đối KHÔNG dừng lại hỏi ý kiến hoặc xin approve plan giữa chừng (`request_feedback = false`).
     - **CẤM DÙNG `ask_question`**: Không được tạo form trắc nghiệm hoặc đặt câu hỏi phân vân kiến trúc.
     - **Assumption-Driven**: Gặp điểm chưa rõ -> Tự động đưa ra giả định chuẩn production tốt nhất và làm thẳng tay.
  3. **HỘI ĐỒNG KIỂM DUYỆT NỘI BỘ (SILENT AUDIT)**:
     - Các subagent tự trao đổi qua `send_message`, tự sửa lỗi cho nhau dưới nền.
     - Không đẩy log dở dang hoặc tin nhắn rác lên khung chat của anh Việt.
  4. **BÀN GIAO 1-SHOT CHỈ KHI HOÀN TẤT TOÀN DIỆN**:
     - Chỉ trả lời anh Việt khi tất cả subagents đã hoàn thành và hệ thống đã kiểm thử thành công.
     - Báo cáo ngắn gọn 3 mục: (1) Những gì đã làm & giả định đã chọn, (2) Kết quả test, (3) Link/File trực tiếp.
