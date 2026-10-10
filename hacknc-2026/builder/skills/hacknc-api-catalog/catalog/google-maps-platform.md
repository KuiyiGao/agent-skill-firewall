---
id: google-maps-platform
name: Google Maps Platform (Maps JS, Geocoding, Places API (New), Routes API)
provider: Google
category: geo
source: resources-doc
listed_as: "Google Maps"
status: changed
cost_model: free-tier
free_allowance: "Per-SKU monthly free caps since 2025-03-01 (the $200 credit is gone): Essentials 10,000 (Dynamic Maps, Geocoding, Compute Routes), Pro 5,000 (Text Search Pro), Enterprise 1,000, Map Tiles 100,000, Text Search IDs-only unlimited; billing account with card required"
card_required: true
signup_minutes: 15
auth: "Query ?key=<key> (Maps JS, Geocoding) or header X-Goog-Api-Key: <key> plus required X-Goog-FieldMask (Places New, Routes)"
base_url: "https://maps.googleapis.com/maps/api | https://places.googleapis.com/v1 | https://routes.googleapis.com"
env_vars: [GOOGLE_MAPS_API_KEY, VITE_GOOGLE_MAPS_API_KEY]
sdks: ["browser: @googlemaps/js-api-loader@2.1.3", "react: @vis.gl/react-google-maps@1.10.1", "browser: @googlemaps/markerclusterer@2.6.2", "python: google-maps-places==0.9.1", "python: google-maps-routing==0.11.2", "python (legacy web services): googlemaps==4.10.0", "node: @googlemaps/places@3.0.1", "heatmap: @deck.gl/google-maps@9.4.0"]
sandbox: "No test mode or test keys; the per-SKU free caps are the sandbox. New Cloud customers also get a $300 / 90-day trial credit. mapId DEMO_MAP_ID works in dev."
offline_mock: easy
demo_effect: 5
integration_hours: "1-3"
risk: medium
track_fit: [hacknc-general, hacknc-beginner, hacknc-frutiger-aero, hacknc-community, mlh-gemini]
finance_fit: 3
tags: [maps, geocoding, places, poi, routing, heatmap, clustering, 3d, atm-locator, fraud-geo, mcp, grounding]
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://developers.google.com/maps/documentation", "https://developers.google.com/maps/billing-and-pricing/pricing", "https://developers.google.com/maps/documentation/places/web-service/text-search", "https://developers.google.com/maps/documentation/routes", "https://developers.google.com/maps/ai/grounding-lite"]
---

## TL;DR
The most polished map for a 2-minute demo (vector maps, Advanced Markers, photorealistic 3D), with a generous free tier: since 2025-03-01 each SKU has its own monthly free cap (Essentials 10k / Pro 5k / Enterprise 1k) instead of the old $200 credit. You still need a Cloud billing account with a card before any key works. Use the *new* APIs (Places API (New), Routes API). They need an `X-Goog-FieldMask` header, and the fields you request decide the price tier.

## Request structure
**Geocoding** (Essentials): `GET /maps/api/geocode/json?address=...&key=...` returns `{status:"OK", results:[{formatted_address, place_id, geometry:{location:{lat,lng}}, types}]}`.
```bash
curl -s "https://maps.googleapis.com/maps/api/geocode/json?address=Old+Well,+Chapel+Hill,+NC&key=$GOOGLE_MAPS_API_KEY" | jq '.results[0].geometry.location'
```
**Places API (New) Text Search**: `POST https://places.googleapis.com/v1/places:searchText`. Headers: `X-Goog-Api-Key` and `X-Goog-FieldMask`. The mask is required, and `*` returns every field at the highest SKU. Body: `textQuery` (required), `includedType` (`bank`, `atm`), `strictTypeFiltering`, `maxResultCount` (1-20), `locationBias`/`locationRestriction`, `openNow`, `minRating`. Response: `{places:[{id, displayName:{text}, formattedAddress, location:{latitude,longitude}}], nextPageToken}`. Siblings: `POST /v1/places:searchNearby`, `GET /v1/places/{id}`, `POST /v1/places:autocomplete`.
```bash
curl -s -X POST https://places.googleapis.com/v1/places:searchText \
  -H "Content-Type: application/json" -H "X-Goog-Api-Key: $GOOGLE_MAPS_API_KEY" \
  -H "X-Goog-FieldMask: places.id,places.displayName,places.formattedAddress,places.location" \
  -d '{"textQuery":"bank near Chapel Hill, NC","includedType":"bank","maxResultCount":10}'
```
How the mask sets the SKU: `places.id` alone bills as Text Search Essentials (IDs Only), which is free without limit. Adding name, address or location bills as Pro (5k free, then about $32 per 1k). Adding rating, phone, website or hours bills as Enterprise (1k free, about $35 per 1k) (search-snippet).

