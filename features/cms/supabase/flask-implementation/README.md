# Flask CMS with Supabase
A simple Flask-based Content Management System (CMS) using Supabase for backend services. Users authenticate via OAuth (primarily Google, with Claremont SSO placeholder), access two data "databases" per user: a temporary client-side cache (localStorage) and a permanent remote database (Supabase tables). Configs are user-editable and dynamic, with modular eviction support for future customization. Built for developers: exposes full provider metadata, supports account linking, and is extensible.
## Features
- **Authentication**: OAuth sign-in (Google via Supabase; Claremont SSO via manual email linking placeholder). Multi-provider account linking for unified profiles.
- **User Databases**:
  - **Local Cache**: Client-side localStorage with FIFO eviction; configurable headers/rows.
  - **Remote Database**: Supabase tables for persistent markdown content; full CRUD with user isolation (RLS).
- **Configs**: Per-user editable JSON (headers, eviction method/limit); applies on refresh (no server reboot).
- **UI**: Plain HTML/CSS; minimal JS for localStorage; server-rendered tables/forms.
- **Developer Tools**: Raw identity provider metadata display; dummy data generation; validation paths noted for extensibility.
## Setup
### Prerequisites
- Python 3.12+ (via `uv` for virtual env).
- Supabase account ([database.new](https://database.new)).
### Installation
1. Clone repo and cd to project: `cd flask-implementation`.
2. Set up env: `uv init --no-readme --no-workspace` (if not done) and `uv add flask supabase python-dotenv sqlalchemy`.
3. Create `.env` with Supabase creds:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key  # From dashboard > Settings > API > Reveal API Keys
   SECRET_KEY=your-flask-secret-key
   ```
4. Set up Supabase:
   - Create project; enable Google OAuth in Auth > Providers (redirect: `http://localhost:3000/auth/callback`).
   - Run SQL (in SQL Editor):
     ```sql
     -- Tables for user isolation
     CREATE TABLE user_content (id UUID PRIMARY KEY, user_id UUID, timestamp TIMESTAMPTZ, content TEXT);
     ALTER TABLE user_content ENABLE ROW LEVEL SECURITY;
     CREATE POLICY "CRUD own content" ON user_content FOR ALL USING (auth.uid() = user_id);
     CREATE TABLE user_configs (user_id UUID PRIMARY KEY, config JSONB DEFAULT ...);
     ALTER TABLE user_configs ENABLE ROW LEVEL SECURITY;
     CREATE POLICY "Manage own config" ON user_configs FOR ALL USING (auth.uid() = user_id);
     ```
   - (Placeholder) Claremont SSO: Email IT for OAuth creds (client ID/secret/endpoints); if SAML, implement later.
### Running
- Start: `uv run main.py --port 3000`.
- Visit `http://localhost:3000/login` to OAuth authenticate.
- Dashboard: View/edit data; Profile: Manage configs/identities.
## Architecture
- **Flask App**: Factory pattern in `app/__init__.py` with Supabase client.
- **Routes**: Auth (`/login`, `/callback`), Dashboard (`/dashboard` with two sections), Data/API (`/api/content`, `/api/config`), Profile (`/profile` for metadata/configs).
- **Supabase Integration**: Client (`create_client` with `ClientOptions`); RLS for security; OAuth via `sign_in_with_oauth`.
- **Local Cache**: localStorage (JS ~50 lines); configurable eviction (default FIFO; extensible via JS snippet in config).
- **Extensibility**: Comments in code for validation (e.g., headers not empty); eval-able custom logic in future.
## Usage
- Login via Google → Profile shows linked identities (raw JSON).
- Update configs in Profile (e.g., change headers ["timestamp", "id", "content"] or limit).
- Dashboard local cache: Add/remove rows (eviction auto-applies).
- Remote: CRUD markdown content with dummy auto-gen.
## Testing
- Basic run: `uv run main.py` → No errors.
- Full flow: Login → Add data → Verify eviction/configs.
- Use `supabase start` (CLI) for local Supabase testing.
## Roadmap
- Claremont SSO: Confirm OAuth with IT; integrate if possible.
- Validation: Add JSONB checks in routes (repo contribution).
- Custom Eviction: Store user-uploaded JS in config; eval in client (dev-focused).
## Contributing
- Part of web-dev-ecosystem monorepo.
- Issues: [GitHub](#).
- PR: Add validation/custom logic per comments in code.

## TO DO: