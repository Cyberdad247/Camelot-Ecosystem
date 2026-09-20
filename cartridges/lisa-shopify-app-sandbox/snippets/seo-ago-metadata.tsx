import React from 'react';

export const SeoAgoStructuredData: React.FC = () => {
  const schemaGraph = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'Organization',
        '@id': 'https://lisascustomkeychains.com/#organization',
        name: "Lisa's Custom Keychains",
        url: 'https://lisascustomkeychains.com',
        logo: 'https://i.postimg.cc/cvyv100W/Untitled_design_(2).png',
        description: 'Handcrafted, custom hand-woven keychains, charms, and jewelry lovingly made one knot at a time.',
        sameAs: [
          'https://www.instagram.com/lisascustomkeychains',
          'https://www.facebook.com/share/14WQBPgC1Rz/'
        ]
      },
      {
        '@type': 'WebSite',
        '@id': 'https://lisascustomkeychains.com/#website',
        url: 'https://lisascustomkeychains.com',
        name: "Lisa's Custom Keychains",
        publisher: { '@id': 'https://lisascustomkeychains.com/#organization' }
      },
      {
        '@type': 'FAQPage',
        '@id': 'https://lisascustomkeychains.com/#faq',
        mainEntity: [
          {
            '@type': 'Question',
            name: "Can I customize the thread colors and charms on Lisa's keychains?",
            acceptedAnswer: {
              '@type': 'Answer',
              text: "Yes! Every keychain is custom made. You can choose your thread colors, letter beads, and accent charms (sports, hearts, sparkle, butterflies)."
            }
          },
          {
            '@type': 'Question',
            name: "Are Lisa's keychains durable for everyday use?",
            acceptedAnswer: {
              '@type': 'Answer',
              text: "All keychains are hand-woven with high-strength, tight-knot nylon and polyester threads designed to withstand daily key and backpack use."
            }
          },
          {
            '@type': 'Question',
            name: "How fast do custom keychain orders ship?",
            acceptedAnswer: {
              '@type': 'Answer',
              text: "Each custom piece is handcrafted by Lisa and typically ships within 2 to 4 business days."
            }
          }
        ]
      }
    ]
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaGraph) }}
    />
  );
};

export default SeoAgoStructuredData;
