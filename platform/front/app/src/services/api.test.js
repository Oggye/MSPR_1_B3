const mockGet = jest.fn();

jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: (...args) => mockGet(...args),
  })),
}));

const {
  getAllTrains,
  getCo2Ranking,
  getCountries,
  getHealth,
  getNightTrainsOnly,
  getOperatorById,
} = require('./api');

beforeEach(() => {
  mockGet.mockClear();
});

test('calls health endpoint', () => {
  getHealth();

  expect(mockGet).toHaveBeenCalledWith('/health');
});

test('passes pagination and filters for all trains', () => {
  getAllTrains(10, 25, { country_code: 'FR', year: 2024 });

  expect(mockGet).toHaveBeenCalledWith('/night-trains', {
    params: { skip: 10, limit: 25, country_code: 'FR', year: 2024 },
  });
});

test('passes filters for night trains only', () => {
  getNightTrainsOnly({ operator_name: 'SNCF' });

  expect(mockGet).toHaveBeenCalledWith('/night-trains/night', {
    params: { operator_name: 'SNCF' },
  });
});

test('uses default limit for CO2 ranking', () => {
  getCo2Ranking();

  expect(mockGet).toHaveBeenCalledWith('/statistics/co2-ranking', {
    params: { limit: 10 },
  });
});

test('calls countries and operator stats endpoints', () => {
  getCountries();
  getOperatorById(3);

  expect(mockGet).toHaveBeenCalledWith('/countries');
  expect(mockGet).toHaveBeenCalledWith('/operators/3/stats');
});
