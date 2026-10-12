# Public accounts and Google sign-in

The public account flow is: **sign in or register → connect a personal Groq API key → open the workspace**. Enable it with `PUBLIC_ACCOUNTS=true`. Email/password accounts work without Google credentials. Passwords use salted scrypt hashes; sessions store token hashes in SQLite. Each account has its own Chroma collection, registry, evaluation directory, provider client, and answer cache. Existing owner documents are not exposed to public accounts.

## Enable Google

1. Open [Google Cloud Console](https://console.cloud.google.com/) and select or create a project you own.
2. Configure Google Auth Platform branding and audience. Use an External audience for accounts outside your organization. While the OAuth app is in testing, add the intended Google accounts as test users; prepare the production audience before advertising unrestricted Google access.
3. Create an OAuth client of type **Web application**.
4. Add this exact authorized redirect URI:

   ```text
   https://vericore-evidence.onrender.com/api/auth/google/callback
   ```

5. In the Render service's Environment settings, privately set:

   ```text
   PUBLIC_ACCOUNTS=true
   PUBLIC_BASE_URL=https://vericore-evidence.onrender.com
   GOOGLE_CLIENT_ID=<your OAuth client ID>
   GOOGLE_CLIENT_SECRET=<your OAuth client secret>
   ```

6. Save and redeploy. Check `/api/auth/status`: `google_enabled` becomes true when both credentials are configured. Sign in through the Google button with an allowed test account, verify the return to `/setup`, add a valid Groq key, and open `/app`.

Do not paste the client secret into chat, commit it, or put it in frontend environment variables. Google client credentials belong to the deployment; individual users supply only their Groq keys.

For local OAuth testing, register a separate authorized callback at `http://127.0.0.1:5173/api/auth/google/callback` and set `PUBLIC_BASE_URL=http://127.0.0.1:5173`. Use `ENV=development` and the frontend proxy. OAuth callback URLs must match exactly.

The implementation uses Google's authorization-code flow, one-use state bound to an HttpOnly cookie, PKCE S256, and Google's HTTPS userinfo endpoint after server-side code exchange. It requires a verified email and uses Google's stable subject ID. Existing password accounts are not silently linked by matching email; use that account's password login instead. See [Google's OpenID Connect documentation](https://developers.google.com/identity/openid-connect/openid-connect).

## Storage and operational limits

- Groq keys are account-specific and held only in server memory. They are not persisted, echoed, or saved in browser storage. A restart requires reconnecting the key.
- Accounts and session hashes are in `<CHROMA_PATH>/accounts.sqlite3`; account registry/evaluation records are in `workspaces/<server-generated-user-id>/`. Document collections use separate server-generated names.
- Render Free has ephemeral storage. Accounts, uploaded documents, and saved evaluation runs may disappear after restart/redeployment. Durable public service requires durable storage.
- Email registration does not verify mailbox ownership and currently has no password reset, account linking, or account deletion interface. It is suitable for the current demo, not a completed enterprise identity service.
- Requests are rate-limited per process/IP. Account operations are serialized within each workspace. The deployed service uses one worker.
- The server's Groq key is never inherited by public accounts. Workspace APIs refuse access until that account connects a validated key.
- Keep public-account mode disabled if you need the previous owner-only local evaluation client; that client has no public-account login flow.
