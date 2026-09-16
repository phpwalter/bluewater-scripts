# Repository Initialization

<!-- locale-guard:language-bar:start -->
<!-- locale-guard:language-bar:end -->

`bluewater init` detects the repository profile and creates a deterministic project-owned `bluewater.yml`.

The generated configuration explicitly lists every Bluewater 1.0 check. Language-specific checks remain enabled in the file but execute only when applicable to the resolved repository profile.

Initialization does not mutate Git submodules, create `.locale-guard.yml`, or install Git hooks. Those are explicit lifecycle operations because they may affect dependency revisions or developer workflow:

1. initialize the repository with `bluewater init`;
2. initialize/pin LocaleGuard according to repository policy;
3. create or review `.locale-guard.yml`;
4. run `bluewater hooks install` when hook enforcement is desired;
5. run `bluewater doctor` and `bluewater repo validate`.

Running `bluewater init` against an existing configuration fails unless `--force` is supplied. Forced initialization regenerates the same bytes for the same detected repository profile.
