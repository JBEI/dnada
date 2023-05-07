import {
  IUserProfile,
  IUserExperiment,
  IUserDesign,
  IUserWorkflow,
  IUserRun,
  IUserInstruction,
  Banner,
} from '@/interfaces';

export interface AppNotification {
  content: string;
  color?: string;
  showProgress?: boolean;
  indefinite?: boolean;
}

export interface MainState {
  token: string;
  isLoggedIn: boolean | null;
  logInError: boolean;
  userProfile: IUserProfile | null;
  userExperiments: IUserExperiment[];
  userDesigns: IUserDesign[];
  userWorkflows: IUserWorkflow[];
  activeWorkflows: IUserWorkflow[];
  activeInstructions: IUserInstruction[];
  userRuns: IUserRun[];
  dashboardMiniDrawer: boolean;
  dashboardShowDrawer: boolean;
  dashboardExperimentsDrawer: boolean;
  notifications: AppNotification[];
  banner: Banner | null;
}
