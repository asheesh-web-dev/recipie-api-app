# django session management

In Django, `django.contrib.session`s manages sessions.

## The Two Core Elements

The framework splits session management into two distinct parts:

- **Session Middleware:** The `SessionMiddleware` interceptor runs automatically on every request and response. It looks for a unique cookie in the browser, loads the matching data, and attaches it to request.session.
- **Session Engine:** The database backend or cache storage where Django saves the actual session data.

## How the Process Works

```text
[Browser Request] ──> Reads Session Cookie ──> [SessionMiddleware] ──> Looks up ID in Storage (DB/Cache)
                                                                                │
[Browser Storage] <── Attaches Cookie ID <─── [SessionMiddleware] <── Populates request.session
```


1. **Incoming Request:** The browser sends a cookie named `sessionid`.
2. **Lookup:** `SessionMiddleware` reads this ID and retrieves the data from your chosen storage engine.
3. **Usage:** Django makes this data available in your code as a dictionary-like object: `request.session['key'] = 'value'`.
4. **Outgoing Response:** The middleware automatically saves any updates back to your storage engine and refreshes the browser cookie expiration.

## Storage Options (Engines)

You can configure where Django saves session data in your settings.py using SESSION_ENGINE:

- **Database (Default):** Saves data in the `django_session` SQL table. It is highly reliable but causes database reads on every single page load.
- **Cache:** Saves data in memory systems like Redis or Memcached. This option is extremely fast and ideal for high-traffic sites.
- **Cached Database:** Writes data to the cache first for speed, but persists it to the database so sessions survive server restarts.
- **Cookies:** Encrypts and stores the entire session payload directly inside the user's browser cookie. This saves server space but limits data to 4KB per user.
