# API Design

Applies to HTTP/REST APIs. For GraphQL or gRPC, adapt the principles but follow the conventions of the respective ecosystem.

## URL structure

- Use `kebab-case` for path segments: `/user-profiles`, not `/userProfiles` or `/user_profiles`
- Use nouns for resources, never verbs: `/orders`, not `/getOrders`
- Nest resources only when the relationship is ownership and the nesting depth is ≤ 2:
  `/users/{id}/orders` — acceptable
  `/users/{id}/orders/{id}/items/{id}/details` — too deep, flatten it
- Use plural nouns for collections: `/articles`, `/comments`
- Resource identifiers in path: `{id}` for primary key, use UUIDs over sequential integers in public APIs

## HTTP methods

| Method | Use for | Idempotent | Body |
|--------|---------|-----------|------|
| `GET` | Read resource or collection | yes | no |
| `POST` | Create resource, trigger action | no | yes |
| `PUT` | Replace resource entirely | yes | yes |
| `PATCH` | Partial update | no | yes |
| `DELETE` | Remove resource | yes | no |

- Never use `GET` for operations with side effects
- Prefer `PATCH` over `PUT` for partial updates — `PUT` requires sending the full representation

## HTTP status codes

Return the most specific applicable code. Common codes:

| Code | Meaning | When to use |
|------|---------|-------------|
| `200` | OK | Successful GET, PUT, PATCH |
| `201` | Created | Successful POST that created a resource |
| `204` | No Content | Successful DELETE or action with no response body |
| `400` | Bad Request | Malformed request, validation failure |
| `401` | Unauthorized | Missing or invalid authentication |
| `403` | Forbidden | Authenticated but not authorized |
| `404` | Not Found | Resource does not exist |
| `409` | Conflict | State conflict (duplicate, version mismatch) |
| `422` | Unprocessable Entity | Valid syntax but semantic validation failed |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unexpected server-side failure |
| `503` | Service Unavailable | Downstream dependency unavailable |

- Never return `200` with an error payload — use the correct error code
- `404` vs `403`: if revealing existence is a security concern, return `404` consistently

## Versioning

- Version in the URL path: `/v1/`, `/v2/` — explicit, cacheable, easy to route
- Bump the major version only for breaking changes; additive changes (new fields, new endpoints) are non-breaking
- Maintain at least one previous major version during a deprecation window
- Announce deprecation via a `Deprecation` response header and documentation

## Request / response format

- Default content type: `application/json`
- Use `camelCase` for JSON field names
- Always return a consistent envelope for collections:
  ```json
  {
    "data": [...],
    "meta": {
      "total": 100,
      "page": 1,
      "per_page": 20
    }
  }
  ```
- For single resources, return the object directly (no wrapper):
  ```json
  { "id": "abc", "name": "Alice", "createdAt": "2026-04-20T10:00:00Z" }
  ```
- Use ISO 8601 for all timestamps: `2026-04-20T10:00:00Z`
- Use strings for large integers (> 2^53) to avoid precision loss in JavaScript clients

## Error response format

Return a consistent error body on all 4xx and 5xx responses:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "issue": "must be a valid email address" }
    ]
  }
}
```

- `code`: machine-readable uppercase string — stable across versions
- `message`: human-readable summary
- `details`: optional array for field-level or multi-error cases
- Never expose stack traces, internal paths, or database errors in the response body — log them server-side

## Pagination

Use cursor-based pagination for large or frequently updated collections; use offset pagination only for small, stable datasets.

### Cursor-based (preferred)
```json
{
  "data": [...],
  "meta": {
    "next_cursor": "eyJpZCI6MTIzfQ==",
    "has_more": true
  }
}
```

### Offset-based
```json
{
  "data": [...],
  "meta": {
    "total": 500,
    "page": 3,
    "per_page": 20
  }
}
```

- Default page size: 20; maximum: 100 — enforce server-side, never trust client values
- Document pagination strategy in the API reference

## Authentication

- Use `Authorization: Bearer <token>` for token-based auth (JWT, opaque tokens)
- Never pass credentials in query parameters — they appear in server logs and browser history
- Use HTTPS everywhere — never serve an API over plain HTTP
- Document the auth scheme in `README.md` or a dedicated API reference

## Rate limiting

- Always rate-limit public and authenticated endpoints
- Return `429 Too Many Requests` with `Retry-After` header when limit is exceeded:
  ```
  HTTP/1.1 429 Too Many Requests
  Retry-After: 30
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1745145600
  ```
- Document rate limits in the API reference

## Documentation

- Every API must have an OpenAPI (Swagger) spec — generate it from code annotations when possible
- Keep the spec versioned alongside the code in the repository
- Document all endpoints, request/response schemas, error codes, and auth requirements
