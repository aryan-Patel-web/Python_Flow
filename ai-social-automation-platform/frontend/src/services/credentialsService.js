import api from './api';

export const credentialsService = {
  async saveCredentials(platformData) {
    const response = await api.post('/credentials/', platformData);
    return response.data;
  },

  async getAllCredentials() {
    const response = await api.get('/credentials/');
    return response.data;
  },

  async getPlatformCredentials(platform) {
    const response = await api.get(`/credentials/${platform}`);
    return response.data;
  },

  async testCredentials(platform) {
    const response = await api.post(`/credentials/${platform}/test`);
    return response.data;
  },

  async updateCredentials(platform, credentialsData) {
    const response = await api.put(`/credentials/${platform}`, credentialsData);
    return response.data;
  },

  async deleteCredentials(platform) {
    const response = await api.delete(`/credentials/${platform}`);
    return response.data;
  }
};
