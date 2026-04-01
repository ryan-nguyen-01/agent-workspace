---
name: skill-role-ui-review
description: Skill so sánh UI đã code với Figma design — chụp screenshot UI thực, đọc ảnh Figma, phát hiện visual discrepancies và report cụ thể từng điểm sai. Dùng sau khi FE agent hoàn thành coding.
---

# Skill: UI Visual Review

## Mục đích
Sau khi viết xong UI, agent tự chụp screenshot UI thực đang chạy, đọc Figma design, so sánh trực tiếp và báo cáo những điểm chưa khớp. Không cần chờ human review thủ công.

---

## Điều kiện tiên quyết

```yaml
requires:
  - App đang chạy (dev server hoặc có static build)
  - Figma URL hoặc screenshot Figma đã được cung cấp trước đó
  - playwright hoặc puppeteer đã được cài (dùng để chụp screenshot)
  - Hoặc: user cung cấp screenshot UI thực (nếu không chạy được dev server)
```

---

## Quy trình (5 bước)

### Bước 1 — Lấy Figma reference

```
Nguồn Figma (theo thứ tự ưu tiên):
  1. Figma MCP → get_design_context(fileKey, nodeId) → trả về screenshot + specs
  2. Screenshot Figma đã được lưu trong docs/ui-design/ (từ agent-designer)
  3. User cung cấp Figma URL → parse → request qua WebFetch

Lưu reference vào memory:
  figma_ref = { screenshot_path, specs: { colors, spacing, typography } }
```

### Bước 2 — Chụp screenshot UI thực

```
OPTION A — Dev server đang chạy (ưu tiên):

  Detect dev server:
    - Check package.json scripts → "dev", "start", "serve"
    - Check nếu port 3000/5173/4200/8080 đang mở:
      lsof -i :3000 | grep LISTEN

  Nếu server đang chạy → chụp bằng Playwright:

    npx playwright screenshot \
      --browser chromium \
      http://localhost:{port}{path} \
      /tmp/ui-review-{component}-{timestamp}.png

  Responsive screenshots:
    Desktop:  --viewport-size "1440,900"
    Tablet:   --viewport-size "768,1024"
    Mobile:   --viewport-size "375,812"

OPTION B — Server chưa chạy:

  Thử start server nền:
    npm run dev &
    sleep 3 (đợi khởi động)
    → Chụp → kill server

OPTION C — Không thể chạy server:

  Yêu cầu user cung cấp screenshot:
  "Để review UI, tôi cần screenshot của component {X} đang chạy.
   Bạn có thể chụp và share không?
   Hoặc nếu có Storybook, share URL story tương ứng."
```

### Bước 3 — So sánh visual

```
Đọc cả 2 ảnh bằng Read tool:
  - figma_screenshot: Read(figma_ref.screenshot_path)
  - actual_screenshot: Read(/tmp/ui-review-{component}-{timestamp}.png)

So sánh theo checklist:

  LAYOUT & SPACING
  □ Padding/margin đúng không? (ước lượng từ visual)
  □ Gap giữa elements đúng không?
  □ Alignment: center/left/right đúng không?
  □ Width/height proportions đúng không?
  □ Flex direction đúng không?

  TYPOGRAPHY
  □ Font size tương đối đúng không?
  □ Font weight (bold/regular/light) đúng không?
  □ Line height (tight/normal/loose) đúng không?
  □ Text alignment đúng không?
  □ Text truncation (nếu có) đúng không?

  COLORS
  □ Background color đúng không?
  □ Text color đúng không?
  □ Border/stroke color đúng không?
  □ Button/interactive element color đúng không?
  □ Có hover state không (nếu Figma có)

  COMPONENTS
  □ Icon đúng loại/size không?
  □ Button shape/size đúng không?
  □ Input field style đúng không?
  □ Avatar/image placeholder đúng không?
  □ Badge/tag style đúng không?

  RESPONSIVE (nếu có nhiều breakpoints)
  □ Layout thay đổi đúng ở breakpoint không?
  □ Elements ẩn/hiện đúng không?
  □ Font size scale đúng không?
```

### Bước 4 — Output Report

```markdown
## UI Review Report — {ComponentName}

**So sánh:** Figma design vs Actual render
**Viewport:** Desktop 1440px | Tablet 768px | Mobile 375px
**Verdict:** ✅ MATCH / ⚠️ MINOR DIFF / ❌ NEEDS FIX

---

### ✅ Đúng
- Layout tổng thể: flex column, align center ✓
- Typography heading: font weight bold ✓
- Button primary color: khớp với design ✓

### ⚠️ Sai nhỏ (không block)
- [ ] Padding container: thực tế ~20px, Figma ~24px → sửa `p-5` → `p-6`
- [ ] Gap giữa items: thực tế ~12px, Figma ~16px → sửa `gap-3` → `gap-4`

### ❌ Sai rõ (cần fix)
- [ ] Button border-radius: thực tế sharp, Figma rounded → thêm `rounded-lg`
- [ ] Text color subtitle: thực tế black, Figma gray-500 → sửa thành `text-gray-500`
- [ ] Mobile: sidebar vẫn hiện, Figma ẩn ở mobile → thêm `hidden md:block`

---

**Action:** {n} issues cần fix → tiến hành fix ngay
```

### Bước 5 — Auto-fix và re-review

```
Với mỗi issue ❌ hoặc ⚠️:
  1. Identify file + class/style cần sửa
  2. Apply fix (Edit tool)
  3. Chụp lại screenshot
  4. Verify fix đã đúng

Sau khi fix tất cả:
  → Chụp final screenshot
  → So sánh lần cuối
  → Nếu pass → report MATCH
  → Nếu vẫn còn diff → escalate với ảnh so sánh
```

---

## Retry Budget

```yaml
max_fix_rounds: 2

round_1:
  fix: tất cả issues ❌ và ⚠️
  re_screenshot: true
  re_compare: true

round_2:
  fix: issues còn lại sau round 1
  re_screenshot: true
  re_compare: true

after_round_2:
  action: escalate
  include:
    - final_screenshot
    - figma_reference
    - remaining_issues_list
  message: |
    "Còn {n} visual differences không thể tự fix:
    {list}
    Cần xem lại design spec hoặc confirm với designer."
```

---

## Playwright setup check

```bash
# Kiểm tra playwright có sẵn không
npx playwright --version 2>/dev/null

# Nếu chưa có — install nhanh (không thêm vào package.json)
npx playwright install chromium --with-deps 2>/dev/null

# Chụp screenshot 1 lệnh
npx playwright screenshot --browser chromium \
  --viewport-size "1440,900" \
  http://localhost:3000/path/to/component \
  /tmp/review.png
```

---

## Storybook support

```
Nếu project có Storybook:
  1. Detect: check package.json có @storybook/* không
  2. Nếu có → ưu tiên chụp từ Storybook (isolated, không cần full app)
  3. URL pattern: http://localhost:6006/?path=/story/{component-name}--{variant}
  4. Chụp từng story: default, hover state, mobile viewport
```

---

## Nguyên tắc

- **Screenshot trước, nhận xét sau** — không đoán UI trông như thế nào
- **So sánh visual, không đọc code** — review render thực, không review source
- **Sai nhỏ vẫn fix** — spacing 4px lệch → vẫn sửa, không bỏ qua
- **Responsive là bắt buộc** — luôn check cả mobile nếu Figma có
- **Không block nếu server không chạy** — fallback sang Option C, không dừng
- **Fix ngay trong cùng task** — không tạo ticket mới cho visual issues nhỏ
