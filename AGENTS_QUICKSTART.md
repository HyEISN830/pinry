# hyeisn-Pinry Agent Quickstart

This is the primary architecture, change-routing, UI-token, handoff, and local
visual-debug guide for this repository. It is written for Codex/agent sessions
and team members who need to make a focused change without loading the whole
repository or replaying earlier release conversations.

Architecture map last refreshed at **R82 / v3.3.6.1r**. Use `git log -1` for the
exact current commit. The runtime sections remain valid unless a later commit
changes the referenced entry points.

The order is intentional: use sections A-F to choose the smallest relevant
surface first. Read sections 1-13 only when Chrome or the isolated runtime is
actually needed. Do not dump this complete file into context during every task.

## A. Context-safe first minute

### A.1 Establish the exact baseline

Run these read-only commands before editing:

```powershell
git status --short --branch
git log -5 --oneline --decorate
rg -n '^## ' AGENTS_QUICKSTART.md
```

- Preserve unrelated or pre-existing worktree changes. They belong to the
  user unless the current task proves otherwise.
- Read only the task row in section C, the applicable token rules in section
  D, and the validation row in section F.
- Locate symbols with `rg -n` before opening a file. For long files, read a
  bounded range with `Get-Content ... | Select-Object -Skip ... -First ...`.
- Do not begin by printing the whole renderer, every Vue component, every
  migration, `rg --files` for the entire repository, or this entire document.
- Before resuming interrupted work, inspect `git diff` and the handoff capsule
  below. Continue from the current state; do not restart completed work.

### A.2 Keep a compact task capsule

Use this state shape in plans, progress notes, or handoffs. It is deliberately
small enough to survive context compaction:

```text
Release / version:
Objective and acceptance criteria:
Current status (done / in progress / not started):
Files intentionally changed:
Decisions and invariants that must survive:
Validation already run and exact result:
Runtime / Chrome state and artifact paths:
Git state (branch, commit, push):
Next concrete action:
```

Never store passwords, tokens, cookies, private media paths, or hidden
chain-of-thought in a capsule. Record final engineering reasons, observable
evidence, tradeoffs, and unresolved risks instead.

### A.3 Route the task before reading deeply

| Task | Read first | Usually skip |
| --- | --- | --- |
| Header, cards, page layout, theme, language | C.2, D, F.1 | Backend internals and runtime setup |
| Pin/Comic/Board API or schema | B.3, C.1, F.1 | Canvas renderer and unrelated views |
| Likes or viewed counts | C.1 `Likes / views`, E | Thumbnail and opening-animation code |
| Thumbnail, original image, upload, avatar | C.1 `Images / media`, C.3, E | Unrelated page styling |
| Search result layout or pagination | C.1/C.2 `Search` | Opening animation and profile editor |
| Opening animation or motion | C.2 `Opening`, D.4, E | Django models unless preference API changes |
| Chrome visual QA | Sections 1, 5, 8, 9 | First-time setup when runtime already exists |
| Fresh or migrated debug environment | Sections 2-8 | Product UI internals until health checks pass |
| Documentation-only change | A, B-F, `git diff --check` | Starting Django or Chrome without a visual need |

Parallel work is useful when agents own different files. Do not assign two
agents to edit the same Vue component, migration, settings block, or this
quickstart simultaneously. The primary agent must integrate and review the
shared diff before validation.

## B. Repository architecture

### B.1 Runtime stack

- **Backend:** Django 2.2 + Django REST Framework. The verified local runtime
  uses CPython 3.9; do not use the machine's Python 3.12/3.14.
- **Frontend:** Vue 2.6 + Vue Router history mode + Buefy/Bulma, built with Vue
  CLI 4, Node 18, and pnpm 9. There is no Vuex store; state is component-local,
  event-bus based, API derived, or persisted in local storage.
- **Data:** Django models use the configured database. The isolated workflow
  uses SQLite; media files live in configured Django storage outside the repo.
- **Rendering:** normal UI is DOM/CSS; the opening animation is one Canvas 2D
  surface controlled by a small Vue lifecycle wrapper.
- **Delivery:** Django serves the built SPA shell and `/api/v2/`. The history
  fallback in `pinry/urls.py` returns `index.html` for non-API routes.

