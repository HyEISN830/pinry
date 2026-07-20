# hyeisn-Pinry Agent Quickstart

This document defines the shared local visual-debug workflow for this repository.
It is intended for Codex/agent sessions and team members who need a real Django
backend, deterministic Pin/Comic data, and reproducible Chrome screenshots.

The order is intentional: establish the Chrome debugging contract first, then
prepare the isolated runtime.

## 1. Chrome debugging contract

### 1.1 Reuse one dedicated Chrome window

- Use Chrome, not the internal browser, for local UI debugging and visual QA.
- Create one dedicated Chrome debug window only when none exists. Reuse that
  window and its tabs across tasks; do not repeatedly create new windows.
- Control that window through the Chrome browser-control interface. Keep the
  work silent: do not use Computer Use to take over the desktop mouse or type
  into Chrome through OS-level input simulation.
- Do not claim, navigate, close, reorder, or otherwise modify the user's other
  Chrome windows and tabs.
- Keep the local debug page open when handing work to another task unless the
  user explicitly asks to close it.

### 1.2 Use the integrated URL

The canonical visual-debug origin is:

```text
http://127.0.0.1:8000/
```

Always use `127.0.0.1`; do not mix it with `localhost`. Keeping one origin
prevents avoidable Cookie, Session, CSRF, and local-storage differences.

Use these routes for focused checks:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/comics
http://127.0.0.1:8000/api/v2/pins/?limit=1
http://127.0.0.1:8000/api/v2/comics/?limit=1
```

Do not use `http://127.0.0.1:8080/static/spa/` for integrated acceptance or
screenshots. Vue's history router can interpret `/static/spa/` as an
application route and show PageNotFound. Port 8080 is only for an explicitly
requested HMR investigation; normal QA is served by Django on port 8000.

### 1.3 Observe before interacting

- Before a screenshot, verify `/`, the relevant API route, and at least one
  `/media/` request return HTTP 200. Never accept a backend 404 as UI state.
- Prefer DOM/Playwright inspection for element state and Chrome tab screenshots
  for visual state. A failed desktop screenshot does not imply that Chrome tab
  screenshots are unavailable.
- Inspect the Chrome console after navigation and after each frontend rebuild.
- After source/build changes, reload the existing tab before inspecting it.
- Use stable DOM attributes or accessible names. Do not guess selectors or use
  positional clicks when a stable locator is available.
- For responsive checks, temporarily set an explicit Chrome viewport, capture
  the result, then reset the override unless the user asks to retain it.

### 1.4 Animation and screenshot state

- For splash-animation work, set `pinry.motion.reduce` to `false`, reload, and
  capture the intended animation frame or recording.
- For Pin/Comic layout work, either wait for the splash to finish or set
  `pinry.motion.reduce` to `true` before reloading. Record which state was used.
- Ordinary tabs in one Chrome profile share cookies, so separate tabs alone do
  not isolate authentication. The default single-window workflow is: verify
  anonymous state, log in, verify owner state, then explicitly log out and
  reload before returning to anonymous QA. Create an additional isolated
  profile/incognito window only with explicit user approval and after confirming
  that Chrome control is available there. Always label the state being verified.
- Chrome screenshots exported to disk belong under:

```text
%LOCALAPPDATA%\hyeisn-pinry\visual-debug\artifacts\screenshots\
```

Screenshots, recordings, console dumps, and downloaded media are runtime
artifacts. Do not commit them unless a user explicitly requests a repository
artifact.

## 2. Isolation and safety contract

The temporary runtime must live outside the repository. Its default root is:

```text
%LOCALAPPDATA%\hyeisn-pinry\visual-debug
```

On the machine where this workflow was first verified, that expands to:

```text
C:\Users\Administrator\AppData\Local\hyeisn-pinry\visual-debug
```

Expected layout:

```text
visual-debug\
├─ tools\uv\                 # portable uv.exe and uvx.exe
├─ downloads\                # downloaded tool archives
├─ python\                   # uv-managed CPython 3.9
├─ .venv\                    # isolated project environment
├─ cache\                    # uv package/download cache
├─ data\
│  ├─ debug.sqlite3          # isolated SQLite database
│  └─ media\                 # isolated originals and thumbnails
├─ generated\                # runtime-only seed/helper scripts
├─ logs\                     # Django stdout/stderr logs
├─ state\
│  ├─ runtime-info.txt       # local URLs and demo credentials
│  └─ runtime.pid            # active Django PID, when running
└─ artifacts\screenshots\   # optional Chrome captures
```

