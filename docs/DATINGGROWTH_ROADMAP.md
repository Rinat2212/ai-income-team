# DatingGrowth AI — roadmap

## MVP added
- [x] Admin-only bot
- [x] SQLite catalog of manually verified public Telegram communities
- [x] Draft queue and approve/reject callbacks
- [x] Basic event counter for start deep-link payloads in the service bot
- [x] Environment configuration and safe default
- [x] No automatic posting or bulk messaging

## Next
1. Add unit tests for URL validation, database CRUD, status transitions and admin access.
2. Add a researcher agent that uses permitted public sources and stores source URL, timestamp, confidence and evidence; no scraping private content.
3. Add an LLM provider adapter behind an explicit configuration switch to generate community-specific admin proposals.
4. Add campaign codes and analytics; instrument @my_daivinchik_2212_bot to parse start payloads if its source is controlled by the owner.
5. Add collaboration states: discovered → reviewed → admin contacted manually → permission granted → campaign approved → completed.
6. Add analytics for approved placements, target-bot starts and conversions after target-side instrumentation exists.
7. Add deployment instructions for a free/low-cost host after secrets and environment are configured.

## Guardrails
- Never send bulk unsolicited DMs.
- Never post to a group without explicit permission from its administrator.
- Respect community rules, Telegram rate limits and opt-out requests.
- Keep bot tokens and API keys in environment secrets, never in Git.
- Human approval remains required for external outreach.
