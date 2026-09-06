# Converter Starter Layout Area Measurement

- status: `starter_layout_bounding_areas_measured_not_extracted_signoff_area`
- measured cells: `4/4`
- source: `Magic select top cell; units microns; box values`

| cell | width (um) | height (um) | bounding area (um2) | measured |
| --- | ---: | ---: | ---: | --- |
| `row_dac_10b` | `12.0` | `5.2` | `62.400000000000006` | `True` |
| `sar_readout_12b` | `14.0` | `6.4` | `89.60000000000001` | `True` |
| `shared_converter_mux` | `16.0` | `7.0` | `112.0` | `True` |
| `aimc_converter_macro` | `22.0` | `10.8` | `237.60000000000002` | `True` |

These are bounding-box measurements of the current starter geometries. They replace a guessed rectangle with a reproducible Magic measurement, but they are not area signoff for the missing integrated transistor converter.

## Refused Claim

does not claim transistor converter area, density, DRC/LVS signoff area, or strict post-layout payload readiness
