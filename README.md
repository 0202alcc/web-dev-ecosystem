# Flask WebPush PWA Template

A starter template for building Progressive Web Apps (PWAs) with Flask backend and webpush notifications using pywebpush.

## Features
- **Flask Backend**: Clean, scalable Python backend with application factory pattern
- **WebPush Notifications**: Direct pywebpush integration for cross-platform push notifications (iOS and Android)
- **PWA Ready**: Progressive Web App capabilities with service worker and manifest
- **Secure Bot Protocol**: IP whitelist, timestamp validation, and optional JWT authentication
- **Local Network Focus**: Designed for home network deployment with Tailscale support
- **Frontend**: Full-featured PWA interface for testing push notifications

## Purpose
This template provides a ready-to-use foundation for new PWA projects. Clone and customize to quickly bootstrap your next Progressive Web Application with push notification support.

## Getting Started

See [documentation.md](docs/documentation.md) for detailed setup instructions.

## TODO

- [ ] **User Authentication System**: Implement Google/GitHub OAuth login so user IDs match authenticated profiles instead of device-based generation

## Tech Stack
- **Backend**: Python/Flask 3.0+
- **Notifications**: pywebpush library (direct Web Push API)
- **Security**: JWT authentication, IP whitelisting, timestamp validation
- **PWA**: Service workers, offline support, installability
- **Deployment**: Local network with Tailscale support

## TO DO:
- Add user authentication
- Expand documentation

### Future CI/CD Enhancements
#### 5. **Additional Infrastructure**
   - **Shared Utilities**: If needed, create composite actions in `.github/actions/` for common steps (e.g., setup Python/Node).
   - **Documentation**: Update `docs/` with guidelines for using reusable workflows in new repos.
   - **Testing**: Add a test job in `ci.yml` to validate reusable workflows (e.g., dry-run calls).

#### 6. **Future-Proofing for Dependencies**
   - **Workflow Dependencies**: If shared code dependencies arise, add `needs:` in `ci.yml` to chain jobs (e.g., lint before tests).
   - **Matrix Expansion**: If many features, convert to a matrix job in `ci.yml` that dynamically calls reusables based on changed paths.

#### Tradeoffs and Considerations
- **Complexity vs. Reusability**: Reusable workflows add indirection but enable seamless updates across repos.
- **Security**: Since workflows are called from public repos, ensure no secrets are exposed; use inputs for sensitive data.
- **Performance**: Global jobs (linting) should be <2-3 minutes; optimize with caching.
- **Maintenance**: Changes to reusables affect all calling repos—test thoroughly.

## License
*(Coming soon)*
