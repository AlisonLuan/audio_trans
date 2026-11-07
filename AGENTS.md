# AGENTS.md

## 1. Purpose and authority

This file defines how AI coding agents and automated contributors must
work in this repository.

The repository is a small Windows-oriented Python audio-transcription
project named `audio_trans`. Its current working-tree inventory is:

``` text
audio_trans/
├── .gitignore
├── AGENTS.md
├── audio/                 # Local recordings; ignored by Git
├── README.md
├── transcrever.bat
├── transcribe.py
└── .git/                  # Git metadata, not application source
```

The source and README show that the tool transcribes Portuguese locally
with OpenAI Whisper. First use may install dependencies and download the
selected model. The README documents Python 3.9+ and Windows 11; verify
compatibility rather than assuming every runtime or platform has been
tested.

When instructions conflict, use this precedence:

1.  Explicit instructions from the repository owner in the current task.
2.  Existing, verified project behavior and documented interfaces.
3.  This `AGENTS.md`.
4.  General conventions and an agent's preferences.

Do not treat assumptions in this document as evidence about
implementation.

## 2. Project understanding

### 2.1 Known facts

-   Repository/directory name: `audio_trans`.
-   `transcribe.py` requests Portuguese transcription with Whisper and
    writes a UTF-8 text file beside the input.
-   `transcrever.bat` accepts a file or folder and forwards model and
    timestamp options to the Python script.
-   `README.md` documents setup, invocation, and privacy behavior; keep
    it aligned with actual code.
-   `.gitignore` excludes local audio recordings and generated
    transcripts. Preserve these privacy protections.
-   First use may install PyTorch, Whisper, and FFmpeg support. Do not
    trigger those downloads during tests without explicit need.

### 2.2 Unknowns that must be verified

Before changing behavior, inspect the implementation and verify:

-   Python version requirements and supported Windows versions beyond
    those claimed by the README.
-   How the program is launched and whether the batch file is the
    primary entry point.
-   Required and optional Python packages, and how they are installed.
-   The model's actual runtime requirements and whether processing
    remains local for the changed workflow.
-   Supported audio containers, codecs, sample rates, channel layouts,
    and maximum input sizes.
-   How input files and directories are selected.
-   Whether language selection or automatic language detection is
    supported.
-   Whether timestamps, speaker labels, subtitles, plain text, or other
    output formats exist.
-   Output naming, destination-directory, overwrite, and duplicate-file
    behavior.
-   Temporary-file handling, logging, progress reporting, and error
    recovery.
-   Network, API-key, account, hardware, and model-download
    requirements, if any.
-   Existing tests, quality checks, and release or packaging procedures.
    No test suite or dependency manifest is present in the current
    repository inventory.

Do not add a feature merely because it is listed as an unknown. First
establish whether it is needed and agree on the intended behavior.

## 3. Mandatory agent workflow

For every task:

1.  **Inspect before editing.** Read the relevant source, README, batch
    file, ignore rules, and nearby code. Search for callers and related
    behavior before changing an interface.
2.  **Establish the baseline.** Check the Git working tree and current
    branch. Do not overwrite, discard, reset, or reformat unrelated user
    changes.
3.  **Understand the request.** Identify the requested outcome, affected
    files, compatibility constraints, and what must remain unchanged.
4.  **Plan proportionately.** Prefer the smallest change that fully
    solves the problem. Avoid speculative refactoring and unnecessary
    abstractions.
5.  **Implement consistently.** Follow existing naming, structure,
    dependency, and error-handling patterns unless there is a concrete
    reason to improve them.
6.  **Validate.** Run relevant tests and checks that are actually
    available. If a check cannot be run, state that clearly and explain
    why.
7.  **Review the diff.** Inspect every changed file for accidental
    edits, unrelated formatting, debug code, secrets, generated
    artifacts, and behavior changes.
8.  **Report precisely.** Summarize what changed, why, what was tested,
    and any remaining limitations.

