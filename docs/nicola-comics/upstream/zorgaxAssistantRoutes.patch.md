# Upstream patch — MyZubster public Zorgax → Nicola Comics

Target repository: `MyZubster-Ecosystem/myzubster`

Issue: `#1176`

The connected GitHub app currently has read access but cannot create a branch in the upstream repository (GitHub returned HTTP 403), so this directory contains the minimal implementation proposal ready for a maintainer to apply.

## 1. Add the service

Copy `nicolaComicsService.js` to:

`src/services/nicolaComicsService.js`

The service is read-only and permits only `gallery`, `detail`, `candidate`, `next_steps`.

## 2. Wire it into `src/routes/zorgaxAssistantRoutes.js`

Add near the other service imports:

```js
const { askNicolaComics } = require('../services/nicolaComicsService');
```

Before the generic `answer(...)` call inside `router.post('/chat', ...)`, add explicit pilot routing. Do not send unrelated prompts to the Nicola endpoint.

```js
const nicola = req.body?.nicolaComics;
if (nicola && typeof nicola === 'object') {
  const pilot = await askNicolaComics({
    action: nicola.action || 'gallery',
    comicId: nicola.comicId || null,
    question: req.body?.message || req.body?.prompt || 'Nicola Comics pilot'
  });
  logFunnelEvent('zorgax_message_sent', req, {
    webResearch: false,
    sourceCount: Array.isArray(pilot.sources) ? pilot.sources.length : 0,
    integration: 'nicola-comics'
  });
  return res.json({
    ok: true,
    entity: 'ZORGAX-001',
    response: pilot.answer,
    ...pilot,
    external_sources: [],
    access: publicAccess(req.zorgaxAccess),
    featureAccess: req.zorgaxPolicy,
    accessNotice: null
  });
}
```

This makes the integration explicit and deterministic instead of trying to infer a participant/pilot from arbitrary natural language.

## 3. Environment

Production may set:

```text
NICOLA_COMICS_BASE_URL=https://myzubster-mvp.onrender.com
```

The service defaults to the same public HTTPS URL so no localhost or private machine is exposed.

## 4. Public request contract

Example request to the existing MyZubster public assistant route:

```json
{
  "message": "Mostrami i fumetti di Nicola",
  "useWeb": false,
  "nicolaComics": {
    "action": "gallery"
  }
}
```

Detail:

```json
{
  "message": "Apri la prima tavola",
  "useWeb": false,
  "nicolaComics": {
    "action": "detail",
    "comicId": "n4k48-comic-001"
  }
}
```

## 5. Evidence boundary

The upstream route must preserve the participant endpoint values. In particular:

- `n4k48-comic-001` is only `NFT_CANDIDATE / PROPOSED_FOR_REVIEW`;
- `rights_status` remains `TO_VERIFY`;
- no `MINTED` claim is permitted without independently verifiable network, contract, token ID and transaction hash;
- this bridge performs no mint, wallet, payment or persistent write.

## 6. E2E acceptance check

After upstream deployment, verify:

`public Zorgax → gallery → detail/card → image → candidate → rights/on-chain status → next_steps`

Only after this request crosses the deployed MyZubster public Zorgax route and reaches the public Nicola Comics endpoint should issue #1176 record the upstream E2E as PASS.
