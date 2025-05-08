import { createServerClient, type CookieOptions } from '@supabase/ssr';
import { cookies } from 'next/headers';

// Define the type for the environment variables for clarity
interface SupabaseEnv {
    NEXT_PUBLIC_SUPABASE_URL: string;
    NEXT_PUBLIC_SUPABASE_ANON_KEY: string; // Use anon key for server components unless auth needed
    // Add SUPABASE_SERVICE_ROLE_KEY if you need elevated privileges server-side, e.g.,
    // SUPABASE_SERVICE_ROLE_KEY: string;
}

// Note: This function is designed to be called within Server Components, Route Handlers, or Server Actions
// It relies on the 'cookies()' function from 'next/headers'
export function createClient() {
    const cookieStore = cookies(); // Get cookies within the function scope

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

    if (!supabaseUrl || !supabaseAnonKey) {
        throw new Error(
            'Missing Supabase environment variables for server client. Check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.'
        );
    }

    return createServerClient<SupabaseEnv>(
        supabaseUrl,
        supabaseAnonKey,
        {
            cookies: {
                // The get, set, and remove methods are adapted from the official Supabase SSR examples
                get(name: string) {
                    return cookieStore.get(name)?.value;
                },
                set(name: string, value: string, options: CookieOptions) {
                    try {
                        cookieStore.set({ name, value, ...options });
                    } catch (error) {
                        // The `set` method was called from a Server Component.
                        // This can be ignored if you have middleware refreshing
                        // user sessions.
                    }
                },
                remove(name: string, options: CookieOptions) {
                    try {
                        cookieStore.set({ name, value: '', ...options });
                    } catch (error) {
                        // The `delete` method was called from a Server Component.
                        // This can be ignored if you have middleware refreshing
                        // user sessions.
                    }
                },
            },
        }
    );
}

// Example of creating a service role client if needed (requires SUPABASE_SERVICE_ROLE_KEY in .env)
/*
import { createClient as createAdminClient } from '@supabase/supabase-js'

export function createAdminClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const supabaseServiceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!;

   if (!supabaseUrl || !supabaseServiceRoleKey) {
        throw new Error(
            'Missing Supabase environment variables for admin client. Check NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.'
        );
    }

  // Use the standard client for service role, not the SSR one
  return createAdminClient(supabaseUrl, supabaseServiceRoleKey, {
     auth: {
            autoRefreshToken: false,
            persistSession: false
        }
  });
}
*/