```text
Browser
  -> Vue Router view -> Vue component -> components/api.js
                                      -> /api/v2/
                                         -> DRF ViewSet / action
                                            -> Serializer
                                               -> Model / configured DB

Image element -> /media/<path> -> serve_guarded_media
                                -> original redirect + permission endpoint
                                -> or size-aware thumbnail stream

Theme selection -> theme.js -> gradientThemePresets.js -> CSS variables
Opening toggle  -> openingPreference.js -> GalleryPageOpening.vue
                                         -> galleryOpeningRenderer.js (Canvas)
```

### B.2 Top-level ownership

| Path | Responsibility |
| --- | --- |
| `core/` | Pin, Board, Comic, image proxy, uploads, likes/views, API serializers/viewsets, permissions, media delivery, migrations, tests |
| `django_images/` | Low-level original/thumbnail records, resize/crop/encode utilities, derivative file lifecycle |
| `users/` | User/profile API, avatar source and 30/48/96px derivatives, login/logout/token behavior |
| `pinry/` | Django settings, root URLs, WSGI, upload handler, generated SPA template/static delivery |
| `pinry_plugins/` | Plugin loading/hooks; thumbnail pre-creation hooks live here |
| `pinry-spa/src/` | Vue application, routes, views, components, API client, theme/motion/i18n/token systems |
| `pinry-spa/public/` | Source PWA icons and public shell assets |
| `docs/` | Project documentation assets; not the active SPA implementation |
| `AGENTS_QUICKSTART.md` | Architecture map, handoff contract, and isolated Chrome/runtime workflow |

Generated SPA output under `pinry/static/spa/` and
`pinry/templates/index.html` is build output and is git-ignored. Build it for
local QA, but do not stage it.

### B.3 Backend request flow

1. `pinry/urls.py` mounts DRF at `/api/v2/`, profile routes, guarded media,
   admin, and the SPA history fallback.
2. `core/views.py` registers the Pin/Image/Upload/Board/Comic/Search ViewSets,
   applies permissions/throttles, annotates likes/views, and defines custom
   actions such as `like`, `viewed`, and `original`.
3. `core/serializers.py` is the public JSON contract and the main create/update
   orchestration layer. Privacy filters here must agree with ViewSet queries.
4. `core/models.py` owns persisted entities, image-fetch jobs, chunk sessions,
   motion-photo records, uniqueness constraints, and cleanup signals.
5. `core/likes.py` defines canonical authenticated/anonymous actor identities.
   Likes and viewed counts intentionally share this de-duplication model.
6. `core/media_views.py` canonicalizes `/media/` paths, prevents original-image
   permission bypasses, identifies derivative size from the database, and
   applies per-size pacing.
7. `django_images/models.py` and `django_images/utils.py` generate and store the
   actual image derivatives.

### B.4 Frontend request and composition flow

1. `pinry-spa/src/main.js` installs Vue/Buefy/i18n, global directives, API
   feedback, saved preferences, and shared SCSS systems.
2. `pinry-spa/src/App.vue` owns the persistent shell: `PHeader`, route
   transition, back-to-top progress, and page-opening overlay. Only its
   `<PHeader app-shell>` renders; legacy per-view header instances are inert
   compatibility shells, so navigation changes belong in `PHeader.vue` once.
3. `pinry-spa/src/router/index.js` is the route-to-view map.
4. Views compose reusable components; `components/api.js` is the frontend API
   boundary. Do not scatter new endpoint strings through components.
5. Shared visual behavior lives in `components/utils/*.scss` and helpers in
   `components/utils/*.js`; page-specific layout remains in its Vue file.
   Masonry owns the outer tile transform, so hover/entrance transforms belong
   on an inner card/frame and layout-ready/resize observers must be cleaned up.

## C. Modification entry points

### C.1 Backend change router