Never claim that a command, test, or manual verification succeeded
unless it was actually run and its result observed.

### 3.1 Clarification policy

Ask the owner before proceeding when a missing decision could materially
change the implementation, data safety, user-visible behavior,
dependencies, or compatibility.

Do not ask questions whose answers can be established by inspecting the
repository. For low-risk, reversible decisions, follow the existing
project convention and state the assumption.

If the requested change cannot be implemented safely with the available
evidence, explain the blocker and request only the minimum necessary
information.

## 4. Personalization and communication

The repository owner values precise, technically grounded assistance.
Apply these rules to analysis, implementation, and reporting:

-   Be direct, structured, and specific. Avoid generic praise, filler,
    and unnecessary repetition.
-   Explain technical decisions with the terminology appropriate to
    Python, Windows automation, audio processing, and software
    engineering.
-   Separate **verified facts**, **assumptions**, **recommendations**,
    and **open questions**.
-   Do not fabricate source-code details, test results, dependency
    versions, benchmarks, or platform support.
-   Explain trade-offs when more than one implementation is reasonable;
    recommend one approach and give the reason.
-   Prefer actionable findings over broad commentary.
-   When reviewing code, prioritize defects, data-loss risks,
    regressions, security issues, and maintainability problems. Do not
    report stylistic preferences as defects.
-   Keep changes focused. Do not silently expand task scope.
-   Preserve existing user-facing behavior unless a change is explicitly
    requested or required to fix a defect.
-   Do not make architectural changes, introduce a framework, or add
    dependencies merely for convenience.
-   Do not address the owner by a personal name unless explicitly
    requested.
-   Use English for repository documentation and technical artifacts
    unless the owner requests another language. Preserve existing
    user-facing language and wording where relevant.

### 4.1 Review output

For code reviews, lead with actionable problems, ordered by severity.
For each finding, include:

-   The affected file and location, when available.
-   The concrete failure mode or risk.
-   The conditions under which it occurs.
-   A practical correction.

Do not pad a review with items that are already correct. Distinguish
confirmed defects from risks that require runtime verification.

## 5. Python engineering standards

These are default engineering rules, not claims about the current code
style. Follow established project conventions where they are sound.

### 5.1 Correctness and maintainability

-   Keep functions focused and make side effects visible.
-   Use descriptive names for variables, functions, classes, and
    constants.
-   Prefer straightforward control flow over clever or compressed
    expressions.
-   Use standard-library functionality when it is sufficient; do not add
    a dependency without a clear benefit.
-   Add type annotations where they improve clarity and are compatible
    with the project's supported Python version.
-   Use `pathlib.Path` for new filesystem code unless the existing
    interface or a library requires another representation.
-   Avoid broad exception handling. Catch exceptions at a boundary where
    the program can provide useful context or recover safely.
-   Do not suppress exceptions or return success-shaped values after a
    failure.
-   Keep configuration separate from processing logic when doing so
    makes behavior easier to understand and test.
-   Avoid global mutable state unless the existing architecture requires
    it.
-   Do not introduce concurrency or parallel processing without
    understanding the transcription engine's thread-safety, resource
    use, and ordering requirements.

### 5.2 Compatibility

-   Verify the supported Python version from project files,
    documentation, and existing syntax before using newer language
    features.
-   Do not assume that the latest Python release is installed on the
    owner's Windows machine.
-   Avoid platform-specific behavior in shared Python code unless it is
    intentional and documented.
-   Where Windows-specific behavior is required, test path handling,
    quoting, encoding, and subprocess invocation on Windows or clearly
    state that it was not tested.
-   Do not change dependency versions or installation instructions
    without checking compatibility with the project's current
    environment.

### 5.3 Error messages and diagnostics

-   Error messages should identify the operation that failed and, where
    safe, the relevant file or setting.
-   Preserve the original exception as diagnostic context when
    appropriate.
