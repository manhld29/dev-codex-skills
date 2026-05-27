# code-change-impact-review

Hướng dẫn sử dụng skill `code-change-impact-review` để đảm bảo mọi thay đổi code đều có:
- Lý do thay đổi rõ ràng.
- Phân tích tác động đến logic liên quan.

## Mục tiêu

Skill này ép quy trình giải thích bắt buộc mỗi khi có sửa code, giúp review nhanh hơn và giảm rủi ro hồi quy.

## Khi nào nên dùng

Dùng skill này khi có bất kỳ thay đổi source nào, ví dụ:
- Sửa bug.
- Refactor.
- Thêm/chỉnh tính năng.
- Tối ưu hiệu năng.
- Chỉnh cấu hình ảnh hưởng hành vi runtime.

Nếu chỉ trả lời lý thuyết và **không sửa code**, không cần áp dụng full cấu trúc báo cáo.

## Cách kích hoạt

Bạn có thể kích hoạt bằng cách nêu tên skill trong yêu cầu, ví dụ:

```text
Dùng skill code-change-impact-review để sửa lỗi X.
```

Hoặc truyền trực tiếp đường dẫn `SKILL.md` của skill trong context.

## Quy trình bắt buộc

Khi skill được áp dụng, agent phải đi theo trình tự:
1. Xác nhận phạm vi và liệt kê file sẽ sửa.
2. Xác định logic liên quan trước khi edit.
3. Chỉ thực hiện tập thay đổi nhỏ nhất nhưng an toàn.
4. Verify bằng test/check phù hợp nếu khả thi.
5. Báo cáo kết quả theo đúng cấu trúc bắt buộc.

## Checklist phân tích tác động

Với mỗi thay đổi không tầm thường, phải rà soát:
- Data flow và chuyển trạng thái.
- Contract hàm/lớp (input, output, side effect).
- Call site và module phụ thuộc.
- Error handling và failure path.
- Backward compatibility và giả định config.
- Rủi ro hiệu năng, bảo mật, concurrency (nếu liên quan).
- Ảnh hưởng coverage test và case test còn thiếu.

## Mẫu output bắt buộc khi có sửa code

Giữ đúng thứ tự 5 phần sau:

1. **Change Summary**
- Liệt kê từng file đã sửa.
- Mỗi file mô tả 1 câu thay đổi.

2. **Why This Change**
- Giải thích lý do gốc cho từng file.
- Gắn với yêu cầu user, nguyên nhân bug hoặc ràng buộc thiết kế.

3. **Impact Analysis**
- Nêu logic/component bị ảnh hưởng theo từng file.
- Mô tả thay đổi hành vi kỳ vọng.
- Nêu side effect tiềm ẩn và cách giảm thiểu.

4. **Risk and Compatibility**
- Nêu rủi ro hồi quy.
- Nêu lưu ý tương thích (API/schema/config/version behavior).

5. **Validation**
- Liệt kê test/check đã chạy và kết quả.
- Nếu chưa chạy, nói rõ lý do và phần chưa xác minh.

## Guardrails

- Không trình bày code edit mà thiếu rationale + impact analysis.
- Không kết luận “không ảnh hưởng” nếu chưa kiểm tra logic phụ thuộc.
- Luôn nêu rõ giả định khi thiếu ngữ cảnh repository.
- Viết ngắn gọn nhưng không thiếu các phần bắt buộc.

## Trường hợp không sửa code

Nếu không có source edit:
- Nêu rõ: không có thay đổi mã nguồn.
- Trả lời ngắn theo hướng giải thích, không cần full 5 phần bắt buộc.

## Ví dụ prompt

```text
Hãy sửa bug timeout khi upload file. Bắt buộc dùng code-change-impact-review và báo cáo đầy đủ 5 phần.
```

```text
Refactor module auth để tách token validator. Áp dụng code-change-impact-review, ưu tiên thay đổi tối thiểu.
```