| Change | Primary entry points | Required companions / invariants |
| --- | --- | --- |
| Pin/Board/Comic field or relation | `core/models.py`, new `core/migrations/`, `core/serializers.py` | Query/privacy in `core/views.py`; frontend contract; targeted API tests |
| API list/detail/action | `core/views.py`, `core/serializers.py` | Register only through existing `drf_router`; preserve owner/private filters and pagination shape |
| Likes / views | `core/likes.py`, `core/models.py`, `core/views.py`, `core/throttles.py` | Actor-key compatibility, uniqueness, race idempotence, serializer annotations; `core/tests/likes.py`, `core/tests/viewed.py` |
| Aggregate search | `AggregateSearchViewSet` in `core/views.py` | `Search.vue`, result components, per-bucket offsets/limits; Pins alone use masonry |
| Static image size or GIF tier | `pinry/settings/base.py`, `core/models.py`, `core/serializers.py`, `django_images/` | Historical-data strategy, `imageVariant.js`, media rate mapping, README/example settings, image tests |
| Original/thumbnail delivery | `core/media_views.py`, `ImageViewSet.original`, `pinry/urls.py` | Never weaken private-original checks or canonical-path handling; cache invalidation on Image/Thumbnail save/delete |
| Direct/chunked image or avatar upload | `core/chunked_uploads.py`, `core/upload_views.py`, `core/models.py` | `chunkedUpload.js`, `FileUpload.vue`/`AvatarCropper.vue`; preserve offset, actor-rate, timeout, cleanup semantics |
| Remote image fetch / motion photo | `ImageManager` and `ImageFetchJob` in `core/models.py`, management command, `core/motion_photo.py` | Serializer status fields, async setting, cleanup and image-fetch tests |
| User/profile/avatar | `users/models.py`, `users/serializers.py`, `users/views.py` | `avatarVariant.js`, profile components, 30/48/96px size contract |
| Settings or deployment behavior | `pinry/settings/base.py`, `development.py`, `docker.py`, `local_settings.example.py` | Environment override compatibility; run effective-setting checks before data writes |
| Plugin hook | `pinry_plugins/runner.py`, loader, plugin class | Keep plugin failure isolated and cover with `pinry_plugins/tests.py` |

### C.2 Frontend change router

| Surface | Primary entry points | Shared dependencies to inspect |
| --- | --- | --- |
| App shell, header, create/my menus, theme/language/logout | `App.vue`, `PHeader.vue` | `theme.js`, `gradientThemePresets.js`, motion/opening preferences, all locale JSON files |
| Pin masonry/card | `Pins.vue`, `pinDisplayItem.js` | `PinHandler.js`, `imageVariant.js`, `avatarVariant.js`, `grid-layout.scss`, `content-card-actions.scss` |
| Pin detail overlay | `PinPreview.vue` | original-image cache/API, `viewed.js`, source/share helpers, content-card tokens |
| Comic list/card | `views/Comics.vue`, `ComicCard.vue`, `PersonalComics.vue` | `SearchComicMasonry.vue`, image/avatar variants, shared action styles |
| Comic detail/reader | `views/ComicReader.vue` | Comic API, `viewed.js`, original-image handling, compact detail metadata tokens |
| Comic creation | `comic/ComicCreateModal.vue` and upload progress components | chunked upload/API, shared create-modal system |
| Board/profile/avatar | `Boards.vue`, Board editors, profile views/components, `AvatarCropper.vue` | `avatarVariant.js`, `user-shell.scss`, collection shell/count styles |
| Search | `views/Search.vue` | `SearchPinMasonry.vue`, `SearchPinCard.vue`, `SearchComicMasonry.vue`, `SearchBoardCard.vue`, cached search state; `search/SearchPanel.vue` is legacy and currently unreferenced |
| Opening animation | `transitions/GalleryPageOpening.vue`, `galleryOpeningRenderer.js` | `openingPreference.js`, `motionPreference.js`, theme variables; no DOM curtain layers |
| Routes / 404 | `router/index.js`, target view, `PageNotFound.vue` | Django history fallback must continue excluding API/admin/static/media |
| API call or upload client | `components/api.js`, `chunkedUpload.js` | CSRF/feedback setup in `main.js`; keep endpoint knowledge centralized |
| Text / language | all three `components/utils/i18n/locales/*.json`, `components/utils/i18n/index.js` | Check desktop and 390px layouts; preserve locale normalization |
| Shared modal/loading/action UI | corresponding `*-system.scss` plus adopting component | Global imports in `main.js`; do not duplicate system CSS locally |

### C.3 High-risk dependency recipes

**Adding an API field**

```text
model + migration (if persisted)
  -> serializer field / annotation
  -> ViewSet query or action
  -> components/api.js
  -> every card/detail/search consumer
  -> en/zh/fr text when visible
  -> backend tests + lint/build + visual QA
```

**Adding or changing an image derivative**

```text
IMAGE_SIZES / animated options
  -> Image property and ImageSerializer
  -> upload and URL-fetch generation
  -> historical-image backfill policy
  -> imageVariant.js selection and fallback
  -> media size lookup / rate policy
  -> seed rules, README/example settings, image tests
```

