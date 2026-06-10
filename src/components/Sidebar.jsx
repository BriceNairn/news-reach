{articles.map((article) => (
  <div className="article-card" key={article.id}>
    <strong>{article.title}</strong>
    <span>{article.source}</span>
    <small>{article.locations.length} locations</small>
  </div>
))}