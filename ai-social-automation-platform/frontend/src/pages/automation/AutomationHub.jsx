import React, { useState } from 'react';

const AutomationPage = () => {
  const [automationEnabled, setAutomationEnabled] = useState(false);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Automation Hub</h1>
            <p className="text-gray-600 mt-1">Manage your AI-powered content automation</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-700">Master Automation</span>
            <button
              onClick={() => setAutomationEnabled(!automationEnabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                automationEnabled ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  automationEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold">🤖 Active Rules</h3>
          <p className="text-3xl font-bold text-blue-600">3</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold">📝 Posts Generated</h3>
          <p className="text-3xl font-bold text-green-600">85</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold">⚡ Velocity Score</h3>
          <p className="text-3xl font-bold text-purple-600">87%</p>
        </div>
      </div>
    </div>
  );
};

export default AutomationPage;