Do not put expensive file generation or database writes into a list/read path
without an explicit migration/backfill plan. See the current `medium` caveat
in E.2.

**Changing a card metadata control**

```text
shared semantic class in content-card-actions.scss
  -> density variable in design-tokens.scss
  -> Pin card + Comic card + search card
  -> PinPreview + ComicReader when detail behavior is intended
  -> coarse-pointer and 390px checks
```

### C.4 Domain naming and write invariants

- `core.models.Image` is a proxy; the real Image/Thumbnail tables and their
  schema migrations live in `django_images/`.
- Pin creation and ComicPage creation accept exactly one of a remote `url` or
  existing `image_by_id`. Pin updates do not swap the image implicitly.
- `(comic, order)` is unique. Page reorder uses a temporary high range before
  normalization; a naive single-pass rewrite can violate the constraint.
- List queries for private objects must use `filter_private_pin/board/comic`;
  object permissions alone do not prevent list/search leakage.
- `Board.pins` is the board-to-pin relation, while the reverse name on a Pin is
  also `pins`; confirm model direction before changing filters or cover logic.
- Pin/ComicPage deletion removes the underlying image only after no other Pin
  or ComicPage references it.

## D. UI token contract

### D.1 Sources of truth

| Layer | File | Purpose |
| --- | --- | --- |
| Theme source values | `App.vue` root/dark variables | Safe initial light/dark values before saved theme application |
| Theme catalog | `utils/gradientThemePresets.js` | Solid/gradient palettes, contrast correction, light/dark CSS-variable payloads |
| Theme application | `utils/theme.js` | Persists selection and writes preset variables/data attributes to `<html>` |
| Semantic/design tokens | `utils/design-tokens.scss` | `--color-*`, fonts, spacing, radii, shadows, breakpoints, motion, z-index, card density |
| SCSS helpers | `utils/_ui-tokens.scss` | Breakpoint/spacing/radius maps and non-emitting mixins/functions |
| Motion helpers | `utils/_motion-mixins.scss`, `motion-system.scss` | Focus, hover, entrance, tilt, and reduced-motion behavior |
| Shared systems | `utils/*-system.scss`, `grid-layout.scss`, `content-card-actions.scss` | Reusable modal, loading, grid, metadata, user, collection, and search behavior |

Components should consume semantic variables such as
`--color-surface-card`, `--color-text-strong`, `--color-accent-foreground`,
`--space-sm`, `--radius-md`, `--shadow-card`, and motion tokens. Theme source
variables such as `--accent` and `--surface-1` are compatibility inputs, not
the preferred component API.

### D.2 Token categories

| Need | Use |
| --- | --- |
| Surface/text/border | `--color-surface-*`, `--color-text-*`, `--color-line-soft`, `--color-border-*` |
| Accent/gradient/glow | `--color-accent-*`, `--color-theme-glow*` |
| Typography | `--font-sans`, `--font-display`, `--font-mono`; set an explicit shared size/line-height for mixed `<a>`/`<button>` groups |
| Spacing | `--space-2xs` through `--space-3xl` |
| Corners | `--radius-xs` through `--radius-xl`, `--radius-pill`, `--radius-card` |
| Elevation/focus | `--shadow-xs/sm/card/hover/floating`, `--focus-ring` |
| Motion | `--motion-duration-*`, `--motion-ease-*`, hover/tilt tokens |
| Layout/layers | `--container-*`, breakpoint helpers, `--z-*` |
| Card metadata density | `--content-card-tag/stat/source-height` and coarse-pointer variants |
| Comic book depth | `--comic-stack-depth/sheet-height/near-*/rear-*`; mobile/coarse overrides stay in `design-tokens.scss` |

### D.3 Rules for tokenized UI changes

1. Do not hardcode a new brand color in a component. Add/derive it in the
   theme preset or semantic token layer, then consume the alias.
2. Use raw pixel values only for truly local geometry such as an icon glyph,
   canvas primitive, or one-off optical alignment. Reusable spacing, radius,
   elevation, duration, and layers require tokens.
3. Do not copy shared card action, loading, modal, search pill, user shell, or
   collection shell CSS into another component. Extend the shared system or
   add a scoped modifier.