Mandatory boundaries:

- Never use, inspect, overwrite, migrate, or delete `C:\data`, `/data`, a
  production SQLite file, or production media for visual debugging.
- Never run migrations or seed data until Django's effective database and
  media paths have been printed and compared with the expected runtime paths.
- `pinry/settings/local_settings.py` is loaded after the development settings
  and can override environment values. Treat a path mismatch as a hard stop.
- Bind Django only to `127.0.0.1:8000`; do not expose the debug server on
  `0.0.0.0` or a LAN interface.
- Do not use the Makefile `serve` target for this workflow because it binds to
  `0.0.0.0`.
- Do not use `docker-compose.example.yml` for this workflow. It exposes port
  2048 and uses an older frontend flow that does not match the current proxy.
- Do not commit the runtime root, database, media, seed output, logs, PID files,
  credentials, screenshots, or generated SPA build output.

## 3. PowerShell session variables

Run commands from the repository root. Establish the same variables in every
new PowerShell session that manages the runtime:

```powershell
$RepoRoot = (Resolve-Path '.').Path
if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot 'manage.py'))) {
    throw 'Run this workflow from the hyeisn-pinry repository root.'
}

$RuntimeRoot = Join-Path $env:LOCALAPPDATA 'hyeisn-pinry\visual-debug'
$Uv = Join-Path $RuntimeRoot 'tools\uv\uv.exe'
$Python = Join-Path $RuntimeRoot '.venv\Scripts\python.exe'

$env:UV_PYTHON_INSTALL_DIR = Join-Path $RuntimeRoot 'python'
$env:UV_CACHE_DIR = Join-Path $RuntimeRoot 'cache'
$env:DJANGO_SETTINGS_MODULE = 'pinry.settings.development'
$env:SQLITE_DATABASE = Join-Path $RuntimeRoot 'data\debug.sqlite3'
$env:MEDIA_ROOT = Join-Path $RuntimeRoot 'data\media'
$env:PINRY_VISUAL_DEBUG_RUNTIME_ROOT = $RuntimeRoot
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUNBUFFERED = '1'
$env:IMAGE_FETCH_ASYNC_ENABLED = '0'
```

## 4. First-time portable Python setup

This repository uses Django 2.2.28. Do not run it with the machine's default
Python 3.12/3.14. The verified local runtime uses uv-managed CPython 3.9 and
does not change the system PATH or Windows registry.

Create the runtime directories:

```powershell
@(
    'tools\uv',
    'downloads',
    'python',
    '.venv',
    'cache',
    'data\media',
    'generated',
    'logs',
    'state',
    'artifacts\screenshots'
) | ForEach-Object {
    New-Item -ItemType Directory -Force `
        -Path (Join-Path $RuntimeRoot $_) | Out-Null
}
```

Download portable uv without running a global installer:

```powershell
$UvZip = Join-Path $RuntimeRoot 'downloads\uv-x86_64-pc-windows-msvc.zip'

Invoke-WebRequest `
    -Uri 'https://github.com/astral-sh/uv/releases/download/0.11.29/uv-x86_64-pc-windows-msvc.zip' `
    -OutFile $UvZip

$ExpectedUvZipSha256 = 'A047D55651BC3E0CA24595B25EC4CFCB10F9DCA9FB56514E661269B37D4FAE68'
$ActualUvZipSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $UvZip).Hash

if ($ActualUvZipSha256 -ne $ExpectedUvZipSha256) {
    throw "uv archive checksum mismatch: $ActualUvZipSha256"
}

Expand-Archive `
    -LiteralPath $UvZip `
    -DestinationPath (Join-Path $RuntimeRoot 'tools\uv') `
    -Force

& $Uv --version
```

Install Python 3.9 and create the isolated virtual environment:

```powershell
& $Uv python install 3.9 `
    --no-bin `
    --no-registry `
    --compile-bytecode

& $Uv venv `
    (Join-Path $RuntimeRoot '.venv') `
    --python 3.9 `
    --managed-python

& $Python --version
```

Install the tracked runtime requirements and the development-settings module:

```powershell
& $Uv pip install --python $Python -r (Join-Path $RepoRoot 'requirements.txt')
& $Uv pip install --python $Python 'django-extensions==3.1.5'

& $Python -c `
    'import django, rest_framework, PIL; print(django.get_version(), rest_framework.VERSION, PIL.__version__)'
```

The first verified environment reported:

```text
uv 0.11.29
Python 3.9.25
Django 2.2.28
DRF 3.13.1
Pillow 9.1.1
```

`requirements.txt` currently uses a pinned package index and hashes. If that
index is unavailable, stop and review the dependency source; do not silently
upgrade Django or switch to the system Python. The Dockerfile/Poetry lock is
the fallback source of truth for a deliberate dependency-parity rebuild.

## 5. Build the Vue SPA

Fresh clones do not contain the generated SPA assets because these paths are
Git-ignored:

```text
pinry/static/spa/
pinry/templates/index.html
```

The project baseline is Node 18 with pnpm 9. In native PowerShell, set
`NODE_OPTIONS` separately instead of invoking the POSIX-style assignment in
the package script:

```powershell
Push-Location (Join-Path $RepoRoot 'pinry-spa')
$PreviousNodeOptions = $env:NODE_OPTIONS

try {
    $env:NODE_OPTIONS = '--openssl-legacy-provider'
    pnpm.cmd install --frozen-lockfile
    pnpm.cmd exec vue-cli-service lint --no-fix
    pnpm.cmd exec vue-cli-service build
}
finally {
    if ($null -eq $PreviousNodeOptions) {
        Remove-Item Env:NODE_OPTIONS -ErrorAction SilentlyContinue
    }
    else {
        $env:NODE_OPTIONS = $PreviousNodeOptions
    }
    Pop-Location
}
```

Do not run `collectstatic` for this local workflow; it creates unrelated
generated output. Django DEBUG mode serves the built SPA/static files directly.

## 6. Verify effective paths before every write

Run this guard before `migrate`, seed, reset, or any command that can write to
the database or media storage:

```powershell
$EffectiveJson = & $Python -c @'
import json
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pinry.settings.development')
import django
django.setup()
from django.conf import settings
print(json.dumps({
    'database': settings.DATABASES['default']['NAME'],
    'media': settings.MEDIA_ROOT,
    'engine': settings.DATABASES['default']['ENGINE'],
    'debug': settings.DEBUG,
}))
'@

$Effective = ($EffectiveJson | Select-Object -Last 1) | ConvertFrom-Json
$ExpectedDatabase = [IO.Path]::GetFullPath($env:SQLITE_DATABASE)
$ExpectedMedia = [IO.Path]::GetFullPath($env:MEDIA_ROOT)
$ActualDatabase = [IO.Path]::GetFullPath([string]$Effective.database)
$ActualMedia = [IO.Path]::GetFullPath([string]$Effective.media)

