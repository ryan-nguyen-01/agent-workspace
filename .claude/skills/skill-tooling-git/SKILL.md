---
name: skill-tooling-git
description: Best practices dùng Git: branching strategy, commit conventions (Conventional Commits), merge vs rebase, conflict resolution, hooks và workflow cho team.
---

# Skill: Git

## Branching Strategy

```
Gitflow (cho product có release cycle):
  main          ← production, always stable
  develop       ← integration branch
  feature/*     ← new features (branch từ develop)
  release/*     ← release prep (branch từ develop)
  hotfix/*      ← emergency fixes (branch từ main)

GitHub Flow (cho web app, deploy liên tục):
  main          ← production, always deployable
  feature/*     ← mọi thứ khác (branch từ main, merge về main)

Trunk-Based (cho team nhỏ, CI/CD mạnh):
  main          ← tất cả merge vào đây
  feature/*     ← tồn tại < 1-2 ngày, short-lived branches
```

## Conventional Commits

```
Format: <type>(<scope>): <description>

Types:
  feat     → tính năng mới
  fix      → bug fix
  docs     → chỉ thay đổi docs
  style    → format, whitespace (không ảnh hưởng logic)
  refactor → refactor code (không feat, không fix)
  test     → thêm/sửa tests
  chore    → build process, dependencies, tooling
  perf     → cải thiện performance
  ci       → thay đổi CI/CD config
  revert   → revert commit trước

✅ Ví dụ tốt:
feat(auth): add Google OAuth login
fix(order): prevent duplicate order on double-click
refactor(user): extract email validation to utility
chore: upgrade NestJS to v10

❌ Ví dụ tệ:
fix stuff
update
WIP
```

## Merge vs Rebase

```
Merge (--no-ff) — preserve history, rõ ràng khi nào feature được merge
  git checkout main
  git merge --no-ff feature/login
  → Tạo merge commit, giữ nguyên feature branch history

Rebase — clean linear history, phù hợp trước khi merge
  git checkout feature/login
  git rebase main        ← rebase lên main mới nhất
  git checkout main
  git merge --ff-only feature/login  ← fast-forward

✅ Rule of thumb:
  - Rebase feature branch lên main/develop trước khi tạo PR
  - Không rebase branch đã push (rewrite public history)
  - Merge (no-ff) để merge PR vào main/develop
```

## Useful Commands

```bash
# Xem history dạng graph
git log --oneline --graph --decorate --all

# Stash với message
git stash push -m "WIP: login form validation"
git stash list
git stash pop stash@{0}

# Interactive rebase — squash commits trước khi merge
git rebase -i HEAD~3   # squash 3 commits gần nhất

# Cherry-pick 1 commit sang branch khác
git cherry-pick <commit-hash>

# Undo commit nhưng giữ lại changes
git reset --soft HEAD~1

# Xem diff đã staged
git diff --staged

# Tìm commit gây ra bug (binary search)
git bisect start
git bisect bad                # current commit is bad
git bisect good <hash>        # known good commit
# → Git tự checkout, mark good/bad cho đến khi tìm ra

# Xóa branch đã merge
git branch --merged | grep -v '\*\|main\|develop' | xargs git branch -d
```

## .gitignore Chuẩn

```gitignore
# Dependencies
node_modules/
.venv/
vendor/

# Build output
dist/
build/
*.class
*.jar
target/

# Environment & secrets
.env
.env.local
.env.*.local
*.pem
*.key

# IDE
.idea/
.vscode/
*.swp
.DS_Store

# Test coverage
coverage/
.nyc_output/

# Logs
*.log
logs/
```

## Git Hooks (với Husky)

```bash
# Setup
pnpm add -D husky lint-staged
npx husky init

# .husky/pre-commit
npx lint-staged

# .husky/commit-msg
npx --no -- commitlint --edit $1

# package.json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,yml}": ["prettier --write"]
  }
}
```

## PR / Code Review Conventions

```
PR title: follow Conventional Commits format
PR size: < 400 lines changed (nếu lớn hơn → split)
PR description:
  - What: mô tả thay đổi
  - Why: lý do / ticket link
  - How to test: steps để reviewer verify

Review checklist:
  [ ] Logic đúng không?
  [ ] Edge cases đã handle?
  [ ] Tests có đủ không?
  [ ] Không có secrets/credentials trong code?
  [ ] Performance impact?
```

## Anti-patterns

```
❌ Commit trực tiếp vào main/master
❌ Commit message "fix", "update", "WIP" không có context
❌ 1 commit chứa nhiều unrelated changes
❌ Force push lên shared branches (main, develop)
❌ Merge conflict giải quyết bằng cách chọn hết "ours" hoặc "theirs"
❌ .env file trong repo (dù là private repo)
❌ Để secret/API key trong code, sau đó xóa bằng commit mới
   → Secret vẫn còn trong git history! Phải revoke và rotate key
```