4. Respect `html[data-theme]`, `html[data-accent-kind]`, and
   `html[data-motion='reduce']`. Reduced motion must not leave hidden timers,
   transforms, Canvas loops, or interaction blockers running.
5. Interactive controls need visible `:focus-visible`, disabled/busy state,
   adequate contrast, and a stable accessible name. Decorative icons/marks
   are `aria-hidden`.
6. Use the shared responsive media profile in `responsiveMedia.js` when JS
   behavior must follow mobile/coarse-pointer policy; use token breakpoints or
   the established media query for CSS layout.
7. Breakpoints have different meanings: media quality is 860px/coarse pointer,
   navigation switches at 980px, and global nav height changes at 760px. Do
   not merge them merely to make the numbers uniform.
8. Never introduce an arbitrary z-index above `--z-page-opening`. Use the
   shared layer scale and verify modal/header/opening interactions.
9. Every visible label must exist in en/zh/fr. Test the longest locale, not
   only the current language.
10. Locale files and this document are UTF-8. On Windows, use
    `Get-Content -Encoding utf8` when the console otherwise renders CJK or box
    drawing characters as mojibake; do not "repair" correctly encoded text.

### D.4 Theme and motion extension checklist

When adding a theme, change `gradientThemePresets.js`, supply accessible light
and dark foregrounds, and let `theme.js` populate the existing variables.
Verify normal/hover/focus/disabled controls, light/dark mode, solid/gradient
accent kinds, and the opening renderer's theme sampling.

When adding animation, use `requestAnimationFrame` for Canvas, cancel it during
destroy/replay, cap pixel ratio/work budgets, tolerate resize and long frame
deltas, and provide a reduced-motion/no-opening path. CSS motion uses the
shared duration/easing tokens rather than new literal timing curves.

## E. Decision record and known risks (R68 onward)

This section records final, verifiable engineering reasons and regression
lessons. It is not a transcript of private reasoning.

**Standing maintenance rule:** every future iteration must update this section
in the same change. Add a compact release entry explaining the chosen outcome,
why that approach was selected, the invariants future work must preserve, the
validation evidence, and any unresolved risk. If a decision supersedes an old
one, keep the history but mark the replacement release clearly. Record durable
engineering conclusions rather than chat transcripts, credentials, private
data, or step-by-step hidden chain-of-thought.

| Release(s) | Final decision and reason that must survive |
| --- | --- |
| R68-R71 | The original curtain/comet concept established the visual direction, but layered CSS curtain/compositor effects flickered across desktop and mobile browsers. R71.1 isolated the comet and proved the curtain was the unstable surface. |
| R69-R70 | The comet moved from fixed DOM particles to Canvas for responsive trails, bloom, dust, star glints, aerodynamic lines, theme gradients, bounded pixel ratio, resize continuity, and replay safety. Keep those effects in the renderer, not dozens of DOM nodes. |
| R72-R74 | The stable architecture is a **single Canvas deep-space veil + comet**. Static nebula/star work is cached, large canvases use adaptive frame/pixel budgets, reduced motion disables it, and the independent opening toggle defaults off. Do not reintroduce animated DOM/CSS curtains or multiple full-screen filtered surfaces. |
| R75 | Pin and Comic `viewed` records mirror the like actor-key/de-dup model. Counts are annotated in list APIs; detail/open surfaces record once and update UI. Search Pins use their own masonry component; other search buckets keep their established layout. |
| R76 | The formal-deployment UI pass consolidated semantic colors, actions, responsive details, 404/search/reader polish, sharing, contrast, and PWA icons. New UI should extend the token/system layer instead of creating another visual dialect. |
| R77 | Mobile cards use sharper images and smaller batches to offset bandwidth/memory. Long/tall desktop thumbnails also needed more detail; selection belongs in the central variant helper, not per-card heuristics. |
| R78-R79 | Card metadata height is controlled through shared density tokens; Comic stacked-sheet decoration must remain outside clipping; mobile avatars choose larger derivatives. Original media stays permission guarded, while derivatives are paced. |
| R80 | Static derivatives are 240px `thumbnail`, 480px `medium`, 600px `standard`, and 125px square. Desktop cards prefer `medium`; mobile/coarse cards prefer `standard`; animated GIF cards prefer `animated_thumbnail_fast`. Language choices use EN/FR/ZH code badges. |
| R81 | Create/My menu items explicitly share a 14px typography baseline. Create is a distinct action surface (desktop creative rows, mobile three-tile grid); My remains a resource-navigation list. Preserve this semantic distinction. |
| R82 | A Comic card is one physical book object. The Grid/Masonry root is measurement-only; an inner frame owns entrance motion, an inner book owns the two attached sheets and tilt, and the clipped card owns content. Embedded rows opt into an equal-height shelf while standalone/personal/search Masonry remains natural-height. |
| R82 patch | `v3.3.6.1r` restored true 3D hover on desktop and hybrid-input devices. Trust the live mouse `PointerEvent`, not primary `hover/pointer` capability queries; keep perspective on the book itself and let its entrance frame return to an untransformed state. |