if ($ActualDatabase -ine $ExpectedDatabase) {
    throw "Unsafe database path: $ActualDatabase"
}
if ($ActualMedia -ine $ExpectedMedia) {
    throw "Unsafe media path: $ActualMedia"
}
if ($Effective.engine -ne 'django.db.backends.sqlite3' -or -not $Effective.debug) {
    throw 'Visual debug requires DEBUG SQLite development settings.'
}
```

Only after this guard succeeds:

```powershell
& $Python (Join-Path $RepoRoot 'manage.py') check
& $Python (Join-Path $RepoRoot 'manage.py') migrate --noinput
```

## 7. Runtime-only visual seed

The full seed helper belongs at:

```text
%LOCALAPPDATA%\hyeisn-pinry\visual-debug\generated\seed_visual_debug.py
```

It is deliberately outside the repository. When restoring an archived debug
runtime, restore `generated/` with `data/`. When creating a fresh helper, it
must obey all of these rules:

- Call the effective-path guard first and independently refuse to run unless
  both SQLite and media resolve inside the exact runtime root.
- Never fetch images from the network and never copy production media. Generate
  deterministic local JPEG/PNG fixtures with Pillow.
- Generate every required `thumbnail`, `medium`, `standard`, and `square`
  derivative; the API expects all four.
- Use a normal, non-staff, non-superuser `visual_debug` account and `.invalid`
  email/URLs only. Generate a new random password with `secrets`; do not print
  it or use it for any real account.
- Prefix titles, board names, tags, captions, actor keys, and searchable marker
  text with `VISUAL_DEBUG_`.
- Treat reseeding as a destructive but repeatable reset of the isolated debug
  database, not as a stable-ID update. It may reset all records only after
  proving that the database is the exact visual-debug SQLite file. IDs may
  change on every reseed.
- For authenticated-like fixtures, use the application's actor key format
  `user:<user-id>` so `viewer_liked` exercises the real path.
- Atomically refresh local-only credentials and current object IDs in
  `$RuntimeRoot\state\runtime-info.txt` after every successful reseed. Never
  print the password or write it to the repository.

The reference dataset contains:

- 14 Pins: portrait, landscape, square, tall, panorama, long/empty descriptions,
  zero/multiple tags, source/no-source, likes, and one private Pin.
- 6 Comics and 24 ComicPages: 1/3/4/5/8-page cases, mixed ratios, long/empty
  metadata, sources, likes, and one private Comic.
- 2 Boards: one public mixed-ratio board and one private board.
- Fully local originals and all four thumbnail sizes.

Run the helper from the repository root so project modules are importable:

```powershell
$env:PYTHONPATH = $RepoRoot
& $Python (Join-Path $RuntimeRoot 'generated\seed_visual_debug.py')
```

The currently verified local demo account is recorded in
`$RuntimeRoot\state\runtime-info.txt`. It is a disposable loopback-only account;
never reuse its password for any real account or expose this server to a network.

## 8. Start Django silently

Port 8000 must be free. Do not kill an unknown process merely to claim it:

```powershell
$Listener = Get-NetTCPConnection `
    -State Listen `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue

if ($Listener) {
    throw "Port 8000 is already owned by PID $($Listener.OwningProcess)."
}
```

Start one non-reloading Django process in the background:

Immediately before this block, rerun the complete effective-path guard from
section 6. Starting the server can write Sessions, Likes, and uploads, so a
stale or overridden path is not acceptable even when migrations already ran.

```powershell
$StdoutLog = Join-Path $RuntimeRoot 'logs\django.stdout.log'
$StderrLog = Join-Path $RuntimeRoot 'logs\django.stderr.log'
$PidFile = Join-Path $RuntimeRoot 'state\runtime.pid'
$ManagePy = [IO.Path]::GetFullPath((Join-Path $RepoRoot 'manage.py'))
$ManagePyArgument = '"{0}"' -f $ManagePy

$Launcher = Start-Process `
    -FilePath $Python `
    -ArgumentList @(
        $ManagePyArgument,
        'runserver',
        '127.0.0.1:8000',
        '--noreload'
    ) `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $StdoutLog `
    -RedirectStandardError $StderrLog `
    -WindowStyle Hidden `
    -PassThru

