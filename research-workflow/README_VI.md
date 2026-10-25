# Bộ công cụ Research học thuật (Python)

Bộ công cụ khởi đầu cho quy trình tìm kiếm tài liệu học thuật có thể tái lập. Công cụ truy vấn API metadata công khai của OpenAlex và Crossref, chuẩn hóa thông tin, loại trùng lặp và xuất CSV, BibTeX, JSON, nhật ký tìm kiếm và bản tóm tắt lượt chạy.

**Phạm vi:** Tự động hóa bước tìm kiếm metadata ban đầu, không phải một systematic review hoàn chỉnh. Công cụ không đảm bảo bao phủ mọi cơ sở dữ liệu, không tải toàn văn trả phí, không tự đánh giá chất lượng nghiên cứu và không đưa ra quyết định đưa bài vào/loại bài cuối cùng. Cần người nghiên cứu xác minh nguồn và kết quả.

## Chạy tại máy

Yêu cầu Python 3.11 trở lên và kết nối mạng tới API công khai.

    python -m pip install -r research-workflow/requirements.txt
    python research-workflow/scripts/run_research.py --query "formative assessment in secondary language learning" --max-records 50 --since-year 2015 --until-year 2026 --output-dir research-workflow/output

Các tệp đầu ra:

- records.csv: bảng metadata đã chuẩn hóa.
- references.bib: thư mục tài liệu dạng BibTeX.
- records.json: bản ghi chuẩn hóa ở định dạng JSON.
- search_log.json: truy vấn, thời điểm, số lượng kết quả và bộ lọc.
- summary.md: tóm tắt lượt tìm kiếm và các giới hạn.

## Chạy tự động trên GitHub

1. Mở tab Actions của repository.
2. Chọn workflow Academic literature search.
3. Chọn Run workflow.
4. Nhập chủ đề/cụm từ tìm kiếm, số bản ghi tối đa cho mỗi API và khoảng năm xuất bản.
5. Khi workflow hoàn tất, tải artifact academic-research-results từ trang chạy workflow.

Workflow chỉ yêu cầu quyền đọc nội dung repository. Không cần API key cho các truy vấn metadata cơ bản tới OpenAlex và Crossref. Có thể thêm secret RESEARCH_MAILTO với địa chỉ email bạn kiểm soát để nhận diện ứng dụng khi truy vấn Crossref.

## Quy trình nghiên cứu khuyến nghị

1. Viết câu hỏi nghiên cứu, phạm vi, tiêu chí đưa vào/loại trừ, ngôn ngữ và khoảng năm trước khi xem kết quả.
2. Ghi lại nguồn, chuỗi tìm kiếm chính xác, ngày tìm kiếm, bộ lọc và giới hạn. Nhật ký do script tạo là nhật ký thực thi, không thay thế đề cương nghiên cứu.
3. Chạy nhiều truy vấn với từ đồng nghĩa, biến thể chính tả và thuật ngữ gần nghĩa. Tham số tìm kiếm API là tìm kiếm văn bản, không phải bộ phân tích Boolean chuyên biệt cho từng cơ sở dữ liệu.
4. Gộp kết quả, khử trùng lặp theo DOI trước rồi theo tiêu đề/năm; kiểm tra thủ công các trường hợp gần giống.
5. Sàng lọc tiêu đề/tóm tắt theo tiêu chí đã định trước. Ghi lý do loại trừ trong bảng sàng lọc; không dùng điểm liên quan tự động làm quyết định cuối cùng.
6. Đọc toàn văn qua kênh truy cập hợp pháp và xác minh trích dẫn bằng DOI hoặc trang nhà xuất bản.
7. Trích xuất thiết kế, bối cảnh, mẫu, công cụ đo, kết quả, hạn chế và tài trợ/xung đột lợi ích.
8. Đánh giá chất lượng hoặc nguy cơ sai lệch bằng công cụ phù hợp với thiết kế nghiên cứu.
9. Tổng hợp kết quả nhất quán và mâu thuẫn, nêu rõ giới hạn; không xem số trích dẫn là thước đo chân lý hay chất lượng.
10. Nếu viết systematic review, tham khảo checklist và sơ đồ dòng PRISMA 2020 phù hợp, đồng thời báo cáo chính xác quy trình lựa chọn nghiên cứu.

## Chính sách trích dẫn và khả năng tái lập

- Xác minh tiêu đề, tác giả, năm, DOI và tạp chí trước khi trích dẫn.
- Không tự tạo DOI, số trang, trích dẫn trực tiếp hoặc kết quả nghiên cứu.
- Phân biệt kết quả mà bài báo báo cáo với diễn giải của người tổng hợp.
- Giữ nguyên truy vấn, nhật ký, dữ liệu metadata và phiên bản script để tái lập.
- Chỉ lưu/chia sẻ toàn văn khi có quyền hợp pháp.

## Tài liệu tham khảo chính thức

- OpenAlex API: https://help.openalex.org/api/
- Crossref REST API: https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- PRISMA 2020: https://www.prisma-statement.org/prisma-2020
- PRISMA 2020 checklist: https://www.prisma-statement.org/prisma-2020-checklist
- PRISMA 2020 flow diagram: https://www.prisma-statement.org/prisma-2020-flow-diagram
- Zotero import formats: https://www.zotero.org/support/kb/importing_standardized_formats
