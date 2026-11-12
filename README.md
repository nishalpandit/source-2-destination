# Source 2 Destination — School & Hostel Student Calling Management System

Enterprise-grade, multi-page HTML5 frontend for **Source 2 Destination**, a centralized governance platform enabling residential schools, hostels, and regional franchises to manage policy-restricted student-to-parent/guardian voice calling.

---

## 1. Technology Stack & Architectural Compliance

- **HTML5**: 83 dedicated, standalone `.html` files across Authentication, Super Admin, Franchise, and School Admin environments.
- **CSS3**: 8 modular external stylesheets (`main.css`, `layout.css`, `components.css`, `tables.css`, `forms.css`, `charts.css`, `animations.css`, `responsive.css`).
- **Bootstrap 5.3**: Responsive 12-column grid utilities and breakpoint architecture.
- **Tailwind CSS**: Utility styling configured with `preflight: false` and `collapse: false` to harmonize cleanly with Bootstrap 5.3.
- **Vanilla JavaScript (ES6+)**: Modular frontend controllers for navigation, collapsible sidebars, advanced data tables, inline form validation, modals/drawers, interactive charts, and ephemeral UI simulations.
- **ApexCharts**: Interactive Area, Line, Bar, Stacked Bar, and Donut analytical visualizations with time-range controls.
- **GSAP**: Restrained micro-interactions honoring `prefers-reduced-motion`.
- **Lucide Icons**: Consistent enterprise iconography across all modules.

### Strict Rules Verified
- **No JS Component Frameworks**: Zero React, Next.js, Vue, Angular, TypeScript, JSX, or TSX.
- **No Browser Storage**: Zero `localStorage`, `sessionStorage`, `IndexedDB`, or client databases. All demonstration state lives strictly in ephemeral JavaScript memory (`window.S2D_DEMO`) and resets cleanly on page refresh.
- **No Fake Backend**: Zero mock REST servers or fake network interceptors.
- **100% Professional English**: Complete interface and fictional sample dataset in English only.

---

## 2. Project Structure

```text
school-calling-system/
├── index.html                      # Platform Hub & Role Environment Launcher
├── auth/                           # Authentication Suite (login, forgot-password, reset-password)
├── super-admin/                    # Portal 1: Global Governance (30 HTML pages)
│   ├── dashboard.html
│   ├── schools/                    # list, add, edit, details (7 tabs)
│   ├── school-admins/              # list, add, edit, details
│   ├── validity/                   # overview, rules
│   ├── recharges/                  # overview, create-plan, history
│   ├── calling-duration/           # index
│   ├── calling-schedules/          # index (interactive weekly matrix)
│   ├── call-history/               # index (with slide-over call inspector)
│   ├── reports/                    # index
│   ├── subscriptions/              # overview, create
│   ├── payments/                   # overview, details
│   ├── devices/                    # list, register, details (Android Enterprise MDM readiness)
│   ├── roles-permissions/          # list (RBAC matrix), create
│   └── settings/                   # general, notifications, audit-logs
├── franchise/                      # Portal 2: Territory Partner Operations (20 HTML pages)
│   ├── dashboard.html
│   ├── schools/                    # list, add, edit, details (territory-scoped)
│   ├── students/                   # list, add, edit, details
│   ├── bulk-upload/                # index (drag-and-drop Excel/CSV preview & validation)
│   ├── classes/                    # index
│   ├── validity/                   # index
│   ├── recharges/                  # index
│   ├── calling-duration/           # index (bounded by Super Admin ceiling)
│   ├── calling-schedules/          # index
│   ├── call-history/               # index
│   ├── reports/                    # index
│   ├── commissions/                # index (18% partner commission ledger & analytics)
│   ├── transactions/               # index
│   └── settings/                   # index
├── school-admin/                   # Portal 3: Campus & Hostel Operations (29 HTML pages)
│   ├── dashboard.html
│   ├── students/                   # list, add, edit, details (7 tabs)
│   ├── bulk-upload/                # index
│   ├── classes/                    # list, sections (separate pages)
│   ├── guardians/                  # list, add, edit, details (authorized number whitelist)
│   ├── student-codes/              # index (backend-issued cryptographic code workflow)
│   ├── student-status/             # index (activation/deactivation & audit trail)
│   ├── calling-schedules/          # index (school, class & student weekly calendar)
│   ├── calling-duration/           # index
│   ├── validity/                   # index
│   ├── recharges/                  # overview, student-recharge
│   ├── call-history/               # index
│   ├── student-reports/            # index
│   ├── class-reports/              # index
│   ├── device-assignments/         # list, assign (with AE enrollment pre-flight check)
│   ├── hostel-wardens/             # list, add, edit, details
│   └── settings/                   # index
└── assets/
    ├── css/                        # 8 modular stylesheets
    ├── js/                         # 11 modular ES6+ scripts (including api-config.js)
    ├── vendor/                     # Local copies of Bootstrap 5.3, Tailwind, Lucide, ApexCharts, GSAP
    ├── images/                     # Brand SVG mark
    └── icons/                      # Favicon SVG
```

---

## 3. Django REST Framework (DRF) Integration Readiness

1. **Centralized Endpoint Registry**: Update `window.S2DApiConfig.config.mode` in `assets/js/api-config.js` from `'DEMO_IN_MEMORY'` to `'LIVE_DRF_API'` and point `baseUrl` to your Django REST gateway.
2. **Server-Side Pagination**: `S2DApiConfig.buildDrfQueryParams()` formats `page`, `page_size`, `search`, `ordering`, and filter keys directly for `rest_framework.pagination.PageNumberPagination` and `django-filter`.
3. **Serializer Field Error Binding**: `S2DApiConfig.applyDrfFieldErrors(formEl, errorPayload)` maps DRF `400 Bad Request` field error dictionaries directly onto `[data-drf-error="<field_name>"]` slots.
4. **Backend Security Boundary**:
   - Unique student calling codes must be generated exclusively on the server (`POST /api/v1/school-admin/student-codes/issue/`).
   - Franchise-to-school and school-to-student tenant isolation, RBAC permission matrices, guardian phone whitelists, calling schedules, duration limits, and Android Enterprise device policies must be enforced server-side.

---

## 4. Running Locally

Serve the `school-calling-system` directory over any standard static HTTP server:

```bash
cd school-calling-system
python3 -m http.server 8080 --bind 0.0.0.0
```

Then open `http://localhost:8080/index.html` in your browser.
