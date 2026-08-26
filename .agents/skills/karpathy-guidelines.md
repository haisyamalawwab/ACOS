---
inclusion: always
---

# Karpathy-Inspired Agent Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 🔴 CRITICAL: No Refactoring Without Errors

**IF IT'S NOT BROKEN, DON'T FIX IT.**

This is a **BLOCKING REQUIREMENT** for this project.

- Working code with anti-patterns > Broken "clean" code
- Stability > Perfection
- Ship features > Refactor for aesthetics

**Forbidden without explicit permission:**
- ❌ Refactoring working code to "better patterns"
- ❌ Converting DB queries to ORM "for best practices"
- ❌ Extracting code to classes/services "for clean architecture"
- ❌ Changing working logic "for performance" (without benchmarks)

**For new features:** Copy existing patterns exactly. Don't introduce new architectural patterns.

**For bug fixes:** Fix the bug only. Don't refactor surrounding code.

**If you think refactoring would help:** Ask first, explain trade-offs, let user decide.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## 5. Always Backup Before Editing

**Sebelum mengubah file apapun, buat backup fisik terlebih dahulu.**

### Format nama backup:
```
backups/<subfolder>/<filename>.bak_YYYYMMDD[_NNN]
```

Contoh:
- `backups/js/asset-index.js.bak_20260529`
- `backups/js/asset-index.js.bak_20260529_002` (jika hari yang sama ada lebih dari satu)
- `backups/php/Home.php.bak_20260529`

### Aturan backup:
- **Wajib backup** sebelum edit file JS, CSS, PHP controller, blade view, atau config penting.
- Gunakan **serial tanggal** (`YYYYMMDD`) agar urutan kronologis jelas.
- Jika dalam satu hari ada beberapa sesi, tambahkan suffix `_002`, `_003`, dst.
- Simpan di folder `backups/<tipe>/` sesuai jenis file:
  - `backups/js/` → file JavaScript
  - `backups/css/` → file CSS
  - `backups/php/` → file PHP (controller, model, dll)
  - `backups/blade/` → file Blade view
- **Jangan hapus backup lama** — ini adalah memory fisik selain git.

### Kenapa backup fisik selain git?
- Git history ada tapi butuh `git checkout` untuk restore.
- Backup fisik bisa dibuka langsung untuk referensi tanpa checkout.
- Jika terjadi error setelah beberapa perubahan, bisa compare langsung dengan backup.

### Alur wajib sebelum edit:
```
1. Backup file → backups/<tipe>/<nama>.bak_YYYYMMDD
2. Edit file
3. Verifikasi perubahan berfungsi
4. Catat di DEV_DOCS jika perubahan signifikan
```

## 6. Verify Before Execute

**ALWAYS confirm understanding before making major changes.**

This is a **CRITICAL RULE** learned from real mistakes. Never skip verification for significant changes.

### When to Verify (MANDATORY):

**Always verify if ANY of these apply:**
- ✅ Major revision (>50 lines changed)
- ✅ Structural/architectural changes
- ✅ Deleting or renaming multiple files
- ✅ Ambiguous request (multiple interpretations possible)
- ✅ Request could impact multiple areas
- ✅ Removing existing features
- ✅ Changing user-facing behavior

**Can skip verification only if:**
- ❌ Trivial change (<10 lines)
- ❌ Fixing obvious typo
- ❌ Adding simple comment
- ❌ Formatting only (no logic change)

### Verification Workflow:

```
1. 📖 Read and understand user request
2. 🤔 Analyze what is being asked
3. ✅ Present your understanding to user
4. ⏸️ WAIT for user confirmation
5. ⚡ Execute ONLY after confirmed
6. 📝 Document changes
```

### How to Present Understanding:

**Format:**
```markdown
## 📋 Verifikasi Pemahaman

Berdasarkan permintaan Anda: "[quote user request]"

### Yang saya pahami:

**Struktur SEKARANG:**
[Show current state with clear structure]

**Struktur yang ANDA INGINKAN:**
[Show desired state with clear structure]

### Perubahan yang akan dilakukan:
1. ✅ [Change 1]
2. ✅ [Change 2]
3. ❌ TIDAK [What will NOT be changed]

### Dampak:
- [Impact 1]
- [Impact 2]

## ❓ Konfirmasi

Apakah pemahaman saya sudah BENAR?
```

### Examples:

**❌ WRONG (No Verification):**
```
User: "Make submenu aligned"
Agent: [Immediately deletes all menus and restructures everything]
Result: Wrong interpretation, major rework needed
```

**✅ RIGHT (With Verification):**
```
User: "Make submenu aligned"
Agent: "Let me verify my understanding first..."
Agent: [Presents clear before/after structure]
Agent: "Is this what you want?"
User: "Yes, correct"
Agent: [Executes with confidence]
Result: Correct implementation, no rework
```

### Red Flags (MUST Verify):

- 🚩 User says "make it better" (too vague)
- 🚩 Request involves "all", "everything", "entire" (broad scope)
- 🚩 You're about to delete >20 lines
- 🚩 You're about to change file structure
- 🚩 You're unsure which interpretation is correct
- 🚩 Change affects multiple components
- 🚩 User corrects you with "that's not what I meant"

### Benefits:

1. ✅ **Prevents Mistakes** - Catch misunderstandings early
2. ✅ **Saves Time** - No rework needed
3. ✅ **Builds Trust** - User sees you understand
4. ✅ **Clear Communication** - Both parties aligned
5. ✅ **Better Results** - Correct implementation first time

### Cost of NOT Verifying:

- ❌ Wrong implementation
- ❌ Wasted time (yours and user's)
- ❌ Need to restore from backup
- ❌ Lost user trust
- ❌ Frustration on both sides

---

**Remember:** 5 minutes of verification saves hours of rework.

**Golden Rule:** When in doubt, ALWAYS verify. Better to over-communicate than under-deliver.
