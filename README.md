# Web Dev Ecosystem Monorepo

A monorepo for web development implementations, showcasing Progressive Web Apps (PWAs), web push notifications, and related technologies across multiple frameworks and variants.

## Structure

Organized into feature-first hierarchy: `features/{feature_name}/{variant}/`
- **`features/webpush/flask/`**: Flask backend with pywebpush for direct web push notifications.
- **`features/webpush/react/`**: Next.js PWA with web push on iOS/Android using MagicBell.
- **`features/pwa/vanilla/`**: Vanilla JS PWA implementation.
- Each subfeature includes: `README.md` (with TO DO), `AGENTS.md`, `docs/`.

## Standards

- **UV-Only Python**: All Python code uses `uv` for dependencies and execution.
- **CI Enforcement**: Validates required structures via `lint_structure.yml`.
- **Ecosystem Dispatcher**: Automates selective updates to subscribed cousin repos.

## Getting Started

1. Clone repo.
2. Use `uv` for Python subfeatures (e.g., `uv run main.py` in Flask).
3. See individual feature READMEs for detailed setup.

## Contributing

- Features in `features/{name}/{variant}`; add required structures.
- Include in `ecosystem.json` for automated updates.
- Follow UV policy and standards.

## TO DO:

- Add new features/variants.
- Enhance ecosystem safeguards.

## License

MIT