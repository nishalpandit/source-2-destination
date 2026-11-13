# View organization

Keep view code separated by responsibility in `Source2Destination/`:

- Super admin views: `admin_views.py`
- Franchise admin views: `franchise-views.py`
- School admin views: `school_views.py`
- API views: `Api_views.py` (preserve capitalization)

Use these files for future work. Do not mix role-specific or API business logic into another role's view module or the shared `views.py`. Keep shared portal/auth routing in `views.py` where appropriate.

Python cannot use a hyphenated filename in a normal import statement. The current URL configuration imports `franchise_views.py`, and `franchise-views.py` currently forwards to that module. When implementing franchise changes, make `franchise-views.py` the implementation source and adapt the import bridge as needed so URL routing still works; keep compatibility code free of duplicated business logic.

Preserve existing user changes. Do not reorganize unrelated code merely to apply this convention.