-   Do not expose API keys, access tokens, private paths, or sensitive
    audio content in logs.
-   Do not turn recoverable per-file errors into silent success.
-   If batch processing exists, make it clear which input failed and
    whether other inputs continued; preserve the behavior unless the
    task requests a change.

### 5.4 Code quality

-   Follow the formatting and linting tools already configured by the
    repository.
-   Do not introduce a formatter or linter solely to satisfy personal
    preference.
-   Avoid unrelated whole-file formatting changes.
-   Remove temporary debugging statements before finalizing a change.
-   Keep comments focused on intent, constraints, and non-obvious
    behavior rather than restating code.

## 6. Audio and transcription integrity

Transcription output is derived data. Protect the original recording and
make processing outcomes understandable.

### 6.1 Input preservation

-   Treat original audio files as user data.
-   Never delete, move, rename, overwrite, or modify an input recording
    unless the owner explicitly requests that behavior.
-   Do not perform destructive conversion in place.
-   If conversion or normalization is required, use a separate temporary
    or output file and handle cleanup safely.
-   Avoid scanning unrelated directories or recursively processing broad
    paths unless that is the documented behavior and the user requested
    it.
-   Validate that an input exists and is a supported file before
    beginning expensive processing, using the project's actual
    supported-input rules.

### 6.2 Transcription fidelity

-   Do not silently alter the transcription language, model, decoding
    options, or accuracy/speed trade-offs.
-   Do not invent words, punctuation, speaker identities, timestamps, or
    metadata.
-   Preserve the transcription engine's actual output semantics unless
    post-processing is explicitly part of the established design.
-   Any text cleanup, punctuation normalization, translation,
    summarization, or speaker-labeling step must be distinguished from
    verbatim transcription.
-   Do not claim that a transcript is verbatim if the implementation
    performs transformations that can change meaning.
-   Be careful with multilingual speech, proper names, technical
    vocabulary, numbers, and domain-specific terminology.
-   If confidence scores or uncertainty indicators are available, do not
    discard or misrepresent them without a clear requirement.

### 6.3 Output safety

-   Determine the current output naming and overwrite policy before
    changing it.
-   Never silently overwrite an existing transcript or unrelated file.
-   If the existing application intentionally overwrites outputs,
    preserve that behavior unless asked to change it; make the risk
    explicit when relevant.
-   Use safe, deterministic output paths and handle filenames containing
    spaces, accents, non-ASCII characters, and Windows-reserved
    characters.
-   Ensure a failed or interrupted transcription does not leave a
    partial file that looks like a completed result.
-   If atomic output writing is appropriate, write to a temporary
    sibling file and replace the destination only after successful
    completion.
-   Do not change transcript encoding or line-ending conventions without
    checking downstream compatibility.

### 6.4 Resource and operational behavior

-   Audio processing can be CPU-, memory-, disk-, GPU-, and
    network-intensive. Avoid unnecessary copies and repeated model
    initialization.
-   Do not add automatic downloads, uploads, telemetry, or external
    service calls without explicit justification and clear
    documentation.
-   If the existing engine downloads models or contacts a service,
    document the actual behavior and failure modes based on the code.
-   Do not add automatic deletion of temporary data unless its ownership
    and lifecycle are clear.
-   Report progress honestly; do not display fabricated percentage
    completion.

## 7. Windows and batch-file requirements

`transcrever.bat` is part of the known repository inventory. Treat it as
a user-facing interface until inspection proves otherwise.

-   Read the complete batch file before changing it.
-   Preserve existing command-line behavior and argument forwarding
    unless the task explicitly changes the interface.
-   Quote paths and arguments correctly, especially paths containing
    spaces, parentheses, ampersands, and non-ASCII characters.
-   Be deliberate about `%` expansion, delayed expansion, `&`, `^`, and
    shell metacharacters.
-   Use `setlocal` where appropriate to prevent environment-variable
    changes leaking into the caller's shell.
