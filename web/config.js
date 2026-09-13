/* Where the API lives.

   Local dev and the Railway-hosted copy both serve the API from the same
   origin, so the base stays empty. On Vercel the frontend is static and the
   API is elsewhere, so it points at Railway.

   Replace the Railway URL below after your first deploy. */
window.FOYER_API =
  ["localhost", "127.0.0.1"].includes(location.hostname)
    ? ""
    : "https://foyer-backend-production.up.railway.app";
