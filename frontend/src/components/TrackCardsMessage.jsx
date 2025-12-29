import "../styles/MessageBase.css";
import "../styles/TrackCardsMessage.css";

function TrackCardsMessage({ cards, source }) {
  const sourceLabel = source === "lastfm" ? "Last.fm" : (source || "Last.fm");

  return (
    <div className="message bot-message api-cards">
      <div className="api-cards-header">
        <span>Recommendations from {sourceLabel}</span>
      </div>
      <div className="api-cards-grid">
        {cards.map((card, index) => {
          const title = card.name || "Untitled";
          const subtitle = card.artist || (card.type === "artist" ? "Artist" : "");
          const typeLabel = card.type ? card.type.toUpperCase() : "ITEM";
          const href = card.url || "";
          const clickable = Boolean(href);

          return (
            <div className="api-card" key={`${title}-${index}`}>
              <div className="api-card-top">
                <span className="api-card-type">{typeLabel}</span>
              </div>
              <div className="api-card-title">{title}</div>
              {subtitle ? <div className="api-card-subtitle">{subtitle}</div> : null}
              {clickable ? (
                <a
                  className="api-card-link"
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Open on Last.fm
                </a>
              ) : (
                <div className="api-card-link api-card-link-muted">No link</div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TrackCardsMessage;
