# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask-based Content Management System with Supabase backend. Users authenticate via OAuth (Google + planned Claremont SSO), with dual data storage: client-side localStorage cache and persistent Supabase tables. Developer-focused with full provider metadata exposure and extensible configuration system.

## Development Commands

### Running the Application
```bash
# Navigate to the Flask implementation directory
cd supabase/flask-implementation

# Run the development server (default port 3000)
uv run main.py --port 3000

# Run with custom host/port
uv run main.py --host 0.0.0.0 --port 5000

# Run without debug mode
uv run main.py --debug false
```

### Dependencies
```bash
# Add new dependencies
uv add <package-name>

# Core dependencies are: flask, supabase, python-dotenv, sqlalchemy
```

### Supabase CLI (Optional for Local Testing)
```bash
# Login and initialize
supabase login
supabase init
supabase link --project-ref <project-id>

# Start local Supabase instance
supabase start

# Reset database schema
supabase db reset
```

## Architecture

### Application Factory Pattern
- Entry point: [main.py](supabase/flask-implementation/main.py) creates app via `create_app()` factory
- App initialization in [app/__init__.py](supabase/flask-implementation/app/__init__.py):
  - Supabase client attached to Flask app instance with custom `ClientOptions` (timeouts, schema)
  - Secret key loaded from environment
  - Blueprints registered for auth, dashboard, data, profile routes

### Authentication Flow
- OAuth providers: Google (implemented), Claremont SSO (planned)
- Flow: `/login` → `sign_in_with_oauth()` → redirect to provider → `/callback` handles tokens
- Session management via Flask sessions; user data includes identity provider metadata
- Multi-provider account linking supported (display raw provider info in profile)
- First login auto-inserts default `user_configs` + 3 mock rows to `user_content`

### Data Architecture - Dual Storage

**Local Cache (Client-side):**
- Browser localStorage as JSON array
- Schema: `{timestamp: "ISO-string", id: "uuid", content: "markdown"}`
- FIFO eviction by default (modular for future custom algorithms)
- Headers and limits controlled by per-user config
- ~50 lines of vanilla JS (no frameworks) in dashboard template

**Remote Database (Supabase):**
- Same schema as local cache
- Tables: `user_content` (with RLS), `user_configs` (JSONB)
- Row Level Security (RLS) enforces user isolation via `auth.uid()`
- CRUD via forms, server-rendered

### Configuration System
- Per-user JSONB configs stored in `user_configs` table
- Default: `{"headers": ["timestamp", "id", "content"], "eviction": {"method": "fifo", "enabled": true, "limit": 10}}`
- Fully editable via `/profile` route; changes apply on page refresh (no server restart)
- Headers are fully customizable (no validation enforced, but code comments note future validation path)
- Placeholder for future custom eviction logic via client-side JS upload

### Supabase Integration Details

**Database Tables:**
```sql
-- user_content: timestamp (TIMESTAMPTZ), id (UUID PK), content (TEXT)
-- user_configs: user_id (UUID PK), config (JSONB)
-- Both have RLS policies: FOR ALL USING (auth.uid() = user_id)
```

**Client Configuration:**
- Uses `ClientOptions` with custom timeouts (10s for postgrest/storage)
- Schema set to "public"
- Anon key for client-side operations; service key for admin tasks (optional)

### Route Structure
- [app/routes/auth.py](supabase/flask-implementation/app/routes/auth.py): `/login`, `/callback`, protected route decorator
- [app/routes/dashboard.py](supabase/flask-implementation/app/routes/dashboard.py): Main UI with both local/remote data sections
- [app/routes/cache.py](supabase/flask-implementation/app/routes/cache.py): Data CRUD `/api/content`, config endpoints `/api/config`
- Profile routes: Display raw provider identities (JSON), config editing, account linking UI

### UI/UX Patterns
- Server-rendered templates (Jinja2)
- Plain HTML/CSS (no frameworks like Bootstrap by default)
- Minimal JavaScript (~50 lines total) for localStorage interactions only
- Dynamic table headers from user config
- Dummy data auto-generation with customizable fields
- Confirmation dialogs on delete operations

## Environment Setup

Required `.env` file in [supabase/flask-implementation/](supabase/flask-implementation/):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key  # Optional for server-side admin
SECRET_KEY=your-flask-secret-key
```

**Supabase Dashboard Setup:**
1. Enable Google OAuth in Auth > Providers (redirect: `http://localhost:3000/auth/callback`)
2. Run SQL for tables (see [docs/planning.md](supabase/flask-implementation/docs/planning.md) lines 29-48)
3. Verify RLS enabled globally

## Key Technical Patterns

### Security
- All routes protected with `@login_required` decorator (except `/login`, `/callback`)
- RLS policies on all user-facing tables
- User isolation enforced at database level via `auth.uid()`
- No sensitive data in code/commits (use `.env`)

### Extensibility Points
- Custom eviction algorithms: Future support for user-uploaded JS snippets in config (noted as risky but developer-focused)
- Validation: Code comments indicate paths for JSONB validation (e.g., "ensure headers not empty")
- Provider linking: Architecture supports multiple OAuth providers per user
- Mock data generation: Customizable dummy content fields

### Data Flow
1. User authenticates → Supabase OAuth → Flask session established
2. Dashboard route fetches user config from `user_configs`
3. Template renders with config vars (headers, eviction params)
4. Client JS uses config to manage localStorage
5. Remote data operations hit `/api/content` routes → Supabase RLS filters by user

## Testing Workflow
1. Run app: `uv run main.py`
2. Login via Google at `http://localhost:3000/login`
3. Verify `/profile` shows identity provider metadata
4. Update config → refresh dashboard to see changes applied
5. Test local cache: Add rows, verify FIFO eviction at limit
6. Test remote: CRUD operations with user isolation
7. Edge cases: Multi-provider linking, config changes without reboot

## Architectural Decisions & Tradeoffs

- **Local storage requires JS**: No way around localStorage API; kept minimal (~50 lines)
- **Uniform schema**: Same `{timestamp, id, content}` for both local and remote
- **Plain HTML/CSS**: Prioritizes development speed; Bootstrap can be added later if needed
- **Developer-focused**: Exposes raw provider metadata, supports account linking, extensible configs
- **Security vs. flexibility**: Custom eviction logic (JS eval) noted as risky but fitting for developer tool
- **Future validation**: Deferred to repo contributions; code comments mark insertion points

## Important Notes

- Working directory is project root `/Users/aleccandidato/Projects/cms`
- Flask app is in `supabase/flask-implementation/` subdirectory
- Python 3.12+ required (managed via `uv`)
- Not a git repository (as of current state)
- Tests directory exists but empty (placeholder for future implementation)
- Claremont SSO planned but not yet implemented; manual email linking fallback available
