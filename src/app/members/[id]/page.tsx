import Link from 'next/link';
import { notFound } from 'next/navigation';
import PoliticianImage from '@/components/PoliticianImage';

// Define the type for a politician based on the database schema
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

// Generate metadata for the page
export async function generateMetadata({ params }: { params: { id: string } }) {
    // Ensure params.id is properly handled
    const id = params.id;
    const politician = await getPolitician(id);

    if (!politician) {
        return {
            title: '議員が見つかりません',
        };
    }

    return {
        title: `${politician.name} | Manifest Monitor`,
        description: `${politician.name}（${politician.party || '無所属'}）の詳細情報`,
    };
}

// Fetch politician data by ID
async function getPolitician(id: string): Promise<Politician | null> {
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
        console.error("Supabase URL or Anon Key is missing in environment variables.");
        return null;
    }

    // Use dynamic import for supabase-js to ensure it's treated correctly server-side
    const { createClient } = await import('@supabase/supabase-js');
    const supabase = createClient(supabaseUrl, supabaseAnonKey);

    const { data, error } = await supabase
        .from('politicians')
        .select('*')
        .eq('id', id)
        .single();

    if (error) {
        console.error("Error fetching politician:", error);
        return null;
    }

    return data;
}

export default async function PoliticianDetailPage({ params }: { params: { id: string } }) {
    // Ensure params.id is properly handled
    const id = params.id;
    const politician = await getPolitician(id);

    if (!politician) {
        notFound(); // This will show the closest not-found.tsx page
    }

    // Placeholder image if no photo_url is available
    const imageUrl = politician.photo_url || '/placeholder.svg';

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
                {/* Back Button */}
                <div className="mb-6">
                    <Link href="/members" className="text-blue-600 hover:underline flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        議員一覧に戻る
                    </Link>
                </div>

                {/* Politician Detail Card */}
                <div className="bg-white rounded-lg shadow-md p-8">
                    <div className="md:flex">
                        {/* Left Column - Photo */}
                        <div className="md:w-1/3 flex justify-center mb-6 md:mb-0">
                            <div className="relative w-48 h-48">
                                <PoliticianImage
                                    src={imageUrl}
                                    alt={`Photo of ${politician.name}`}
                                    fallbackSrc="/placeholder.svg"
                                />
                            </div>
                        </div>

                        {/* Right Column - Details */}
                        <div className="md:w-2/3 md:pl-8">
                            <h1 className="text-3xl font-bold mb-2 text-black">{politician.name}</h1>
                            {politician.name_kana && (
                                <p className="text-gray-600 mb-4">{politician.name_kana}</p>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                                <div className="bg-gray-50 p-3 rounded">
                                    <h3 className="text-sm font-semibold text-gray-500">所属</h3>
                                    <p className="text-lg text-black">{politician.chamber}</p>
                                </div>

                                <div className="bg-gray-50 p-3 rounded">
                                    <h3 className="text-sm font-semibold text-gray-500">政党</h3>
                                    <p className="text-lg text-black">{politician.party || '無所属'}</p>
                                </div>

                                <div className="bg-gray-50 p-3 rounded">
                                    <h3 className="text-sm font-semibold text-gray-500">選挙区</h3>
                                    <p className="text-lg text-black">{politician.district || '---'}</p>
                                </div>

                                {politician.term_end && (
                                    <div className="bg-gray-50 p-3 rounded">
                                        <h3 className="text-sm font-semibold text-gray-500">任期満了</h3>
                                        <p className="text-lg text-black">{politician.term_end}</p>
                                    </div>
                                )}
                            </div>

                            {politician.profile_url && (
                                <div className="mt-6">
                                    <a
                                        href={politician.profile_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors"
                                    >
                                        公式プロフィールを見る
                                    </a>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Additional Sections - Can be expanded later */}
                    <div className="mt-12 border-t pt-8">
                        <h2 className="text-2xl font-bold mb-6 text-black">発言・活動</h2>
                        <p className="text-gray-600">
                            この議員の国会での発言や活動記録は現在準備中です。
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}
