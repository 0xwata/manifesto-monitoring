"use client"; // Designate as a Client Component

import Link from 'next/link';
import PoliticianCardImage from './PoliticianCardImage';

// Define the props type based on the Politician type in the page component
type PoliticianCardProps = {
    politician: {
        id: string;
        name: string;
        name_kana?: string | null;
        photo_url: string | null;
        party: string | null;
        district: string | null;
        chamber: string;
    };
};

// Basic placeholder image URL
const PLACEHOLDER_IMAGE = '/placeholder.svg';

const PoliticianCard: React.FC<PoliticianCardProps> = ({ politician }) => {
    const imageUrl = politician.photo_url || PLACEHOLDER_IMAGE;

    return (
        <Link href={`/members/${politician.id}`} className="block">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
                <div className="flex items-start">
                    {/* Image */}
                    <div className="flex-shrink-0 mr-4">
                        <PoliticianCardImage
                            src={imageUrl}
                            alt={`Photo of ${politician.name}`}
                            fallbackSrc={PLACEHOLDER_IMAGE}
                        />
                    </div>

                    {/* Details */}
                    <div className="flex-1">
                        <h3 className="text-lg font-semibold mb-1 text-black">
                            {politician.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-1">
                            所属: <span className="font-medium text-black">{politician.chamber}</span>
                        </p>
                        <p className="text-sm text-gray-600 mb-1">
                            政党: <span className="font-medium text-black">{politician.party || '---'}</span>
                        </p>
                        <p className="text-sm text-gray-600">
                            選挙区: <span className="font-medium text-black">{politician.district || '---'}</span>
                        </p>
                    </div>
                </div>
            </div>
        </Link>
    );
};

export default PoliticianCard;
