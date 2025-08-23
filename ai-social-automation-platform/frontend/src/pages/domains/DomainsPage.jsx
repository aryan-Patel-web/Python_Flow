import React from 'react';
import Layout from '../../components/Layout/Layout';

const Domains = () => {
  return (
    <Layout>
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">Content Domains</h1>
        <p className="text-gray-600 mt-2">Select your content domains and niches here...</p>
        
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg">Memes & Entertainment</h3>
            <p className="text-gray-600 text-sm">Funny content and viral memes</p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg">Tech News</h3>
            <p className="text-gray-600 text-sm">Latest technology updates</p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg">Business & Finance</h3>
            <p className="text-gray-600 text-sm">Business tips and financial advice</p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg">Lifestyle</h3>
            <p className="text-gray-600 text-sm">Health, wellness, and lifestyle content</p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg">Coding Tips</h3>
            <p className="text-gray-600 text-sm">Programming tutorials and tips</p>
          </div>
          
          <div className="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <h3 className="font-semibold text-lg">Travel</h3>
            <p className="text-gray-600 text-sm">Travel guides and destinations</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Domains;