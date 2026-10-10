---
id: here-platform
name: HERE Platform (Maps API for JavaScript 3.2, Geocoding & Search v7, Routing v8, Isoline v8)
provider: HERE Technologies
category: geo
source: resources-doc
listed_as: "HERE Technologies Developer"
status: changed
cost_model: free-tier
free_allowance: "Base plan free monthly tier per service: ~30,000 transactions/month for Geocoding & Search and for map tiles; routing quoted as 5,000-30,000 (unverified, sources conflict); payment method required, the no-card Limited plan ended 2025"
card_required: true
signup_minutes: 20
auth: "Query apiKey=<key> on every REST call; new H.service.Platform({apikey}) in JS (OAuth 2.0 bearer tokens are the alternative)"
base_url: "https://{geocode|discover|browse|autosuggest|lookup}.search.hereapi.com/v1 | https://router.hereapi.com/v8 | https://isoline.router.hereapi.com/v8 | https://maps.hereapi.com/v3"
env_vars: [HERE_API_KEY]
sdks: ["browser: HERE Maps API for JavaScript 3.2 (CDN https://js.api.here.com/v3/3.2/)", "python: flexpolyline==0.1.0 (official polyline decoder; no maintained REST SDK, use requests)", "node: @here/flexpolyline@0.1.0"]
sandbox: "none; the Base plan's free monthly transactions are the sandbox, and a payment method must be on file"
offline_mock: easy
demo_effect: 3
integration_hours: "2-3"
risk: medium
track_fit: [hacknc-general, hacknc-community]
finance_fit: 2
tags: [maps, geocoding, places, poi, routing, isoline, clustering, fleet, logistics, atm-locator, fraud-geo]
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.here.com/docs", "https://github.com/heremaps/maps-api-for-javascript-examples", "https://www.here.com/get-started/pricing", "https://platform.here.com"]
---

## TL;DR
HERE offers logistics-grade geocoding, POI search and routing (truck, EV, isolines, matrix) plus a JS map SDK (3.2). The free path changed: the no-card **Limited plan** closed to new users on 2025-03-27 and stopped working on 2025-08-31. New accounts must add a payment method to get the **Base plan**, which includes free monthly transactions and charges only above them. Choose HERE when you need isolines ("reachable in 10 min") or category POI search by code; otherwise ArcGIS (no card) or Google is the smoother pick.

