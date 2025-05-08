"use client"; // Designate as a Client Component

import Image from 'next/image';
import { useState } from 'react';

type PoliticianImageProps = {
    src: string;
    alt: string;
    fallbackSrc: string;
};

const PoliticianImage: React.FC<PoliticianImageProps> = ({ src, alt, fallbackSrc }) => {
    const [imgSrc, setImgSrc] = useState(src);

    return (
        <Image
            src={imgSrc}
            alt={alt}
            fill
            className="rounded-lg object-cover"
            unoptimized={true}
            onError={() => setImgSrc(fallbackSrc)}
        />
    );
};

export default PoliticianImage;
