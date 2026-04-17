# TASK-demo-figma — Figma-to-Code Workflow Demo

## Mô tả

Task mẫu minh họa workflow trích xuất design từ Figma và lưu local để coder implement.
Sử dụng Figma MCP `get_design_context` để lấy code reference + design tokens.

## User Request

> "Implement trang Home cho fashion e-commerce store theo design Figma này:
> https://www.figma.com/design/7xrPkquBzkRr2HLgTMKqr8/Fashion-Ecommerce-Store?node-id=2-63"

## Figma Info

- **File**: Fashion Ecommerce Store (Community)
- **Frame**: Home (node-id: 2:63)
- **Viewport**: 1440x3998px (desktop)
- **Stack gợi ý**: React + Tailwind CSS (output từ Figma MCP)

## Ghi chú

- Task này là **ví dụ tham khảo** cho quy trình Figma → Local Assets → Coder
- Các file trong `assets/` là output thực từ Figma MCP API (demo session)
- Minh họa luồng: Task Analysis trích xuất → Coder Leader assign → Service Coder đọc local
- Xem thêm: `.claude/skills/skill-task-analysis/SKILL.md` § Design Asset Extraction
