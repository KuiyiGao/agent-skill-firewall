---
id: arcgis-location-platform
name: ArcGIS Location Platform (basemaps, geocoding, places, routing; Maps SDK for JS 5.x)
provider: Esri
category: geo
source: resources-doc
listed_as: "ArcGIS"
status: changed
cost_model: free-tier
free_allowance: "Monthly: 2,000,000 basemap tiles and 20,000 geocodes (not stored); ~20,000 simple routes and a small Places tier (~500 searches / 100 details) (unverified); no card unless you enable pay-as-you-go"
card_required: false
signup_minutes: 10
auth: "Query token=<API key> on REST; esriConfig.apiKey or ApiKeyManager.fromKey(key) in JS. Keys come from 'API key credentials' (expire after 1 day to 1 year)"
base_url: "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer | https://places-api.arcgis.com/arcgis/rest/services/places-service/v1 | https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World | https://basemapstyles-api.arcgis.com/arcgis/rest/services/styles/v2"
env_vars: [ARCGIS_API_KEY]
sdks: ["browser: @arcgis/map-components@5.1.27 (CDN https://js.arcgis.com/5.1/)", "browser: @arcgis/core@5.1.27", "js: @esri/arcgis-rest-request@4.11.0 + @esri/arcgis-rest-geocoding/-places/-routing@4.11.0", "maplibre: @esri/maplibre-arcgis@1.3.1 (peer maplibre-gl ~5.24.0 || ~6.3.0)", "python: arcgis==2.4.3 (Python 3.11-3.14, heavy deps)"]
sandbox: "No test mode; the monthly free tier is the sandbox. Without pay-as-you-go enabled, calls just stop working when a free tier is used up (no bill)"
offline_mock: easy
demo_effect: 4
integration_hours: "1-3"
risk: low
track_fit: [hacknc-general, hacknc-beginner, hacknc-frutiger-aero, hacknc-community]
finance_fit: 3
tags: [maps, geocoding, places, poi, routing, basemap, heatmap, clustering, choropleth, 3d-globe, maplibre, atm-locator, fraud-geo]
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://developers.arcgis.com/documentation/", "https://location.arcgis.com/pricing/", "https://developers.arcgis.com/javascript/latest/", "https://developers.arcgis.com/maplibre-gl-js/", "https://github.com/Esri/arcgis-rest-js"]
---

## TL;DR
This is the no-card option of the three map providers. A free **ArcGIS Location Platform** account (formerly the "ArcGIS Developer" account) includes monthly free tiers (2M basemap tiles, 20k geocodes), and nothing is billed unless you add a payment method for pay-as-you-go. Create an **API key credential** in the portal. Legacy API keys were retired on 2026-06-27 and now return errors, so older tutorials' keys will not work. It has the strongest visual kit for the money: a 3D globe (`<arcgis-scene>`), ocean and imagery basemaps, heatmap and cluster renderers, and a MapLibre plugin if you prefer MapLibre.

## Request structure
Every REST call takes `f=json` and `token=$ARCGIS_API_KEY`. Coordinates are `x=lng, y=lat` (WGS84).
- **Geocode:** `GET .../World/GeocodeServer/findAddressCandidates?singleLine=...&maxLocations=1&outFields=PlaceName,Type` returns `{spatialReference:{wkid:4326}, candidates:[{address, location:{x,y}, score, attributes, extent}]}`. Siblings: `reverseGeocode?location=x,y`, `suggest`. Add `forStorage=true` only if you keep results, which is billed (stored geocodes have no free tier).
- **Places:** `GET .../places-service/v1/places/near-point?x=&y=&radius=(m)&searchText=|categoryIds=&pageSize=` returns `{results:[{placeId, name, location:{x,y}, categories:[{categoryId,label}], distance}], pagination:{nextUrl}}`. Also `/places/within-extent`, `/places/{placeId}?requestedFields=...`, and `/categories?filter=bank` to look up category IDs.
- **Route:** `GET|POST .../Route_World/solve?stops=x1,y1;x2,y2&returnDirections=false` returns `{routes:{features:[{attributes:{Total_TravelTime, Total_Kilometers, Total_Miles}, geometry:{paths:[[[x,y],...]]}}]}}` (attribute names unverified). There are also ClosestFacility, ServiceArea (drive-time polygons) and OD cost matrix services.
- **Basemap style (MapLibre/Mapbox style JSON):** `https://basemapstyles-api.arcgis.com/arcgis/rest/services/styles/v2/styles/arcgis/navigation?token=...`. Other styles: `arcgis/streets`, `arcgis/topographic`, `arcgis/imagery`, `arcgis/dark-gray`, `arcgis/oceans` (unverified for oceans in v2).
```bash
curl -s "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?f=json&singleLine=Old+Well,+Chapel+Hill,+NC&maxLocations=1&token=$ARCGIS_API_KEY" | jq '.candidates[0].location'
curl -s "https://places-api.arcgis.com/arcgis/rest/services/places-service/v1/places/near-point?f=json&x=-79.0512&y=35.9121&radius=1500&searchText=bank&pageSize=10&token=$ARCGIS_API_KEY" | jq '.results[] | {name, distance}'
curl -s "https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve?f=json&stops=-79.0512,35.9121;-78.7875,35.8776&returnDirections=false&token=$ARCGIS_API_KEY" | jq '.routes.features[0].attributes'
```
**Python** (`arcgis` is heavy: pandas, numpy, dask, pyarrow; plain `requests` against the URLs above is the light path):
```python
import os, itertools
from arcgis.gis import GIS                               # pip install arcgis==2.4.3
from arcgis.geocoding import geocode, get_places_api
gis = GIS(api_key=os.environ["ARCGIS_API_KEY"])
hit = geocode("Old Well, Chapel Hill, NC", max_locations=1)[0]   # uses the active GIS; for_storage=False by default
print(hit["address"], hit["location"])                   # {'x': -79.05..., 'y': 35.91...}
banks = get_places_api(gis).search_by_radius([-79.0512, 35.9121], radius=1500, search_text="bank")
for p in itertools.islice(banks, 10):                    # the generator auto-pages; islice caps quota use
    print(p["name"], p["distance"])
```
**JS REST** (browser or Node): `const authentication = ApiKeyManager.fromKey(key);` then `geocode({ singleLine, authentication })`, `findPlacesNearPoint({ x, y, radius, searchText, authentication })` (the response field is `results`, although the README destructures `places`) and `solveRoute({ stops: [[x1,y1],[x2,y2]], authentication })`.

