// When served from Docker's nginx (localhost), use same-origin so /api/ is proxied.
// In production (Vercel, etc.), fall back to the Render backend URL.
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

export const CONFIG = {
  // Use the local backend or fall back to the production API URL
  API_BASE_URL: window.CSEHUB_API_BASE_URL || (isLocal ? "" : "https://csehub-ezdl.onrender.com"),
  SUPABASE_URL: "https://uayvvxmyiuofigddtmxb.supabase.co",
  // The client-side publishable key for Supabase Auth
  SUPABASE_ANON_KEY: window.CSEHUB_SUPABASE_ANON_KEY || "sb_publishable_Vzp_KX58h55EzmOi03qKPA_ntUBSyhK"
};
