import React, { useState } from 'react';

const DomainsPage = () => {
  const [selectedDomains, setSelectedDomains] = useState([]);

  const domains = [
    {
      id: 'memes',
      name: 'Memes & Entertainment',
      description: 'Funny content, viral memes, and entertainment posts',
      icon: '😂',
      color: 'bg-yellow-500'
    },
    {
      id: 'tech',
      name: 'Tech News',
      description: 'Latest technology updates, gadgets, and innovations',
      icon: '💻',
      color: 'bg-blue-500'
    },
    {
      id: 'business',
      name: 'Business & Finance',
      description: 'Business tips, financial advice, and market insights',
      icon: '💼',
      color: 'bg-green-500'
    },
    {
      id: 'lifestyle',
      name: 'Lifestyle',
      description: 'Health, wellness, fitness, and lifestyle content',
      icon: '🌱',
      color: 'bg-pink-500'
    },
    {
      id: 'coding',
      name: 'Coding Tips',
      description: 'Programming tutorials, coding tips, and development guides',
      icon: '⚡',
      color: 'bg-purple-500'
    },
    {
      id: 'travel',
      name: 'Travel',
      description: 'Travel guides, destinations, and adventure stories',
      icon: '✈️',
      color: 'bg-indigo-500'
    },
    {
      id: 'food',
      name: 'Food & Recipes',
      description: 'Delicious recipes, food photography, and cooking tips',
      icon: '🍳',
      color: 'bg-orange-500'
    },
    {
      id: 'motivation',
      name: 'Motivation & Quotes',
      description: 'Inspirational quotes, motivational content, and success stories',
      icon: '🚀',
      color: 'bg-red-500'
    }
  ];

  const toggleDomain = (domainId) => {
    setSelectedDomains(prev => 
      prev.includes(domainId)
        ? prev.filter(id => id !== domainId)
        : [...prev, domainId]
    );
  };

  const isSelected = (domainId) => selectedDomains.includes(domainId);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Domains</h1>
        <p className="text-gray-600">
          Select the content domains you want AI to generate content for. You can choose multiple domains to diversify your content.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">
            Available Domains ({selectedDomains.length} selected)
          </h2>
          {selectedDomains.length > 0 && (
            <button
              onClick={() => setSelectedDomains([])}
              className="text-sm text-red-600 hover:text-red-800"
            >
              Clear All
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {domains.map((domain) => (
            <div
              key={domain.id}
              onClick={() => toggleDomain(domain.id)}
              className={`cursor-pointer rounded-lg border-2 p-4 transition-all duration-200 hover:shadow-md ${
                isSelected(domain.id)
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white ${domain.color}`}>
                  <span className="text-lg">{domain.icon}</span>
                </div>
                {isSelected(domain.id) && (
                  <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✓</span>
                  </div>
                )}
              </div>
              
              <h3 className="font-semibold text-gray-900 mb-2">{domain.name}</h3>
              <p className="text-sm text-gray-600">{domain.description}</p>
            </div>
          ))}
        </div>

        {selectedDomains.length > 0 && (
          <div className="mt-8 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Selected Domains:</h3>
            <div className="flex flex-wrap gap-2">
              {selectedDomains.map((domainId) => {
                const domain = domains.find(d => d.id === domainId);
                return (
                  <span
                    key={domainId}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                  >
                    <span className="mr-1">{domain.icon}</span>
                    {domain.name}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        <div className="mt-6 flex justify-end space-x-3">
          <button
            disabled={selectedDomains.length === 0}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Save Domains ({selectedDomains.length})
          </button>
        </div>
      </div>
    </div>
  );
};

export default DomainsPage;