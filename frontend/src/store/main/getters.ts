import { MainState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';
import { IUserWorkflow, Banner } from '@/interfaces';

export const getters = {
  hasAdminAccess: (state: MainState) => {
    return (
      state.userProfile &&
      state.userProfile.is_superuser &&
      state.userProfile.is_active
    );
  },
  loginError: (state: MainState) => state.logInError,
  dashboardShowDrawer: (state: MainState) => state.dashboardShowDrawer,
  dashboardMiniDrawer: (state: MainState) => state.dashboardMiniDrawer,
  dashboardExperimentsDrawer: (state: MainState) =>
    state.dashboardExperimentsDrawer,
  userProfile: (state: MainState) => state.userProfile,
  banner: (state: MainState): Banner | null => state.banner,
  token: (state: MainState) => state.token,
  isLoggedIn: (state: MainState) => state.isLoggedIn,
  firstNotification: (state: MainState) =>
    state.notifications.length > 0 && state.notifications[0],
  userExperiments: (state: MainState) => state.userExperiments,
  userExperiment: (state: MainState) => (experimentId: number) => {
    const filteredExperiments = state.userExperiments.filter(
      (experiments) => experiments.id === experimentId
    );
    if (filteredExperiments.length > 0) {
      return { ...filteredExperiments[0] };
    }
  },
  userDesigns: (state: MainState) => state.userDesigns,
  userDesign: (state: MainState) => (designID: number) => {
    const filteredDesigns = state.userDesigns.filter(
      (design) => design.id === designID
    );
    if (filteredDesigns.length > 0) {
      return { ...filteredDesigns[0] };
    }
  },
  userWorkflows: (state: MainState) => state.userWorkflows,
  userWorkflow: (state: MainState) => (workflowID: number) => {
    const filteredWorkflows = state.userWorkflows.filter(
      (workflows) => workflows.id === workflowID
    );
    if (filteredWorkflows.length > 0) {
      return { ...filteredWorkflows[0] };
    }
  },
  activeWorkflows: (state: MainState) => state.activeWorkflows,
  activeWorkflow: (state: MainState) => (experimentID: number) => {
    const filteredWorkflows = state.activeWorkflows.filter(
      (workflows) => workflows.experiment_id === experimentID
    );
    if (filteredWorkflows.length > 0) {
      return { ...filteredWorkflows[0] };
    } else {
      return {} as IUserWorkflow;
    }
  },
  activeInstructions: (state: MainState) => state.activeInstructions,
  activeInstruction: (state: MainState) => (instructionID: number) => {
    const filteredInstructions = state.activeInstructions.filter(
      (instructions) => instructions.id === instructionID
    );
    if (filteredInstructions.length > 0) {
      return { ...filteredInstructions[0] };
    }
  },
  userRuns: (state: MainState) => state.userRuns,
  userRun: (state: MainState) => (experimentID: number) => {
    // const filteredRuns = state.userRuns.filter(
    //     (runs) => runs.experiment_id === experimentID);
    const filteredRuns = state.userRuns;
    if (filteredRuns.length > 0) {
      return { ...filteredRuns[0] };
    }
  },
};

const { read } = getStoreAccessors<MainState, State>('');

export const readDashboardMiniDrawer = read(getters.dashboardMiniDrawer);
export const readDashboardShowDrawer = read(getters.dashboardShowDrawer);
export const readDashboardShowExperiments = read(
  getters.dashboardExperimentsDrawer
);
export const readHasAdminAccess = read(getters.hasAdminAccess);
export const readIsLoggedIn = read(getters.isLoggedIn);
export const readLoginError = read(getters.loginError);
export const readToken = read(getters.token);
export const readUserProfile = read(getters.userProfile);
export const readFirstNotification = read(getters.firstNotification);
export const readUserExperiments = read(getters.userExperiments);
export const readUserExperiment = read(getters.userExperiment);
export const readUserDesigns = read(getters.userDesigns);
export const readUserDesign = read(getters.userDesign);
export const readUserWorkflows = read(getters.userWorkflows);
export const readUserWorkflow = read(getters.userWorkflow);
export const readActiveWorkflows = read(getters.activeWorkflows);
export const readActiveWorkflow = read(getters.activeWorkflow);
export const readUserRuns = read(getters.userRuns);
export const readUserRun = read(getters.userRun);
export const readActiveInstructions = read(getters.activeInstructions);
export const readActiveInstruction = read(getters.activeInstruction);
export const readBanner = read(getters.banner);
