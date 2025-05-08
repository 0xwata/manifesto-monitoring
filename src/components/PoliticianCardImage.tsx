"use client"; // Designate as a Client Component

import Image from 'next/image';
import { useState } from 'react';

type PoliticianCardImageProps = {
    src: string;
    alt: string;
    fallbackSrc: string;
};

const PoliticianCardImage: React.FC<PoliticianCardImageProps> = ({ src, alt, fallbackSrc }) => {
    const [imgSrc, setImgSrc] = useState(src);

    return (
        <Image
            src={imgSrc}
            alt={alt}
            width={80}
            height={80}
            className="rounded-full object-cover bg-gray-200"
            unoptimized={true}
            onError={() => setImgSrc(fallbackSrc)}
        />
    );
};

export default PoliticianCardImage;
