import api from './api';

export const domainsService = {
  async getAvailableDomains() {
    const response = await api.get('/domains/');
    return response.data;
  },

  async selectDomains(domainsData) {
    const response = await api.post('/domains/select', domainsData);
    return response.data;
  },

  async getUserDomains() {
    const response = await api.get('/domains/user');
    return response.data;
  },

  async updateDomainSettings(settingsData) {
    const response = await api.put('/domains/settings', settingsData);
    return response.data;
  },

  async previewDomainContent(domainData) {
    const response = await api.post('/domains/preview', domainData);
    return response.data;
  }
};
