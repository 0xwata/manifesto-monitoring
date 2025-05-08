import PoliticianCard from '@/components/PoliticianCard';
import Link from 'next/link';

// Define the type for a politician based on the database schema
// Using snake_case as returned by Supabase unless transformed
type Politician = {
    id: string;
    name: string;
    name_kana: string | null;
    photo_url: string | null;
    party: string | null;
    district: string | null;
    chamber: string;
    term_end: string | null;
    profile_url: string | null;
    created_at: string;
    updated_at: string;
};

export default async function MembersPage() {
    // Reverted to direct client creation for server-side fetch
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
        console.error("Supabase URL or Anon Key is missing in environment variables.");
        return <div className="p-4 text-red-500">Configuration error.</div>;
    }

    // Use dynamic import for supabase-js to ensure it's treated correctly server-side if needed
    const { createClient } = await import('@supabase/supabase-js');
    const supabase = createClient(supabaseUrl, supabaseAnonKey);

    console.log("Fetching politicians from Supabase (using direct client)...");
    const { data: politicians, error } = await supabase
        .from('politicians')
        .select('*')
        .order('chamber', { ascending: true }) // Example ordering
        .order('name_kana', { ascending: true }); // Then by kana name

    if (error) {
        console.error("Error fetching politicians:", error);
        // Consider rendering an error message to the user
        return <div className="p-4 text-red-500">Error loading members: {error.message}</div>;
    }

    if (!politicians || politicians.length === 0) {
        return <div className="p-4">No members found.</div>;
    }

    console.log(`Fetched ${politicians.length} politicians.`);

    // Separate politicians by chamber
    const representatives = politicians.filter(p => p.chamber === '衆議院');
    const councilors = politicians.filter(p => p.chamber === '参議院');

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white border-b">
                <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-blue-700">
                        <Link href="/">Manifest Monitor</Link>
                    </h1>
                    <nav>
                        <ul className="flex space-x-6">
                            <li><Link href="/members" className="text-blue-600 hover:underline">議員一覧</Link></li>
                            <li><Link href="/policies" className="text-gray-600 hover:underline">政策一覧</Link></li>
                            <li><Link href="/manifests" className="text-gray-600 hover:underline">マニフェスト一覧</Link></li>
                        </ul>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-4 py-8">
                {/* Representatives Section */}
                <section className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <h2 className="text-xl font-bold mb-6 pb-2 border-b text-black">
                        衆議院議員 ({representatives.length}名)
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {representatives.map((politician) => (
                            <PoliticianCard key={politician.id} politician={politician} />
                        ))}
                    </div>
                </section>

                {/* Councilors Section */}
                <section className="bg-white rounded-lg shadow-sm p-6">
                    <h2 className="text-xl font-bold mb-6 pb-2 border-b text-black">
                        参議院議員 ({councilors.length}名)
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {councilors.map((politician) => (
                            <PoliticianCard key={politician.id} politician={politician} />
                        ))}
                    </div>
                </section>
            </main>
        </div>
    );
}
