using System;
using System.Collections.Generic;

namespace MusicAiRecomApp.Models.DTO
{
    public class PlaylistRequest
    {
        public string Name { get; set; } = string.Empty;
        public string Context { get; set; } = string.Empty;
        public TimeSpan? Duration { get; set; }
    }
}
