```markdown
# Framework and Feature Comparison

## Tooling Standards
For all Python code in the monorepo (including scripts under `/scripts` and features like Flask WebPush), `uv` must be used exclusively for dependency management and execution. This ensures reproducible environments and prevents inconsistencies. Always use commands like `uv run python <script>` or `uv pip install` instead of direct `python` or `pip`.
## WebPush Implementations
### Flask WebPush
- **Backend**: Python Flask server
- **Push Service**: pywebpush library (direct Web Push API)
- **Security**: IP whitelist + timestamp validation
- **Deployment**: Local network with Tailscale support
- **Pros**: No external APIs, full control, simple deployment
- **Cons**: Requires backend server, more setup
### React WebPush
- **Frontend**: React application
- **Push Service**: MagicBell SDK
- **Security**: API key authentication
- **Deployment**: Any static hosting
- **Pros**: No backend required, managed service
- **Cons**: External API dependency, less control
## PWA Implementations
### Vanilla PWA
- **Complexity**: Low
- **Features**: Basic offline support, installable
- **Use Case**: Learning PWAs, simple web apps
- **Bundle Size**: Minimal
### React PWA
- **Complexity**: Medium
- **Features**: Full PWA with routing, state management
- **Use Case**: Complex web applications
- **Bundle Size**: Larger
## Choosing the Right Implementation
### For Learning
- Start with **Vanilla PWA** for basic concepts
- Move to **Flask WebPush** for backend integration
### For Production Apps
- **Flask WebPush** for full-stack control
- **React WebPush** for rapid frontend development
### For Prototyping
- **React PWA** for quick MVPs
- **Vanilla PWA** for simple demos
```
