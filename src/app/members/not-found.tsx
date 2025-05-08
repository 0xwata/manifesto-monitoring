import Link from 'next/link';

export default function NotFound() {
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
                <div className="bg-white rounded-lg shadow-md p-8 text-center">
                    <h1 className="text-3xl font-bold mb-4">議員が見つかりません</h1>
                    <p className="text-gray-600 mb-8">
                        指定されたIDの議員情報は存在しないか、削除された可能性があります。
                    </p>
                    <Link
                        href="/members"
                        className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        議員一覧に戻る
                    </Link>
                </div>
            </main>
        </div>
    );
}