-   Check and propagate meaningful exit codes from Python and any
    external commands.
-   Do not report success when the Python process failed.
-   Avoid hard-coded machine-specific paths, usernames, drive letters,
    or installed executable locations.
-   Do not assume that the current working directory is the batch file's
    directory. If the script needs repository-relative paths, derive
    them robustly from the script location.
-   Preserve user-supplied arguments and avoid unsafe command-string
    construction.
-   Be explicit about console encoding when changing output that may
    contain accented or non-English text.
-   Do not assume PowerShell syntax is valid in a `.bat` file.
-   Keep the batch file simple; do not duplicate substantial application
    logic in batch commands.

For any change to the batch launcher, validate at least the intended
invocation and error/exit-code behavior on Windows when possible. If
Windows execution is unavailable, perform static inspection and disclose
the limitation.

## 8. Dependencies, configuration, and secrets

-   Inspect the actual dependency declaration and installation
    instructions before adding or changing packages.
-   Check the current repository for a `requirements.txt`,
    `pyproject.toml`, virtual environment, or lockfile before adding or
    changing dependency instructions.
-   If a dependency is added, explain why the standard library or
    existing dependencies are insufficient.
-   Pin or constrain versions only according to the project's
    established dependency-management strategy.
-   Do not commit credentials, API keys, access tokens, personal audio,
    private transcripts, model weights, caches, or local environment
    files.
-   Use the existing configuration mechanism. Do not introduce a new
    secrets-management system without need.
-   Validate required configuration at startup and provide a clear,
    actionable error without printing secret values.
-   Do not change `.gitignore` casually. Confirm that ignore rules
    protect generated files and local secrets without hiding required
    source or documentation.

## 9. Testing and validation

The current repository has no test suite or test framework. Recheck for
tests before adding new ones, and use the checks that actually exist.

### 9.1 Before changing code

-   Check the Git working tree and avoid disturbing uncommitted changes.
-   Read the current README and identify the documented invocation.
-   Identify the current Python and external-tool prerequisites from the
    project itself.
-   Determine whether tests, fixtures, linting, formatting, or
    type-checking configuration exists.

### 9.2 After changing code

Run the narrowest relevant checks first, then broader checks where
practical:

-   Python syntax/bytecode compilation using the project's supported
    interpreter.
-   Existing automated tests, if present.
-   Existing lint, format-check, or type-check commands, if configured.
-   A safe command-line smoke test using a non-sensitive sample or a
    deliberately invalid input.
-   A Windows batch-file invocation test when the batch file is affected
    and Windows is available.
-   A regression check for the original behavior and any documented
    command-line interface affected by the change.

Do not invent a test command or claim that a test suite exists. If no
tests are present, say so and perform appropriate non-destructive
checks.

### 9.3 Test-data policy

-   Prefer short, synthetic, public-domain, or explicitly authorized
    audio samples.
-   Do not upload private recordings to external services for testing
    without authorization.
-   Do not commit test recordings or generated transcripts unless they
    are intentionally part of the project and safe to distribute.
-   Keep temporary test artifacts outside tracked source directories
    where practical.
-   Verify that tests do not overwrite or delete user data.

## 10. Documentation requirements

Update `README.md` when a change affects user-visible setup, supported
inputs, invocation, configuration, outputs, dependencies, or
troubleshooting.

Documentation must:

-   Match the implementation, not an intended future design.
-   Show commands with correct Windows quoting and paths where
    applicable.
-   Distinguish required from optional prerequisites.
-   Explain environment variables or configuration only if they actually
    exist.
-   Avoid promising support for formats, languages, engines, or
    platforms that have not been verified.
-   Include meaningful failure and recovery guidance where appropriate.

Do not duplicate the entire README in `AGENTS.md`. This file governs
agent behavior; the README explains how users operate the application.

## 11. Git and repository hygiene

-   Do not run destructive Git commands such as `reset --hard`,
    `clean -fd`, forced checkout, or history rewriting unless the owner
    explicitly requests them and the affected data is understood.