$RuntimePrefix = [IO.Path]::GetFullPath($RuntimeRoot).TrimEnd('\') + '\'
$ExpectedManagePyRegex = [regex]::Escape($ManagePy)
$Listener = $null
$ServerProcess = $null
$Ready = $false
$UnexpectedListener = $false

for ($Attempt = 0; $Attempt -lt 40; $Attempt++) {
    $Candidate = Get-NetTCPConnection `
        -State Listen `
        -LocalAddress '127.0.0.1' `
        -LocalPort 8000 `
        -ErrorAction SilentlyContinue |
        Select-Object -First 1

    if ($Candidate) {
        $CandidateProcess = Get-CimInstance Win32_Process `
            -Filter "ProcessId = $($Candidate.OwningProcess)" `
            -ErrorAction SilentlyContinue

        if ($CandidateProcess) {
            $CandidateExecutable = [IO.Path]::GetFullPath(
                $CandidateProcess.ExecutablePath
            )
            $IsExpectedCandidate = (
                $CandidateExecutable.StartsWith(
                    $RuntimePrefix,
                    [StringComparison]::OrdinalIgnoreCase
                ) -and
                $CandidateProcess.CommandLine -match $ExpectedManagePyRegex -and
                $CandidateProcess.CommandLine -match
                    '\brunserver\s+127\.0\.0\.1:8000\b'
            )

            if (-not $IsExpectedCandidate) {
                $UnexpectedListener = $true
                break
            }

            $ServerProcess = $CandidateProcess
            try {
                $RootStatus = (Invoke-WebRequest `
                    -UseBasicParsing `
                    -Uri 'http://127.0.0.1:8000/' `
                    -TimeoutSec 1
                ).StatusCode
                if ($RootStatus -eq 200) {
                    $Listener = $Candidate
                    $Ready = $true
                    break
                }
            }
            catch {
                # The socket can appear shortly before Django is HTTP-ready.
            }
        }
    }

    if ($Launcher.HasExited) {
        break
    }
    Start-Sleep -Milliseconds 250
}

if (-not $Ready) {
    if ($ServerProcess) {
        Stop-Process -Id $ServerProcess.ProcessId -ErrorAction SilentlyContinue
    }
    if (-not $Launcher.HasExited) {
        $LauncherPath = [IO.Path]::GetFullPath($Launcher.Path)
        if ($LauncherPath.StartsWith(
            $RuntimePrefix,
            [StringComparison]::OrdinalIgnoreCase
        )) {
            Stop-Process -Id $Launcher.Id -ErrorAction SilentlyContinue
        }
    }
    Get-Content -LiteralPath $StderrLog -Tail 50 -ErrorAction SilentlyContinue
    if ($UnexpectedListener) {
        throw 'Port 8000 was claimed by an unexpected process; nothing was killed.'
    }
    throw 'Django did not become ready on 127.0.0.1:8000.'
}

# The Windows venv executable may be a redirector that launches the real
# CPython child. Record the process that actually owns the listening socket.
$ServerPid = [int]$Listener.OwningProcess
$ServerPid | Set-Content -LiteralPath $PidFile -NoNewline
```

Windows does not run Gunicorn here. `--noreload` is intentional: it leaves one
stable listening process that can be verified and stopped safely. A short-lived
or waiting venv redirector parent may coexist with the real CPython listener.

Health checks:

```powershell
(Invoke-WebRequest -UseBasicParsing `
    'http://127.0.0.1:8000/').StatusCode

$Pins = (Invoke-WebRequest -UseBasicParsing `
    'http://127.0.0.1:8000/api/v2/pins/?limit=1').Content | ConvertFrom-Json

$Comics = (Invoke-WebRequest -UseBasicParsing `
    'http://127.0.0.1:8000/api/v2/comics/?limit=1').Content | ConvertFrom-Json

$Pins.count
$Comics.count
```

With the reference seed, anonymous APIs report 13 public Pins and 5 public
Comics. Fetch a thumbnail URL from the Pin response and verify it returns
`image/jpeg` or `image/png` with HTTP 200 before opening Chrome.

## 9. Daily UI-debug loop

1. Re-establish the PowerShell variables from section 3.
2. Confirm the PID/port and run the root, API, and media health checks.
3. Open or reuse the single dedicated Chrome debug window at
   `http://127.0.0.1:8000/`.
4. Inspect anonymous Home, Pin, Comics, and Comic Reader states.
5. Read `$RuntimeRoot\state\runtime-info.txt` when an authenticated owner state
   is required; do not save the disposable password to Chrome. After owner QA,
   explicitly log out and reload before treating the window as anonymous again.
6. After frontend changes, run lint/build, reload the same Chrome tab, inspect
   the console, and capture the relevant desktop/mobile viewport.
7. Store any exported captures under `$RuntimeRoot\artifacts\screenshots`.
8. Run proportional lint/build/backend checks before signing off a change.

## 10. Stop Django safely

Never stop a process solely because its PID appears in a stale file. Confirm
that both its executable and command line belong to this runtime:

```powershell
$PidFile = Join-Path $RuntimeRoot 'state\runtime.pid'

if (Test-Path -LiteralPath $PidFile) {
    $ServerPid = [int](Get-Content -Raw -LiteralPath $PidFile)
    $Process = Get-CimInstance Win32_Process `
        -Filter "ProcessId = $ServerPid" `
        -ErrorAction SilentlyContinue

    if ($null -ne $Process) {
        $RuntimePrefix = [IO.Path]::GetFullPath($RuntimeRoot).TrimEnd('\') + '\'
        $Executable = [IO.Path]::GetFullPath($Process.ExecutablePath)
        $ExpectedManagePy = [regex]::Escape(
            [IO.Path]::GetFullPath((Join-Path $RepoRoot 'manage.py'))
        )

        $IsRuntimePython = $Executable.StartsWith(
            $RuntimePrefix,
            [StringComparison]::OrdinalIgnoreCase
        )
        $IsExpectedServer = (
            $Process.CommandLine -match $ExpectedManagePy -and
            $Process.CommandLine -match
                '\brunserver\s+127\.0\.0\.1:8000\b'
        )
        $OwnsExpectedSocket = [bool](
            Get-NetTCPConnection `
                -State Listen `
                -LocalAddress '127.0.0.1' `
                -LocalPort 8000 `
                -ErrorAction SilentlyContinue |
                Where-Object { $_.OwningProcess -eq $ServerPid }
        )

        if (-not ($IsRuntimePython -and $IsExpectedServer -and $OwnsExpectedSocket)) {
            throw 'PID belongs to another process; refusing to stop it.'
        }

        Stop-Process -Id $ServerPid -ErrorAction Stop
        Wait-Process -Id $ServerPid -Timeout 10 -ErrorAction SilentlyContinue
    }

    Remove-Item -LiteralPath $PidFile -Force
}
```

## 11. Archive and migrate

Stop Django before archiving. Usually archive only `data/`, `generated/`, and
selected state information. The virtual environment and downloaded Python are
machine-specific and should be rebuilt on the destination machine.

```powershell
$PidFile = Join-Path $RuntimeRoot 'state\runtime.pid'
if (Test-Path -LiteralPath $PidFile) {
    throw 'runtime.pid still exists. Stop and verify Django before archiving.'
}

$ArchiveListener = Get-NetTCPConnection `
    -State Listen `
    -LocalPort 8000 `
    -ErrorAction SilentlyContinue

if ($ArchiveListener) {
    $ArchiveProcess = Get-CimInstance Win32_Process `
        -Filter "ProcessId = $($ArchiveListener.OwningProcess)" `
        -ErrorAction SilentlyContinue
    $RuntimePrefix = [IO.Path]::GetFullPath($RuntimeRoot).TrimEnd('\') + '\'

    if (
        $ArchiveProcess -and
        [IO.Path]::GetFullPath($ArchiveProcess.ExecutablePath).StartsWith(
            $RuntimePrefix,
            [StringComparison]::OrdinalIgnoreCase
        )
    ) {
        throw 'The visual-debug Django process is still running.'
    }
}

$ArchiveDirectory = Join-Path `
    $env:USERPROFILE `
    'Documents\hyeisn-pinry-debug-archives'

New-Item -ItemType Directory -Force -Path $ArchiveDirectory | Out-Null

$Archive = Join-Path $ArchiveDirectory (
    'hyeisn-pinry-visual-debug-{0}.zip' -f (Get-Date -Format 'yyyyMMdd-HHmmss')
)

Compress-Archive `
    -LiteralPath @(
        (Join-Path $RuntimeRoot 'data'),
        (Join-Path $RuntimeRoot 'generated'),
        (Join-Path $RuntimeRoot 'state')
    ) `
    -DestinationPath $Archive
```

An archive containing `runtime-info.txt` contains a disposable local password;
handle it as a credential-bearing local artifact. Do not commit or upload it to
an untrusted location.

On a new machine:

1. Recreate uv, Python, and `.venv` from sections 3–4.
2. Restore only the archived runtime data/generated files.
3. Rebuild the SPA from section 5.
4. Re-run the effective-path guard.
5. Run migrations, start Django, and repeat all health checks.

## 12. Manual removal

The complete disposable location is:

```text
C:\Users\Administrator\AppData\Local\hyeisn-pinry\visual-debug
```

For another Windows account, open this portable form in Explorer:

```text
%LOCALAPPDATA%\hyeisn-pinry\visual-debug
```

Stop Django first. Then validate the exact resolved path before recursively
removing it:

```powershell
$ExpectedRoot = [IO.Path]::GetFullPath(
    (Join-Path $env:LOCALAPPDATA 'hyeisn-pinry\visual-debug')
).TrimEnd('\')

$ResolvedRoot = (
    Resolve-Path -LiteralPath $ExpectedRoot -ErrorAction Stop
).Path.TrimEnd('\')

$ExpectedParent = [IO.Path]::GetFullPath(
    (Join-Path $env:LOCALAPPDATA 'hyeisn-pinry')
).TrimEnd('\')
$RuntimePrefix = $ResolvedRoot + '\'
$ReparsePoint = [IO.FileAttributes]::ReparsePoint
$RootItem = Get-Item -LiteralPath $ResolvedRoot -Force -ErrorAction Stop
$ParentItem = Get-Item -LiteralPath $ExpectedParent -Force -ErrorAction Stop

if (
    $ResolvedRoot -ine $ExpectedRoot -or
    (Split-Path -Parent $ResolvedRoot) -ine $ExpectedParent -or
    (Split-Path -Leaf $ResolvedRoot) -ine 'visual-debug' -or
    ($RootItem.Attributes -band $ReparsePoint) -or
    ($ParentItem.Attributes -band $ReparsePoint)
) {
    throw "Unexpected cleanup target; refusing to delete: $ResolvedRoot"
}

$UnsafeReparsePoint = Get-ChildItem `
    -LiteralPath $ResolvedRoot `
    -Force `
    -Recurse `
    -ErrorAction Stop |
    Where-Object { $_.Attributes -band $ReparsePoint } |
    ForEach-Object {
        $Link = $_
        $Targets = @($Link.Target)
        $Unsafe = $Targets.Count -eq 0

        foreach ($Target in $Targets) {
            if ([string]::IsNullOrWhiteSpace([string]$Target)) {
                $Unsafe = $true
                break
            }
            $TargetPath = if ([IO.Path]::IsPathRooted([string]$Target)) {
                [IO.Path]::GetFullPath([string]$Target)
            }
            else {
                [IO.Path]::GetFullPath(
                    (Join-Path $Link.DirectoryName ([string]$Target))
                )
            }
            if (
                $TargetPath -ine $ResolvedRoot -and
                -not $TargetPath.StartsWith(
                    $RuntimePrefix,
                    [StringComparison]::OrdinalIgnoreCase
                )
            ) {
                $Unsafe = $true
                break
            }
        }

        if ($Unsafe) {
            $Link
        }
    } |
    Select-Object -First 1

if ($UnsafeReparsePoint) {
    throw "Runtime reparse point escapes the root; refusing deletion: $($UnsafeReparsePoint.FullName)"
}

$RunningRuntimeProcess = Get-CimInstance Win32_Process |
    Where-Object {
        $_.ExecutablePath -and
        [IO.Path]::GetFullPath($_.ExecutablePath).StartsWith(
            $RuntimePrefix,
            [StringComparison]::OrdinalIgnoreCase
        )
    } |
    Select-Object -First 1

if ($RunningRuntimeProcess) {
    throw "A runtime process is still running: PID $($RunningRuntimeProcess.ProcessId)"
}

$PidFile = Join-Path $ResolvedRoot 'state\runtime.pid'
if (Test-Path -LiteralPath $PidFile) {
    throw 'runtime.pid still exists; complete the safe stop procedure first.'
}

Remove-Item -LiteralPath $ResolvedRoot -Recurse -Force
```

Deleting that one directory removes the temporary Python, packages, caches,
SQLite database, media, seed helpers, credentials, logs, PID file, and Chrome
capture artifacts. It does not alter the repository or system Python.

## 13. Troubleshooting and prohibited shortcuts

- PageNotFound or 404 at `8080/static/spa/`: use the integrated port-8000 URL.
- Template missing at port 8000: rebuild the SPA; do not hand-edit generated
  `pinry/templates/index.html`.
- `No module named django_extensions`: install the explicitly pinned extension
  into the isolated venv.
- Effective DB is `/data/db.sqlite3` or media is `/data/media`: stop. Restore
  the environment variables and inspect `pinry/settings/local_settings.py`.
- Images are absent or API returns 500: confirm the seed generated original,
  `thumbnail`, `medium`, `standard`, and `square` records under the isolated
  media root.
- Port 8000 is occupied: inspect the owning process. Do not kill an unknown
  process and do not casually move Django to another port; the Vue proxy is
  fixed to 8000.
- Do not substitute real accounts, production exports, production media,
  external image URLs, `make serve`, the old Compose example, or the system
  Python for this workflow.
- Do not stage generated SPA output. The only repository file introduced by
  this quickstart workflow should be intentional documentation or explicitly
  requested reusable tooling.