### E.1 Current thumbnail and delivery contract

| Variant | Geometry | Normal card use | Default pace |
| --- | --- | --- | --- |
| `thumbnail` | 240px wide | legacy/fallback | 64 KiB/s |
| `medium` | 480px wide | desktop static cards | 128 KiB/s |
| `standard` | 600px wide | mobile/coarse static cards | 256 KiB/s |
| `square` | 125x125 crop | square/legacy consumers | unchanged legacy fallback, normally 64 KiB/s |
| `animated_thumbnail_fast` | 180px wide, max 48 frames | animated GIF card priority | 256 KiB/s |
| original | source geometry | authorized detail/reader only | 1 MiB/s preview stream |

New uploads and URL-fetched images generate every configured static derivative
at creation; GIFs additionally generate the animated derivative. Avatar
30/48/96px sizes are a separate user-profile contract and are not image-card
tiers.

Original files must route through `/api/v2/images/<id>/original/` permission
checks and the preview stream. Never make a raw `/media/` alias a private-image
bypass. Thumbnail size cannot be inferred from the content-addressed URL; use
the `Thumbnail.image -> size` database mapping and clear its cache on changes.
Generated thumbnails are currently served without per-object authorization;
private-content safety therefore also depends on APIs not leaking private
thumbnail URLs. Do not describe every `/media/` response as permission guarded.

### E.2 SQLite historical-medium caveat

Images created before R80 have no `medium` row. The current `Image.medium`
property lazily generates it under a transaction. On SQLite, concurrent first
reads after deployment can contend for the database-wide writer lock and emit
`database is locked`.

Preferred follow-up architecture:

1. provide a bounded management command to backfill missing `medium` files
   sequentially during maintenance;
2. run it with one writer/application worker against verified media/DB paths;
3. make normal list/read serialization side-effect free after backfill;
4. retain upload-time generation for all new work.

Until that change lands, treat a burst of post-deploy lock errors as a known
historical backfill risk, not as evidence that new uploads omit derivatives.

### E.3 Likes and viewed identity contract

- Authenticated records use `user:<id>`; anonymous records use a salted
  `anon:v1:<hash>`. Reads/de-duplication retain compatibility with legacy
  `ip:<hash>` keys so old records do not count twice.
- A Like is a toggle; a View is idempotent. Database uniqueness and the
  post-conflict recheck make concurrent requests report the winning state.
- Only trust `X-Forwarded-For` when the direct peer is configured in
  `TRUSTED_PROXY_IPS`.
- Pin/Comic list, detail, and search responses must retain all four fields:
  `likes_count`, `viewer_liked`, `viewed_count`, and `viewer_viewed`.

### E.4 Upload and remote-fetch state contract

- Chunk upload state is `uploading -> processing -> complete|failed`; offsets
  are server-authoritative, completion is idempotent, and final image handling
  must pass through `ImageSerializer` so all derivatives exist.
- Avatar completion passes through `UserProfile.set_avatar()` to create the
  independent 30/48/96px sizes.
- Remote fetch is synchronous by default. If
  `IMAGE_FETCH_ASYNC_ENABLED=true`, Web requests can temporarily expose fetch
  status without an image and a separate
  `process_image_fetch_jobs` management worker is mandatory. Current startup
  scripts do not launch it automatically; prefer one worker until claim logic
  is made multi-worker safe.

### E.5 Comic book-card layout contract (R82)

- `ComicCard.vue` is the shared visual source of truth. Its root
  `.comic-card-shell` may also be a Masonry tile, so it must remain untransformed
  and must not own sheets positioned against a stretched Grid row.
- The required hierarchy is shell -> `.comic-card-frame.motion-card-enter` ->
  `.comic-book.motion-tilt-card` -> `.comic-card`. The frame alone owns entry
  motion, the book moves the card and sheets as one object, and only the card
  clips cover/content to its rounded border.