**Routes API**: `POST https://routes.googleapis.com/directions/v2:computeRoutes` (matrix: `/distanceMatrix/v2:computeRouteMatrix`). A field mask is required. Each waypoint is given as `address`, `placeId` or `location.latLng`.
```bash
curl -s -X POST https://routes.googleapis.com/directions/v2:computeRoutes \
  -H "Content-Type: application/json" -H "X-Goog-Api-Key: $GOOGLE_MAPS_API_KEY" \
  -H "X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline" \
  -d '{"origin":{"address":"Old Well, Chapel Hill, NC"},"destination":{"address":"RDU Airport, NC"},"travelMode":"DRIVE"}'
# -> {"routes":[{"distanceMeters":31000,"duration":"1700s","polyline":{"encodedPolyline":"..."}}]}  (numbers illustrative)
```
**Python** (Places New over gRPC: the API key goes in client_options and the field mask in metadata):
```python
import os
from google.maps import places_v1                     # pip install google-maps-places==0.9.1
client = places_v1.PlacesClient(client_options={"api_key": os.environ["GOOGLE_MAPS_API_KEY"]})
resp = client.search_text(
    request={"text_query": "ATM near Franklin St, Chapel Hill", "included_type": "atm", "max_result_count": 10},
    metadata=[("x-goog-fieldmask", "places.id,places.displayName,places.location")])
for p in resp.places:
    print(p.display_name.text, p.location.latitude, p.location.longitude)
```
For geocoding only: `googlemaps.Client(key=...).geocode("Old Well, Chapel Hill")`. Its `places`, `directions` and `distance_matrix` helpers call the **legacy** endpoints.

**Basemap in a web page** (npm + Vite):
```js
import { setOptions, importLibrary } from "@googlemaps/js-api-loader";   // v2 API: there is no Loader class
setOptions({ key: import.meta.env.VITE_GOOGLE_MAPS_API_KEY, v: "weekly" });
const { Map } = await importLibrary("maps");
const { AdvancedMarkerElement } = await importLibrary("marker");
const map = new Map(document.getElementById("map"),
  { center: { lat: 35.9121, lng: -79.0512 }, zoom: 14, mapId: "DEMO_MAP_ID" });  // Advanced Markers need a mapId
new AdvancedMarkerElement({ map, position: { lat: 35.9121, lng: -79.0512 }, title: "Old Well" });
```
React: `<APIProvider apiKey={key}><Map defaultCenter={pos} defaultZoom={12} mapId="DEMO_MAP_ID"><AdvancedMarker position={pos}/></Map></APIProvider>`. The same library has `<Map3D>` for photorealistic 3D.

**For agents:** Maps Grounding Lite is a hosted MCP server at `https://mapstools.googleapis.com/mcp` (header `X-Goog-Api-Key`) with the tools `search_places`, `compute_routes` and `lookup_weather`. The Gemini API's "Grounding with Google Maps" tool is not on the free tier. The paid tier includes 5,000 prompts/month, then $14 per 1k (search-snippet).

## Simulation & free sandbox
- There are no test keys. The free caps reset monthly per SKU, so a hackathon stays at $0 unless something loops. In Cloud Console, set per-API daily quotas (the Quotas page) and add a budget alert. An alert does not stop spending; a quota does.
- Use two keys. The browser key is restricted to "Websites" (`http://localhost:5173/*` plus your deploy domain) and to the Maps JavaScript API only. The server key is limited to the Places, Routes and Geocoding APIs.
- `DEMO_MAP_ID` gives you the vector map and Advanced Markers in development without creating a map ID.
- The output is real live data: the JSON shapes above, and tiles from Google's servers.

## Visualization ideas
- Clustered ATM/branch pins from `places[].location`: `new MarkerClusterer({ map, markers })` (@googlemaps/markerclusterer).
- Heat layer of flagged transactions (lat/lng weighted by `amount`): use deck.gl `HeatmapLayer` through `GoogleMapsOverlay` (@deck.gl/google-maps). The built-in `visualization.HeatmapLayer` was deprecated in May 2025 and is unavailable from May 2026.
- "Impossible travel" line: a red `google.maps.Polyline` with `geodesic: true` between two card swipes, labelled with the distance and the time gap. For driving context, decode `routes.polyline.encodedPolyline` with `google.maps.geometry.encoding.decodePath`.
- 3D photorealistic fly-over to a flagged branch (`<gmp-map-3d>` / `<Map3D>`). It looks very good on stage; the 3D SKU pricing is unverified.
- Simple choropleth: `map.data.loadGeoJson(url)` plus `map.data.setStyle(f => ({fillColor: color(f.getProperty("risk"))}))`.

## Scenarios (official)
- Store/branch locator: Places Text/Nearby Search with Maps JS and Advanced Markers.
- Address entry: Place Autocomplete (New) (`places:autocomplete`). Address Validation is a separate API.
- Delivery and logistics ETAs: Routes API `computeRoutes` / `computeRouteMatrix` (the Route Optimization API also exists).
- Grounding LLM agents in real places: the Maps Grounding Lite MCP server and Gemini's Maps grounding tool.