-   Do not amend, squash, rebase, commit, or push unless explicitly
    requested.
-   Do not modify remotes, branch configuration, hooks, or repository
    metadata as part of an ordinary code change.
-   Do not include generated files, caches, virtual environments, audio
    recordings, transcripts, secrets, or temporary logs in commits
    unless explicitly intended.
-   Review `git diff` and `git status` before finishing.
-   Preserve unrelated changes made by the owner or other contributors.
-   Keep changes limited to the task. Avoid renaming files or
    reorganizing the repository without a clear benefit and approval
    where behavior or workflow may change.

## 12. Security and privacy

Audio may contain personal, confidential, or commercially sensitive
information.

-   Treat recordings and transcripts as private by default.
-   Do not transmit audio or transcript contents to an external endpoint
    unless that is already an explicit, documented part of the
    application or the owner authorizes it.
-   Do not add telemetry, analytics, crash uploads, or background
    network behavior without explicit approval.
-   Do not log full transcripts, audio payloads, credentials, or
    personal data unnecessarily.
-   Validate file paths and external command arguments; avoid shell
    injection and unsafe path concatenation.
-   Do not execute untrusted downloaded scripts or binaries as part of
    setup.
-   Do not weaken TLS verification, authentication, or other security
    controls to work around a connectivity problem.
-   Explain any privacy implications of changing the transcription
    engine or processing location.

## 13. Change-specific decision rules

### Bug fixes

-   Reproduce or identify the failure path before changing code.
-   Fix the underlying cause rather than masking symptoms.
-   Add a regression test when a suitable test structure exists.
-   Preserve unrelated behavior.

### New features

-   Confirm expected inputs, outputs, defaults, failure behavior, and
    compatibility.
-   Reuse existing dependencies and interfaces where reasonable.
-   Document user-visible behavior.
-   Avoid speculative features and hidden network activity.

### Refactoring

-   Preserve externally observable behavior.
-   Avoid combining broad refactoring with unrelated feature work.
-   Use tests or before/after checks to support behavioral equivalence.
-   Do not refactor solely to match a preferred style.

### Dependency changes

-   Verify package maintenance, compatibility, licensing implications
    where relevant, and installation impact.
-   Explain size, runtime, platform, and security implications for
    significant dependencies.
-   Update the authoritative dependency declaration and setup
    documentation together.

### Performance changes

-   Measure or identify the actual bottleneck before optimizing.
-   Preserve transcription quality and output correctness.
-   Consider memory, CPU/GPU availability, model initialization, and
    I/O.
-   Report the measurement conditions; do not make unsupported speed
    claims.

## 14. Definition of done

A task is complete only when all applicable conditions are met:

-   The requested behavior is implemented and its scope is respected.
-   Existing interfaces and documented behavior are preserved unless
    intentionally changed.
-   Input recordings and unrelated user files remain untouched.
-   Errors are handled clearly and do not masquerade as successful
    completion.
-   Relevant tests and checks have been run, or unavailable checks are
    explicitly disclosed.
-   Documentation is updated when user-facing behavior or setup changes.
-   The final diff contains no unrelated edits, secrets, or temporary
    artifacts.
-   The completion report states:
    1.  What changed.
    2.  Which files changed.
    3.  What validation was performed and its observed result.
    4.  What was not tested or remains uncertain.

## 15. Guidance for future refinement of this file

Keep this file aligned with verified source and documentation. Update
project-specific details when the implementation changes, including:

-   Exact Python version and dependency installation commands.
-   Actual transcription backend and model choices.
-   Real CLI syntax and batch-file behavior.
-   Supported audio formats and output conventions.
-   Existing tests and exact validation commands.
-   Known limitations and established project design decisions.

Base refinements on direct evidence from the repository or an explicit
decision from the owner. Remove obsolete guidance and do not turn
guesses into repository facts.