- The two sheets are real, decorative `aria-hidden` spans. Do not move them
  into the clipped card or replace them with `.motion-tilt-card::after`;
  reduced-motion rules intentionally hide that global glare pseudo-element.
- Only the embedded `Comics.vue` row passes `shelf-layout`. Its flex chain
  fills the Grid row and keeps the source/stat footer at the bottom. `/comics`,
  personal Comics, and search Comics retain content-driven height, with the
  stack depth included in Masonry measurement and gutter calculations.
- Geometry comes from the `--comic-stack-*` design tokens: desktop uses 12px
  total depth and 10px sheets; mobile/coarse uses 10px and 8px. Surfaces mix
  semantic card/accent colors, use two layers only, and keep just one restrained
  rear shadow.
- Tilt accepts fine mouse pointers only, measures the untransformed frame, and
  enables `will-change` only while tilting. Touch/coarse pointers skip the rAF
  work. Reduced motion disables transform/glare but preserves the static pages.

R82 validation evidence: at 2048x1111 the Home fixtures with 2/2/1/2 tags had
identical 675.6px card bodies and a 3px page overlap. `/comics` retained natural
675.6/671.1/644.5px heights; the next tile followed the shortest column with
the exact 16px gutter. At 390x844, stack depth reduced to 10px, overlap stayed
2px, and document width did not overflow. Light/dark, solid/gradient, full and
reduced motion all passed in the dedicated Chrome window. The only console
messages were external Chrome-extension message-channel errors; no Vue/app
errors appeared. Screenshots remain runtime artifacts outside the repository.

The `v3.3.6.1r` hover repair established two additional invariants:

- Do not veto a confirmed `pointerType === 'mouse'` with `(hover:hover)` or
  `(pointer:fine)`. Those media features describe the primary input and report
  coarse/no-hover on many touch laptops even while an attached mouse is active.
  Touch and pen events remain excluded, and `data-motion='reduce'` remains the
  hard accessibility veto. Scale follows `.is-tilting`, not sticky `:hover`.
- The final `.comic-book` transform must contain
  `perspective(var(--tilt-perspective))`. The intervening entrance frame uses
  `animation-fill-mode: backwards` so its completed animation leaves real
  `transform:none` and `filter:none`; retaining an identity matrix/filter with
  `both` creates a 3D-flattening boundary that makes rotation look flat.

Chrome validation forced the primary media state to `hover:none` and
`pointer:coarse`, then supplied a real mouse pointer event. The card still
reached `rotateX:2.52deg`, `rotateY:3.36deg`, `glare:0.2`, and a perspective
matrix; ordinary desktop input and reset-to-identity also passed. The emulated
input state was cleared before handoff.

Known global follow-up: the site preference drives `html[data-motion]`, but it
does not yet automatically inherit OS `prefers-reduced-motion`. Also avoid
reviving old page-scoped Comic visual rules in `Comics.vue`; shared card changes
belong in `ComicCard.vue` and the semantic token layer.

## F. Validation, release, and handoff contract

### F.1 Minimum validation matrix

| Change surface | Minimum checks |
| --- | --- |
| Vue markup/style/helper | Vue lint, production build, relevant desktop view, 390x844 mobile view, console, light/dark when theme-sensitive |
| Header/theme/language | anonymous and owner state, longest locale, keyboard focus, reduced motion, viewport reset and explicit logout |
| Django model/API | `manage.py check`, `makemigrations --check --dry-run`, targeted tests, serializer response inspection |
| Likes/views | `core.tests.likes`, `core.tests.viewed`, anonymous/authenticated de-dup and concurrent/idempotent behavior |
| Image/media/tier | `core.tests.original_images`, `core.tests.views`, `django_images.tests`, real API derivative URL and private-original denial |
| Chunk upload/avatar | `core.tests.chunked_uploads`, relevant `users.tests`, interrupted/resumed upload and actual dimensions |
| Search | targeted backend response plus Pin/Board/Comic/Tag UI; load-more offsets and Pin masonry |
| Opening/motion | lint/build, full/reduced/off states, desktop/mobile/portrait, resize, replay, frame smoothness |
| Documentation only | path/symbol spot checks, heading scan, `git diff --check` |

