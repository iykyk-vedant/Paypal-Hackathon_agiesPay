# AegisPay testing access

Updated 2026-10-03.

- No login, admin account, or password is required for the current dashboard.
- No authentication credentials were created or modified during the light-theme redesign.
- Existing provider credentials are loaded from `/app/.env`; do not expose their values.
- Preview origin is available via the `preview_endpoint` environment variable in this imported vanilla project. No `frontend/.env` exists.
- Test transactions and the initial October 2026 schedule are sample/sandbox data. Manual refund and freeze actions are intentionally unavailable.