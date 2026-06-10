import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";


const REGION_BY_COUNTRY = {
  // Oceania
  AS: "Oceania",
  NZ: "Oceania",

  // North America
  US: "North America",
  CA: "North America",
  MX: "North America",

  // Europe
  UK: "Europe",
  FR: "Europe",
  GM: "Europe",
  SP: "Europe",
  IT: "Europe",

  // Asia
  CH: "Asia",
  IN: "Asia",
  TH: "Asia",
  KS: "Asia",
  JA: "Asia",
  IR: "Asia",
  IS: "Asia",

  // Africa
  NI: "Africa",
  GH: "Africa",
  WA: "Africa",

  // South America
  BR: "South America",
  AR: "South America",
  CO: "South America",
};



function getArticleRegion(article) {
  const regions = new Set(
    (article.locations || [])
      .map((loc) => REGION_BY_COUNTRY[loc.country])
      .filter(Boolean)
  );

  if (regions.size === 0) return "Other";
  if (regions.size === 1) return [...regions][0];

  return "Multi-region";
}




function App() {
  const [articles, setArticles] = useState([]);
  const [selectedRegion, setSelectedRegion] = useState("All");
  const [selectedArticle, setSelectedArticle] = useState(null);

  useEffect(() => {
    fetch("/data/gdeltArticles.json")
      .then((res) => res.json())
      .then(setArticles)
      .catch((err) => console.error("Failed to load articles", err));
  }, []);

  const mappedArticles = articles.filter(
    (article) => article.locations && article.locations.length > 0
  );

  const articlesWithRegions = mappedArticles.map((article) => ({
    ...article,
    region: getArticleRegion(article),
  }));

  const regions = ["All", 
    ...new Set(articlesWithRegions.map((a) => a.region))
  ];

  const filteredArticles =
    selectedRegion === "All"
      ? articlesWithRegions
      : articlesWithRegions.filter(
        (article) => article.region === selectedRegion
      );

  const handleArticleClick = (article) => {
    if (selectedArticle?.id === article.id) {
      setSelectedArticle(null);
    } else {
      setSelectedArticle(article);
    }
  };

  const visibleArticles = selectedArticle ? [selectedArticle] : filteredArticles;

  return (
    <div className="app">
      <aside className="sidebar">
        <h1>News Reach</h1>
        <p>Track the News</p>

        
        <div className="region-filters">
          {regions.map((region) => (
            <button
              key={region}
              onClick={() => setSelectedRegion(region)}
              className={selectedRegion === region ? "active" : ""}
            >
              {region}
            </button>
          ))}
        </div>

        <h2>Articles</h2>

        {filteredArticles.map((article) => (
          <div className={
            selectedArticle?.id === article.id
              ? "article-card selected"
              : "article-card"
          }
          key={article.id}
          onClick={() => handleArticleClick(article)}
          >
            <strong>{article.title}</strong>
            <span>{article.source}</span>
            <span>
              <a href={article.url}>Read Article</a>
            </span>
            <small>{article.region} · {article.locations.length} locations</small>
          </div>
        ))}
      </aside>

      <main className="map-panel">
        <MapContainer
          center={[-34.9285, 138.6007]}
          zoom={6}
          className="map"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />


          {visibleArticles.flatMap((article) =>
            (article.locations || []).map((location) => (
              <Marker
                key={`${article.id}-${location.name}`}
                position={[location.lat, location.lng]}
              >
                <Popup>
                  <strong>{article.title}</strong>
                  <br />
                  {article.source}
                  <br />
                  {location.name}
                </Popup>
              </Marker>
            ))
          )}
        </MapContainer>
      </main>
    </div>
  );
}

export default App;