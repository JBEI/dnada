import {
  IUserProfile,
  IUserExperiment,
  IUserDesign,
  IUserWorkflow,
  IUserRun,
  IUserInstruction,
  Banner,
} from '@/interfaces';
import { MainState, AppNotification } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const mutations = {
  setToken(state: MainState, payload: string) {
    state.token = payload;
  },
  setLoggedIn(state: MainState, payload: boolean) {
    state.isLoggedIn = payload;
  },
  setBanner(state: MainState, payload: Banner) {
    state.banner = payload;
  },
  setLogInError(state: MainState, payload: boolean) {
    state.logInError = payload;
  },
  setUserProfile(state: MainState, payload: IUserProfile) {
    state.userProfile = payload;
  },
  setDashboardMiniDrawer(state: MainState, payload: boolean) {
    state.dashboardMiniDrawer = payload;
  },
  setDashboardShowDrawer(state: MainState, payload: boolean) {
    state.dashboardShowDrawer = payload;
  },
  addNotification(state: MainState, payload: AppNotification) {
    state.notifications.push(payload);
  },
  removeNotification(state: MainState, payload: AppNotification) {
    state.notifications = state.notifications.filter(
      (notification) => notification !== payload
    );
  },
  setDashboardShowExperiments(state: MainState, payload: boolean) {
    state.dashboardExperimentsDrawer = payload;
  },
  setUserExperiments(state: MainState, payload: IUserExperiment[]) {
    state.userExperiments = payload;
  },
  setUserExperiment(state: MainState, payload: IUserExperiment) {
    const userExperiments = state.userExperiments.filter(
      (experiment: IUserExperiment) => experiment.id !== payload.id
    );
    userExperiments.push(payload);
    state.userExperiments = userExperiments;
  },
  deleteUserExperiment(state: MainState, experimentID: number) {
    const userExperiments = state.userExperiments.filter(
      (experiment: IUserExperiment) => experiment.id !== experimentID
    );
    state.userExperiments = userExperiments;
  },
  setUserDesigns(state: MainState, payload: IUserDesign[]) {
    state.userDesigns = payload;
  },
  setUserDesign(state: MainState, payload: IUserDesign) {
    const userDesigns = state.userDesigns.filter(
      (design: IUserDesign) => design.id !== payload.id
    );
    userDesigns.push(payload);
    state.userDesigns = userDesigns;
  },
  deleteUserDesign(state: MainState, designID: number) {
    const userDesigns = state.userDesigns.filter(
      (design: IUserDesign) => design.id !== designID
    );
    state.userDesigns = userDesigns;
  },
  setUserWorkflows(state: MainState, payload: IUserWorkflow[]) {
    state.userWorkflows = payload;
  },
  setUserWorkflow(state: MainState, payload: IUserWorkflow) {
    const userWorkflows = state.userWorkflows.filter(
      (workflow: IUserWorkflow) => workflow.id !== payload.id
    );
    userWorkflows.push(payload);
    state.userWorkflows = userWorkflows;
  },
  deleteUserWorkflow(state: MainState, workflowID: number) {
    const userWorkflows = state.userWorkflows.filter(
      (workflow: IUserWorkflow) => workflow.id !== workflowID
    );
    state.userWorkflows = userWorkflows;
  },
  setActiveUserWorkflows(state: MainState, payload: IUserWorkflow[]) {
    state.activeWorkflows = payload;
  },
  setActiveUserWorkflow(state: MainState, payload: IUserWorkflow) {
    const activeWorkflows = state.activeWorkflows.filter(
      (workflow: IUserWorkflow) =>
        workflow.experiment_id !== payload.experiment_id
    );
    activeWorkflows.push(payload);
    state.activeWorkflows = activeWorkflows;
  },
  setUserRuns(state: MainState, payload: IUserRun[]) {
    state.userRuns = payload;
  },
  setUserRun(state: MainState, payload: IUserRun) {
    const userRuns = state.userRuns.filter(
      (workflow: IUserRun) => workflow.id !== payload.id
    );
    userRuns.push(payload);
    state.userRuns = userRuns;
  },
  setActiveUserInstructions(state: MainState, payload: IUserInstruction[]) {
    state.activeInstructions = payload;
  },
  setActiveUserInstruction(state: MainState, payload: IUserInstruction) {
    const activeInstructions = state.activeInstructions.filter(
      (instruction: IUserInstruction) =>
        instruction.workflow_id !== payload.workflow_id
    );
    activeInstructions.push(payload);
    state.activeInstructions = activeInstructions;
  },
};

const { commit } = getStoreAccessors<MainState | any, State>('');

export const commitSetDashboardMiniDrawer = commit(
  mutations.setDashboardMiniDrawer
);
export const commitSetDashboardShowDrawer = commit(
  mutations.setDashboardShowDrawer
);
export const commitSetDashboardShowExperiments = commit(
  mutations.setDashboardShowExperiments
);
export const commitSetLoggedIn = commit(mutations.setLoggedIn);
export const commitSetLogInError = commit(mutations.setLogInError);
export const commitSetToken = commit(mutations.setToken);
export const commitSetUserProfile = commit(mutations.setUserProfile);
export const commitAddNotification = commit(mutations.addNotification);
export const commitRemoveNotification = commit(mutations.removeNotification);
export const commitSetExperiments = commit(mutations.setUserExperiments);
export const commitSetExperiment = commit(mutations.setUserExperiment);
export const commitDeleteExperiment = commit(mutations.deleteUserExperiment);
export const commitSetDesigns = commit(mutations.setUserDesigns);
export const commitSetDesign = commit(mutations.setUserDesign);
export const commitDeleteDesign = commit(mutations.deleteUserDesign);
export const commitSetWorkflows = commit(mutations.setUserWorkflows);
export const commitSetWorkflow = commit(mutations.setUserWorkflow);
export const commitDeleteWorkflow = commit(mutations.deleteUserWorkflow);
export const commitSetActiveWorkflows = commit(
  mutations.setActiveUserWorkflows
);
export const commitSetActiveWorkflow = commit(mutations.setActiveUserWorkflow);
export const commitSetRuns = commit(mutations.setUserRuns);
export const commitSetRun = commit(mutations.setUserRun);
export const commitSetActiveInstructions = commit(
  mutations.setActiveUserInstructions
);
export const commitSetActiveInstruction = commit(
  mutations.setActiveUserInstruction
);
export const commitSetBanner = commit(mutations.setBanner);
