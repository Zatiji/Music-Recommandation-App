using System;
using System.Collections.Generic;

namespace MusicAiRecomApp.Models
{
    public class Playlist
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Name { get; set; } = string.Empty;
        public string Context { get; set; } = string.Empty;  // Exemple : "étude", "entraînement", "gaming"
        public TimeSpan? Duration { get; set; }
        public List<Track> Tracks { get; set; } = new List<Track>();
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}
