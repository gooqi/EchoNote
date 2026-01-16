import { createSupabaseAuthMiddleware } from "@echonote/supabase/middleware";

import { env } from "../env";
import type { AppBindings } from "../hono-bindings";

export const supabaseAuthMiddleware = createSupabaseAuthMiddleware<AppBindings>(
  {
    supabaseUrl: env.SUPABASE_URL,
    supabaseAnonKey: env.SUPABASE_ANON_KEY,
  },
);
