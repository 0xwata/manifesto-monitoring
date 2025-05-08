import { createBrowserClient } from '@supabase/ssr';

// Define the type for the environment variables for clarity
interface SupabaseEnv {
    NEXT_PUBLIC_SUPABASE_URL: string;
    NEXT_PUBLIC_SUPABASE_ANON_KEY: string;
}

// Function to create a Supabase client for client components
export function createClient() {
    // Ensure environment variables are defined
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
        throw new Error(
            'Missing Supabase environment variables. Check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY.'
        );
    }

    return createBrowserClient<SupabaseEnv>(
        supabaseUrl,
        supabaseAnonKey
    );
}

// Note: For server-side operations (Server Components, API Routes),
// you might create a separate server client using the service_role key
// or use the createServerClient from '@supabase/ssr' if handling auth.
// For simple data fetching in Server Components, the anon key is often sufficient
// if RLS policies allow read access.