**Basemap in a web page**. Option A is the Maps SDK 5.1 web components (set the key *before* the SDK script):
```html
<script>var esriConfig = { apiKey: "YOUR_ARCGIS_API_KEY" };</script>   <!-- inject at build time; restrict the key -->
<script type="module" src="https://js.arcgis.com/5.1/"></script>
<arcgis-map basemap="arcgis/navigation" center="-79.0512,35.9121" zoom="13" style="height:100vh"></arcgis-map>
<!-- 3D globe: <arcgis-scene basemap="satellite" ground="world-elevation"></arcgis-scene> -->
```
Option B is MapLibre + the Esri plugin (UMD needs maplibre-gl 5.x, because 6.x ships ESM only):
```html
<link href="https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl.css" rel="stylesheet" />
<script src="https://unpkg.com/maplibre-gl@5.24.0/dist/maplibre-gl.js"></script>
<script src="https://unpkg.com/@esri/maplibre-arcgis@1.3.1/dist/umd/maplibre-arcgis.min.js"></script>
<div id="map" style="height:100vh"></div>
<script>
  const map = new maplibregl.Map({ container: "map", center: [-79.0512, 35.9121], zoom: 13 });
  maplibreArcGIS.BasemapStyle.applyStyle(map, { style: "arcgis/navigation", token: window.ARCGIS_API_KEY });
</script>
```

## Simulation & free sandbox
- Signup at location.arcgis.com is free with no card. Without pay-as-you-go you keep only the privileges whose free tier is not yet used up, so a runaway loop fails instead of billing you (search-snippet).
- Create the key under Content, New item, Developer credentials, API key credentials. Tick only Basemaps, Geocoding (not stored), Places and Routing, and set the expiration (default about 3 months, max 1 year). Editing a credential's privileges or expiration invalidates the keys generated from it.
- The output is real JSON in the shapes above. Public Living Atlas layers (demographics, boundaries) are free sample data for choropleths (access rules for individual layers unverified).

## Visualization ideas
- Heatmap of flagged transactions: `GeoJSONLayer` with `renderer: { type: "heatmap" }` (`HeatmapRenderer`), weighted by `amount`.
- Clustered branches/ATMs: `featureReduction: { type: "cluster" }` on a FeatureLayer/GeoJSONLayer, or the plugin's `feature-layer-cluster` example in MapLibre.
- Choropleth of risk by county: class-breaks renderer on county polygons (Living Atlas or your own GeoJSON) driven by `risk_score`.
- 3D glossy globe for the Frutiger Aero track: `<arcgis-scene basemap="satellite" ground="world-elevation">` with camera fly-to on alerts. The classic `oceans` basemap gives the aqua look in 2D.
- Route/"impossible travel" lines from `routes.features[0].geometry.paths`.

## Scenarios (official)
- Display a map with a basemap style (Maps SDK for JS, MapLibre, Leaflet, OpenLayers tutorials).
- Search for an address or POI with the geocoding service (`findAddressCandidates`, `suggest`).
- Find places near a point or in an extent, with categories (Places service).
- Find a route and directions, the closest facility or service areas (routing services).
- Host your own data as feature layers and visualize it with smart mapping renderers (heatmap, clusters, class breaks).

