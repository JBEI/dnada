import { mutations } from './mutations';
import { getters } from './getters';
import { actions } from './actions';
import { MainState } from './state';

const defaultState: MainState = {
  isLoggedIn: null,
  token: '',
  logInError: false,
  userProfile: null,
  userExperiments: [],
  userDesigns: [],
  userWorkflows: [],
  activeWorkflows: [],
  activeInstructions: [],
  userRuns: [],
  dashboardMiniDrawer: false,
  dashboardShowDrawer: false,
  dashboardExperimentsDrawer: false,
  notifications: [],
  banner: null,
};

export const mainModule = {
  state: defaultState,
  mutations,
  actions,
  getters,
};
