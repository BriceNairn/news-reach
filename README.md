# News Reach

News Reach is a data pipeline and interactive map that tracks global news stories usding GDELT data.

Every 15 minutes, a new GDELT Global Knowledge Graph (GKG) dataset is ingested, cleaned and enriched before being added to a searchable article store.

The processed data is then visualised in a React + Leaflet web application, allowing users to explore news stories geographically.

## Current Features

- Automated ingestion of GDELT GKG datasets
- Duplicate article detection
- Bad domain filtering
- Headline enrichment from source websites
- Geographic extraction and mapping
- Interactive Leaflet map with article sidebar
- Regional filtering
- Historical article retention

## Technology Stack

- Python
- React
- Vite
- Leaflet
- GDELT Global Knowledge Graph (GKG)