## Finance-agent angle
Medium (inferred). Best for the "monitoring dashboard with a map" variant:
- A fraud geo-anomaly layer: a heatmap of flagged swipes plus impossible-travel lines between consecutive swipes (geocode merchants once and cache them).
- A branch/ATM locator agent: Places `near-point` with `categoryIds` from `/categories?filter=atm`.
- A client/portfolio risk choropleth: synthetic client addresses aggregated by county, plus Living Atlas income layers for context.
- An agent-activity globe: each agent action as a pulse at its counterparty location (inferred, purely visual).

## Gotchas
- Legacy API keys (created before 2024-06-27) were retired on 2026-06-27 and now error. Use API key credentials, which expire, so check the expiry date before demo day.
- "ArcGIS Developer account" tutorials refer to what is now the ArcGIS Location Platform account. ArcGIS Online org accounts bill in credits and cannot use basemap sessions.
- Geocode results with `forStorage=true` are billed at about $4 per 1k with no free tier. Places results must not be stored permanently (Places API terms). Cache only for demo replay.
- The Python `PlacesAPI.search_by_radius` generator follows `pagination.nextUrl` automatically, so each page is a billable request. Cap it with `islice`.
- `@esri/maplibre-arcgis@1.3.1` pins its peer `maplibre-gl` to `~5.24.0 || ~6.3.0`, and maplibre-gl 6.x has no UMD `maplibre-gl.js` (ESM `.mjs` only).
- Maps SDK 5.x favors web components (`<arcgis-map>`, `$arcgis.import(...)`). Many 4.x widget-based snippets (`new MapView`, `require([...])`) are outdated.
- Show "Powered by Esri" attribution; MapLibre needs `customAttribution` for it.
- `@esri/arcgis-rest-routing` defaults to `route.arcgis.com`, while Esri samples use `route-api.arcgis.com`. Pass `endpoint` explicitly if a key is rejected (unverified).

## Mock fallback
Set `GEO_MODE=live|cache`. Write adapters `geocode(addr)`, `places_near(x, y, q)` and `route(stops)` that return ArcGIS JSON from `fixtures/arcgis/<sha1(params)>.json`; live mode records them. Keep a converted GeoJSON copy (`location.x/y` to `[lng, lat]`, `paths` to LineString) for the map. Offline basemap: MapLibre with OpenStreetMap raster tiles (light use, attribution) or a local PMTiles extract (pmtiles@4.5.0 + @protomaps/basemaps@5.7.2). In the Maps SDK, swap `basemap` to a local `VectorTileLayer`/GeoJSON-only map when `navigator.onLine` is false. Fake transactions come from a seeded generator (e.g. Faker) with lat/lng inside the Triangle bounding box.

## Sources
- https://registry.npmjs.org/@esri/arcgis-rest-geocoding, -routing, -places, -request (4.11.0: default URLs geocode-api / route.arcgis.com / places-api, `findAddressCandidates`, `ApiKeyManager`, openapi `results` schema, "cannot permanently store places") (sdk-source)
- https://registry.npmjs.org/@esri/maplibre-arcgis (1.3.1 README, examples/basemap-*.html, peerDependencies) (sdk-source)
- https://registry.npmjs.org/maplibre-gl (6.13.0 ESM-only dist; 5.24.0 UMD) (sdk-source)
- https://registry.npmjs.org/@arcgis/core and @arcgis/map-components (5.1.27: HeatmapRenderer, FeatureReductionCluster, GeoJSONLayer, `oceans` basemap id, arcgis-scene `ground="world-elevation"`) (sdk-source)
- https://raw.githubusercontent.com/Esri/jsapi-resources/main/templates/js-maps-sdk-cdn/index.html (CDN 5.1, `$arcgis.import`) (sdk-source)
- https://github.com/Esri/developer-support and EsriDevEvents 2026 demos (`var esriConfig = { apiKey }` before js.arcgis.com/5.x) (sdk-source)
- https://github.com/Esri/arcgis-maps-sdk-unreal-engine-samples (route-api.arcgis.com/.../Route_World/solve) (sdk-source)
- https://pypi.org/project/arcgis/ (2.4.3 wheel: `GIS(api_key=)`, `geocode`, `PlacesAPI.search_by_radius` pagination) (sdk-source)
- https://location.arcgis.com/pricing/ (2M tiles, 20k geocodes not stored, $4/1k stored) (search-snippet)
- https://location.arcgis.com/faq/ and https://location.arcgis.com/help/billing/ (free signup, payment method only for pay-as-you-go) (search-snippet)
- https://developers.arcgis.com/documentation/security-and-authentication/api-key-authentication/api-key-legacy/ and the security FAQ (legacy keys retired 2026-06-27, expiry 1 day to 1 year) (search-snippet)
- https://developers.arcgis.com/documentation/glossary/arcgis-location-platform/ (formerly ArcGIS Developer account) (search-snippet)
- https://docs.insightmaps.app/guide/legal/attribution and https://plans.apis.io/plans/esri-arcgis/esri-arcgis-plans-pricing/ (third-party: 20k routes, Places 500/100) (search-snippet)
