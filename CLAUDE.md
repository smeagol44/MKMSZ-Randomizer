# MKMSZR — Claude Code instructions

Shared project rules (the same text the other assistant uses):

@AGENTS.md

Follow AGENTS.md. Where it names another tool's features (e.g. "Sol chats", "Work mode"), they don't apply here. The notes below add to it for Claude Code; if anything here seems to conflict with AGENTS.md or the user's instructions, ask.

## Claude Code specifics

- **Sessions are ephemeral.** Cloud containers are discarded; anything not committed and pushed is lost. The Wiki is the durable record: document findings there (via PR), not only in chat.
- **Branches and PRs.** Work on the branch assigned to the session. Open a PR only as part of the agreed task, and confirm with the user before opening one. The user reviews and merges; never push to `main`.
- **Quota.** Use plain `git` for commits/pushes/fetches. Use GitHub connector calls only when needed (e.g. opening a PR). Don't fetch full PR threads or CI logs, and don't subscribe to PR activity, unless asked.
- **ROMs.** The user supplies clean ROMs as uploads. Verify SHA-256 before use. Never copy ROMs into the repo. Disposable outputs go in the session scratchpad, named per AGENTS.md.
- **No emulator.** Don't install or run emulators. Static analysis (e.g. disassembling with capstone) is fine and is labelled static/implementation evidence.
- **External sources.** The `MKMSZR Research` Library isn't accessible here; ask the user for provenance when it's needed. `smeagol44/MKMSZ-Ghidra` can be cloned read-only for metadata; changes to it also go through a PR on that repo.
- **Read before writing.** Before editing a Wiki owner page, read its current text on the latest `main`. Keep edits minimal and keep the existing evidence labels and history.
