# Desktop E2E Autotest Generator

Skill nay giup Codex tu dong:
- Phan tich `feature_goal` (muc dich chuc nang can test)
- Sinh test case va export thanh CSV
- Tao code auto test Python cho desktop app
- Doc file CSV test case va cap nhat ket qua test vao tung dong testcase theo `tc_id`
- Ho tro target chay app dang `.exe` hoac lenh `python file.py`

## Vi tri skill

`C:\Users\ManhLD31\.codex\skills\desktop-e2e-autotest-generator`

## Cach goi skill

Dung prompt theo format:

```text
Use $desktop-e2e-autotest-generator
feature_goal: <muc dich chuc nang>
launch_target: <C:\path\app.exe hoac python path\to\main.py>
source_paths: <optional, danh sach file code lien quan>
```

## Vi du

```text
Use $desktop-e2e-autotest-generator
feature_goal: Dang nhap va tim kiem ho so khach hang
launch_target: python src/main.py
source_paths: src/controller/list_vd_controller.py, src/services/session_service.py
```

## Skill se tao output gi

1. File testcase CSV trong `test_case/`:
- `testcases_<feature_slug>.csv`

2. File test E2E unittest trong `auto_test/`:
- `test_<feature_slug>_e2e.py`

3. File test E2E se:
- Doc testcase tu CSV
- Chay testcase theo methods `test_tcXX_*`
- Fill ket qua `PASS` / `FAIL` / `ERROR` / `SKIP` vao cot `result`
- Fill thong tin chi tiet vao cot `actual`

## Cau truc CSV

CSV duoc tao voi cac cot:

```text
tc_id,title,precondition,steps,expected,result,actual
```

- `result`, `actual` ban dau rong
- Sau khi chay test, ket qua tung `tc_id` duoc cap nhat ngay trong file CSV

## Chay script thu cong (neu can)

```powershell
python C:\Users\ManhLD31\.codex\skills\desktop-e2e-autotest-generator\scripts\generate_desktop_e2e.py \
  --feature-goal "Dang nhap va tim kiem ho so" \
  --launch-target "python src/main.py" \
  --repo-root "C:\Users\ManhLD31\Documents\FCI\Python\fcd-client" \
  --source-path "src/controller/list_vd_controller.py" \
  --source-path "src/services/session_service.py"
```

## Chay test da sinh

```powershell
python -m unittest auto_test/test_<feature_slug>_e2e.py -v
```

## Yeu cau moi truong

- Windows desktop session co GUI
- Python tuong thich voi project
- Khuyen nghi cai `pywinauto` de bam control UI on dinh

## Luu y quan trong

- File test sinh ra chua placeholder `TODO`; can thay selector that (`auto_id`, `title`, `control_type`) theo app thuc te.
- Neu app khong mo duoc hoac khong attach UI, ket qua co the la `SKIP` hoac `ERROR`; thong tin se duoc ghi vao cot `actual`.
- Nen uu tien explicit wait thay vi `sleep` cung de giam flaky test.