## Request structure
Every REST call takes `apiKey=$HERE_API_KEY` as a query parameter. Coordinates are written `lat,lng`.
- **Geocode:** `GET https://geocode.search.hereapi.com/v1/geocode?q=...&limit=1` returns `{items:[{title, id, resultType, address:{label, countryCode, city, postalCode,...}, position:{lat,lng}, mapView, scoring:{queryScore}}]}`. Reverse geocoding: `/v1/revgeocode?at=lat,lng`. HERE's Python lib sends it to the `geocode.search.hereapi.com` host; the docs use `revgeocode.search.hereapi.com` (unverified).
- **POI by free text:** `GET https://discover.search.hereapi.com/v1/discover?at=lat,lng&q=bank&limit=10`.
- **POI by category:** `GET https://browse.search.hereapi.com/v1/browse?at=lat,lng&categories=700-7010-0108` (ATM; bank = `700-7000-0107`). Each item has `title, position, distance, categories[], openingHours, contacts`.
- **Route:** `GET https://router.hereapi.com/v8/routes?transportMode=car&origin=lat,lng&destination=lat,lng&return=summary,polyline` returns `{routes:[{id, sections:[{summary:{duration (s), length (m)}, polyline:"<flexible polyline>"}]}]}`. Other `transportMode` values: `truck|pedestrian|bicycle|scooter|taxi|bus`.
- **Isoline:** `GET https://isoline.router.hereapi.com/v8/isolines?transportMode=car&origin=lat,lng&range[type]=time&range[values]=600` returns polygons encoded as flexible polylines (response field names unverified: `isolines[].polygons[].outer`).
- **Raster tiles** (usable from MapLibre/Leaflet): `https://maps.hereapi.com/v3/base/mc/{z}/{x}/{y}/png8?style=explore.day&size=512&apiKey=...`.
```bash
curl -s "https://geocode.search.hereapi.com/v1/geocode?q=Old+Well,+Chapel+Hill,+NC&limit=1&apiKey=$HERE_API_KEY" | jq '.items[0].position'
curl -s "https://browse.search.hereapi.com/v1/browse?at=35.9121,-79.0512&categories=700-7010-0108&limit=10&apiKey=$HERE_API_KEY" \
  | jq '.items[] | {title, distance, position}'
```
**Python** (plain `requests`; the official `here-location-services` 0.4.0 is from 2021 and unmaintained):
```python
import os, requests, flexpolyline                      # pip install requests flexpolyline==0.1.0
r = requests.get("https://router.hereapi.com/v8/routes", timeout=10, params={
    "transportMode": "car", "origin": "35.9121,-79.0512", "destination": "35.8776,-78.7875",
    "return": "summary,polyline", "apiKey": os.environ["HERE_API_KEY"]}).json()
sec = r["routes"][0]["sections"][0]
print(sec["summary"]["length"], "m", sec["summary"]["duration"], "s")
path = flexpolyline.decode(sec["polyline"])            # [(lat, lng), ...]; reverse to [lng, lat] for GeoJSON
```
**Basemap in a web page** (CDN, version 3.2 as used by HERE's official examples):
```html
<link rel="stylesheet" href="https://js.api.here.com/v3/3.2/mapsjs-ui.css" />
<script src="https://js.api.here.com/v3/3.2/mapsjs-core.js"></script>
<script src="https://js.api.here.com/v3/3.2/mapsjs-service.js"></script>
<script src="https://js.api.here.com/v3/3.2/mapsjs-ui.js"></script>
<script src="https://js.api.here.com/v3/3.2/mapsjs-mapevents.js"></script>
<div id="map" style="height:100vh"></div>
<script>
  const platform = new H.service.Platform({ apikey: window.HERE_API_KEY });   // inject at build time, don't commit
  const layers = platform.createDefaultLayers();
  const map = new H.Map(document.getElementById("map"), layers.vector.normal.map,
    { center: { lat: 35.9121, lng: -79.0512 }, zoom: 13, pixelRatio: window.devicePixelRatio || 1 });
  new H.mapevents.Behavior(new H.mapevents.MapEvents(map));   // pan/zoom
  H.ui.UI.createDefault(map, layers);
  map.addObject(new H.map.Marker({ lat: 35.9121, lng: -79.0512 }));
  platform.getRoutingService().calculateRoute(              // same params as the REST call
    { transportMode: "car", origin: "35.9121,-79.0512", destination: "35.8776,-78.7875", return: "polyline,summary" },
    (res) => res.routes[0].sections.forEach((s) => map.addObject(
      new H.map.Polyline(H.geo.LineString.fromFlexiblePolyline(s.polyline), { style: { lineWidth: 5 } }))),
    console.error);
</script>
```
POI search from JS: `platform.getSearchService().discover({ q, at }, ok, err)`.

## Simulation & free sandbox
- There are no test keys and no sandbox host. The Base plan's free monthly transactions are the sandbox, with billing only above them. HERE notes that pricing pages render per account and region, so check the free numbers on your own account's billing page.
- The official examples site loads a `test-credentials.js` with HERE's own demo key. Do not reuse it; create an app and key in platform.here.com (Access Manager, Apps, API keys).
- The output is real data in the shapes above. Routes come back as encoded flexible polylines, so decode them before drawing.

## Visualization ideas
- Clustered ATM/branch markers: `H.clustering.Provider` over `H.clustering.DataPoint(lat, lng)` (needs `mapsjs-clustering.js`), fed by `browse` items.
- Coverage isolines: 5/10/15-minute drive-time polygons around each branch, colored by tier, to show "ATM deserts" where no polygon reaches (fields: isoline polygons, `range.values`).
- Route lines with maneuver dots and an ETA panel (`summary.duration`, `actions[]`), as in the official A-to-B example.
- 3D extruded polygons per region (the "Extruded geo shapes" example) as a volume or risk bar map.

## Scenarios (official)
- Display a map, markers, info bubbles and GeoJSON/KML/GPX (Maps API for JS examples).
- Car, pedestrian and public-transport routing from A to B (`router.hereapi.com/v8/routes`); EV range as an isoline (`isoline.router.hereapi.com/v8/isolines`).
- Landmark/POI search (`discover`), marker clustering, indoor maps.
- Fleet and logistics: matrix routing, tour planning, truck attributes, traffic (product pages, search-snippet).

## Finance-agent angle
Weak to medium (inferred). Plausible uses:
- Branch/ATM coverage analysis with isolines ("which clients live more than 15 min from a fee-free ATM").
- Cash-logistics or field-agent route planning (truck/matrix routing).
- An impossible-travel check for card fraud: compare the routing `duration` between two swipe locations with the time between swipes.
For a monitoring dashboard these are side features; Google or ArcGIS give the same pins and lines with less signup friction.

## Gotchas
- A card or payment method is required at onboarding (Base plan). Allow 15-30 min for account creation, the billing form and app/key creation.
- Free-tier numbers conflict across 2026 sources (30k vs 5k for routing; old 250k "freemium" posts are obsolete), and a ~6% list-price increase from 2026-04-01 is reported (search-snippet). Set usage alerts in the billing console.
- Polylines use HERE **Flexible Polyline**, not Google's encoded polyline. Decode with `flexpolyline` / `H.geo.LineString.fromFlexiblePolyline`.
- Parameters are `lat,lng` (`at=35.91,-79.05`), while GeoJSON is `[lng, lat]`. Swapping them puts pins in Antarctica.
- The `apiKey` sits in the URL and is visible in browser devtools. Proxy REST calls through your backend; for the JS map, use a separate key (domain restriction options unverified).
- Load all `mapsjs-*.js` modules from the same version (3.2). 3.1 tutorials mostly work but differ in details (unverified).
- The npm package `@here/maps-api-for-javascript` lives on HERE's own registry (repo.platform.here.com), not npmjs.org. For a hackathon, use the CDN.
- developer.here.com (the URL on the HackNC doc) is the old portal. Accounts live at platform.here.com and docs at www.here.com/docs (unverified redirect).
- Storing search/geocode results long-term is restricted by the HERE terms (unverified).

## Mock fallback
Set `HERE_MODE=live|cache`. Write adapters `geocode(q)`, `browse(at, categories)`, `route(a, b)` and `isoline(at, seconds)` that return HERE's JSON shapes from `fixtures/here/<sha1(params)>.json`; live mode records them. Store decoded polylines and isoline polygons as GeoJSON next to the raw JSON so the map draws without the decoder. If the HERE JS SDK fails to load, render the same GeoJSON with MapLibre GL JS on OpenStreetMap raster tiles (`https://tile.openstreetmap.org/{z}/{x}/{y}.png`, light use and attribution required) or a local PMTiles extract (pmtiles@4.5.0) for fully offline use. For isolines without HERE, approximate them with `@turf/turf` `circle(center, km)` and label them "approx."

## Sources
- https://raw.githubusercontent.com/heremaps/maps-api-for-javascript-examples/master/README.md (examples list, "version 3.2") (sdk-source)
- https://raw.githubusercontent.com/heremaps/maps-api-for-javascript-examples/master/map-with-route-from-a-to-b/demo.html and demo.js (CDN URLs, Platform/createDefaultLayers, calculateRoute params, fromFlexiblePolyline) (sdk-source)
- .../search-for-landmark/demo.js (getSearchService().discover) and .../marker-clustering/demo.js (mapsjs-clustering.js) (sdk-source)
- https://raw.githubusercontent.com/heremaps/here-location-services-python/master/here_location_services/geocoding_search_api.py and routing_api.py (hosts geocode/discover/browse/lookup.search.hereapi.com, router.hereapi.com/v8/routes) (sdk-source)
- https://github.com/heremaps/xyz-showcase (boston-liquor/index.js: isoline.router.hereapi.com/v8/isolines with range[type]/range[values]) (sdk-source)
- https://pypi.org/project/flexpolyline/ (0.1.0 wheel: `decode()`) (sdk-source)
- GitHub code search: leaflet-providers, traccar-web (maps.hereapi.com/v3/base/mc tiles); third-party repos using categories 700-7010-0108 (ATM) and 700-7000-0107 (bank) (search-snippet)
- https://www.here.com/learn/blog/april-2025-platform-release-notes and july/august-2025 release notes (Limited plan closed 2025-03-27, ended 2025-08-31; payment method required for Base) (search-snippet)
- https://placematic.com/here-location-services/here-pricing/, https://apicostcalc.com/here.html, https://local-eyes.nl/here-maps-api-costs-in-2024/ (third-party free-tier numbers, 2026 price increase) (search-snippet)