The isolated runtime installs runtime requirements, not every development test
dependency. `django_images.tests` imports tracked dev dependency
`qrcode==7.3.1`; install the tracked dev set or that exact package in the
isolated venv before calling this an application failure. As of R81, the
isolated full suite also has a pre-existing
`users.tests.AvatarUploadTest.test_upload_avatar_creates_multiple_sizes`
failure where the immediate response contains an empty small avatar. Reproduce
and report it separately; do not claim an unrelated release introduced or
fixed it without evidence.

### F.2 Version and git convention

- Recent owner releases are identified by commit subjects such as
  `v3.3.5r R81`. They are not synchronized with `pyproject.toml`, the SPA
  package version, or a Git tag. Do not change/tag those unless requested.
- Unless the current user request explicitly says otherwise, completed release
  work includes commit and push on the current branch after validation.
- Stage only intentional source/docs files. Never stage generated SPA output,
  runtime data, credentials, screenshots, logs, PID files, or user changes.
- Finish with a clean `git status --short --branch`, confirm the upstream ref,
  and put commit/push state in the handoff capsule.
- If validation is blocked by a known baseline issue, report the exact passing
  targeted suites and the exact blocker. Never summarize a failed full suite
  as fully passing.

## G. Remote deployment storage maintenance contract

### G.1 Storage ownership and cleanup boundary

- The deployment source convention is `/opt/src/pinry`; the Compose project is
  `/opt/stacks/pinry`.
- Treat `/opt/stacks/pinry/data/**` as persistent production data. The Compose
  bind mount exposes it as `/data`, including SQLite databases and their
  `-wal`/`-shm`/journal files, original media, thumbnails, avatars, Motion
  Photos, and upload chunks. Never classify this tree as build residue.
- Preserve Compose files, overrides, `.env*`, certificates, secrets, backups,
  `pinry/settings/local_settings.py`, tracked source, and Git history.
- Repeated image builds normally grow Docker's BuildKit cache and leave the
  replaced image dangling. A small source tree is not evidence that the Docker
  data root is also small.

### G.2 Read-only audit before deletion

Use the saved Termark asset for remote commands; do not request credentials or
bypass it with direct `ssh`, `scp`, or `sftp`. Before cleanup:

1. Run `docker compose config` and `docker compose ps -a` from
   `/opt/stacks/pinry`; verify the data bind mount and whether Pinry is down.
2. Record the exact ID of `local/pinry-custom:latest`. When its Compose stack
   is down, Docker may label this current deploy image "reclaimable" merely
   because no container references it. That label alone does not authorize
   deletion.
3. Compare `df -h /`, `docker system df -v`, `docker builder du`, and
   `docker image ls --filter dangling=true`.
4. Inspect the source and persistent-data sizes separately. Do not read or
   print `.env` contents during a storage audit.

### G.3 Safe first-line cleanup

After the audit proves the current image is tagged and persistent data is a
bind mount, the conservative cleanup pair is:

```sh
docker builder prune -f
docker image prune -f
```

The first command removes unused build cache; the second removes dangling
images only. Recheck the recorded Pinry image ID immediately afterward. It must
still exist and match exactly. Leave the application in its prior running or
stopped state unless the user explicitly asks to start it.

Do not use `docker system prune -a`, `docker image prune -a`,
`docker volume prune`, blanket container/network pruning, manual deletion under
Docker/containerd storage, or `git clean -fdX`. Do not delete
`/opt/stacks/pinry/data/static`: generated static files and persistent media
share that tree. Source-side caches may be removed only by exact verified path,
never as a substitute for measuring Docker storage first.

### G.4 Post-clean verification and maintenance baseline

Repeat the disk/Docker audit, confirm that the current image ID and persistent
data remain present, confirm no unexpected service changed state, and report
both reclaimed and deliberately retained space. Build cache reported as active
or `0B reclaimable` is not residue that should be forced away.

The 2026-07-20 maintenance pass established the current baseline: unused
BuildKit records released about 2.64GB and dangling images released about
940.1MB, approximately 3.58GB total. Root usage changed from 19GB to 16GB and
free space from 57GB to 60GB (25% to 21%). The current Pinry image, source,
Compose configuration, and 398MB persistent-data tree were preserved, and
Pinry remained down. Docker subsequently showed 3.212GB of active,
non-reclaimable build cache; it also called the stopped stack's 1.517GB current
Pinry image reclaimable, so that image was intentionally retained.

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