## Finance-agent angle
Medium (inferred). The map is the visual layer, not the finance logic.
- Fraud geo-anomaly: an agent geocodes each transaction's merchant and flags "impossible travel" (for example, two swipes 800 miles apart within 1 hour imply ~1,290 km/h, faster than an airliner at ~900 km/h). The map shows both pins and the line.
- Branch/ATM locator agent: "nearest ATM open now" via Text Search with `includedType:"atm"` and `openNow:true`, or through the Grounding Lite MCP `search_places` tool.
- Client-location risk map: geocode *synthetic* client addresses and color them by risk score. Never send real customer PII.

## Gotchas
- A billing account with a payment card is required even to stay inside the free caps, and card verification can stall signup. Do it before the hack starts.
- Caps are per SKU and not pooled. One Enterprise field in the mask (e.g. `places.rating`) bills the whole call as Enterprise, so never loop with `X-Goog-FieldMask: *`.
- Places (legacy), Directions and Distance Matrix became "Legacy" on 2025-03-01. Google says to keep them disabled on new projects, which then hit `LegacyApiNotActivatedMapError`. The `googlemaps` Python library (last release Jan 2023) and most old tutorials use these legacy APIs.
- `google.maps.Marker` has been deprecated since Feb 2024. `AdvancedMarkerElement` requires a `mapId`.
- @googlemaps/js-api-loader 2.x replaced the `Loader` class with `setOptions` + `importLibrary`, so v1 snippets break.
- Call the web services (Geocoding, Places, Routes) from your backend with the server key. A referrer-restricted browser key is rejected server-side.
- On auth failure the map goes grey with a "This page can't load Google Maps correctly" banner. Hook `window.gm_authFailure = () => switchToFallback()`.
- Terms of service: you may cache place IDs, but not most Places content, and Google content should not be shown on a non-Google basemap (unverified, check the Maps ToS).

## Mock fallback
Set `MAPS_MODE=live|cache`. Write adapters `geocode(addr)`, `search_places(q, near)` and `route(a, b)` that return Google's own response shapes. In live mode they write `fixtures/maps/<sha1(request)>.json`; in cache mode they read it back. For the map itself: if the script fails or `gm_authFailure` fires, render MapLibre GL JS with an OpenStreetMap raster source (`https://tile.openstreetmap.org/{z}/{x}/{y}.png`, light use and attribution required) or a PMTiles extract of the Triangle area served from `/public` (pmtiles@4.5.0 + @protomaps/basemaps@5.7.2), which works fully offline. Draw the same cached GeoJSON (`[lng, lat]` order). Precompute route polylines into GeoJSON LineStrings so routes still draw offline.

## Sources
- https://registry.npmjs.org/@googlemaps/js-api-loader (2.1.3 README: setOptions/importLibrary, v1-to-v2 migration) (sdk-source)
- https://registry.npmjs.org/@vis.gl/react-google-maps (1.10.1 README: APIProvider, Map, AdvancedMarker, Map3D, DEMO_MAP_ID) (sdk-source)
- https://registry.npmjs.org/@googlemaps/markerclusterer (2.6.2 README) (sdk-source)
- https://pypi.org/project/google-maps-places/ (0.9.1 wheel: `places_v1` client X-Goog-FieldMask note, REST URIs, SearchTextRequest fields) (sdk-source)
- https://pypi.org/project/google-maps-routing/ (0.11.2 wheel: computeRoutes/computeRouteMatrix URIs, field-mask examples, Waypoint.address) (sdk-source)
- https://pypi.org/project/googlemaps/ (4.10.0 sdist: geocoding.py, places.py legacy paths) (sdk-source)
- https://github.com/google-gemini/genai-processors/blob/main/examples/mcp_server.py and https://github.com/google-ai-edge/gallery/blob/main/mcp/README.md (Grounding Lite MCP URL and header) (sdk-source)
- https://developers.google.com/maps/billing-and-pricing/pricing-categories and /pricing (caps, Dynamic Maps $7/1k, Text Search IDs-only unlimited, Pro $32/1k) (search-snippet)
- https://developers.google.com/maps/get-started (billing required, $300 trial) (search-snippet)
- https://developers.google.com/maps/legacy and https://developers.google.com/maps/deprecations (legacy APIs, HeatmapLayer, Marker) (search-snippet)
- https://developers.google.com/maps/ai/grounding-lite and https://ai.google.dev/gemini-api/docs/pricing (search-snippet)
- https://www.woosmap.com/blog/google-maps-api-pricing-breakdown, https://mapatlas.eu/blog/google-maps-api-pricing-2026 (third-party SKU prices: Geocoding/Compute Routes $5/1k, Text Search Enterprise $35/1k) (search-snippet)
