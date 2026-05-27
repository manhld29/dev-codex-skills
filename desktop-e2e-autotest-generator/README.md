# Desktop E2E Autotest Generator

Skill nay giup Codex tu dong:
- Phan tich `feature_goal` (muc dich chuc nang can test)
- Sinh danh sach test case E2E
- Chuyen test case thanh code auto test Python cho desktop app
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

## Skill se lam gi

1. Tao test cases markdown trong `auto_test/`:
- `testcases_<feature_slug>.md`

2. Tao skeleton code E2E unittest trong `auto_test/`:
- `test_<feature_slug>_e2e.py`

3. Tu dong chon mode launch:
- `exe`: chay truc tiep executable
- `python`: chay command Python
- `command`: command tong quat

4. Chuan bi san cac test baseline:
- Launch app
- Vao man hinh chuc nang
- Feature-specific flow (TODO can map selector that)
- Close app

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
- Neu app khong mo duoc hoac khong attach UI, trang thai thuc thi can report `blocked` kem ly do cu the.
- Nen uu tien explicit wait thay vi `sleep` cung de giam flaky test.