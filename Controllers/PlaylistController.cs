using Microsoft.AspNetCore.Mvc;

namespace MusicAiRecomApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PlaylistController : ControllerBase
    {
        // GET api/playlist
        [HttpGet]
        public IActionResult GetAllPlaylists()
        {
            return Ok(new[] { "Playlist Étude", "Playlist Entraînement" });
        }

        // POST api/playlist
        [HttpPost]
        public IActionResult CreatePlaylist([FromBody] string playlistName)
        {
            return Ok($"Playlist '{playlistName}' créée !");
        }
    }
}