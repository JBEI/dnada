import { api } from '@/api';
import router from '@/router';
import { getLocalToken, removeLocalToken, saveLocalToken } from '@/utils';
import Axios, { AxiosError, AxiosResponse } from 'axios';
import { getStoreAccessors } from 'typesafe-vuex';
import { ActionContext } from 'vuex';
import { State } from '../state';
import {
  commitAddNotification,
  commitRemoveNotification,
  commitSetLoggedIn,
  commitSetLogInError,
  commitSetToken,
  commitSetUserProfile,
  commitSetExperiments,
  commitSetExperiment,
  commitDeleteExperiment,
  commitSetDesign,
  commitSetDesigns,
  commitDeleteDesign,
  commitSetWorkflow,
  commitSetWorkflows,
  commitDeleteWorkflow,
  commitSetRuns,
  commitSetRun,
  commitSetActiveInstructions,
  commitSetBanner,
} from './mutations';
import { AppNotification, MainState } from './state';
import {
  IUserExperimentCreate,
  IUserDesignUpdate,
  IUserDesign,
  AutomateSettings,
  BannerUpdate,
} from '@/interfaces';

type MainContext = ActionContext<MainState, State>;

export const actions = {
  // async loginUser(user: UserSubmit): Promise<UserResponse|undefined> {
  //     try {
  //         const response = await axios.post('/users/login', {user});
  //         return (response.data as UserResponse)
  //     } catch (err) {
  //         console.error(err);
  //     }
  // }
  async actionLogIn(
    context: MainContext,
    payload: { username: string; password: string }
  ) {
    try {
      const response = await api.logInGetToken(
        payload.username,
        payload.password
      );
      const token = response.data.access_token;
      if (token) {
        saveLocalToken(token);
        commitSetToken(context, token);
        commitSetLoggedIn(context, true);
        commitSetLogInError(context, false);
        await dispatchGetUserProfile(context);
        dispatchRouteLoggedIn(context);
        commitAddNotification(context, {
          content: 'Logged in',
          color: 'success',
        });
      } else {
        await dispatchLogOut(context);
      }
    } catch (err) {
      commitSetLogInError(context, true);
      await dispatchLogOut(context);
    }
  },
  async actionGetUserProfile(context: MainContext) {
    try {
      const response = await api.getMe(context.state.token);
      if (response.data) {
        commitSetUserProfile(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetBanner(context: MainContext) {
    try {
      const response = await api.getBanner(context.state.token);
      if (response.data) {
        commitSetBanner(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateBanner(context: MainContext, payload: BannerUpdate) {
    const loadingNotification = {
      content: 'Updating Banner',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateBanner(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetBanner(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Banner successfully updated',
        color: 'success',
      });
      return response.data;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Updating Banner',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateUserProfile(context: MainContext, payload) {
    try {
      const loadingNotification = {
        content: 'Saving',
        showProgress: true,
        indefinite: true,
      };
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateMe(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetUserProfile(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Profile successfully updated',
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionCheckLoggedIn(context: MainContext) {
    if (!context.state.isLoggedIn) {
      let token = context.state.token;
      if (!token) {
        const localToken = getLocalToken();
        if (localToken) {
          commitSetToken(context, localToken);
          token = localToken;
        }
      }
      if (token) {
        try {
          const response = await api.getMe(token);
          commitSetLoggedIn(context, true);
          commitSetUserProfile(context, response.data);
        } catch (error) {
          await dispatchRemoveLogIn(context);
        }
      } else {
        await dispatchRemoveLogIn(context);
      }
    }
  },
  async actionRemoveLogIn(context: MainContext) {
    removeLocalToken();
    commitSetToken(context, '');
    commitSetLoggedIn(context, false);
  },
  async actionLogOut(context: MainContext) {
    await dispatchRemoveLogIn(context);
    await dispatchRouteLogOut(context);
  },
  async actionUserLogOut(context: MainContext) {
    await dispatchLogOut(context);
    commitAddNotification(context, { content: 'Logged out', color: 'success' });
  },
  actionRouteLogOut(context: MainContext) {
    if (router.currentRoute.path !== '/login') {
      router.push('/login').catch((err) => {
        throw new Error(`Problem handling something: ${err}.`);
      });
    }
  },
  async actionCheckApiError(context: MainContext, payload: AxiosError) {
    if (payload.response!.status === 401) {
      // await dispatchLogOut(context);
      // console.log('Error 401');
    }
  },
  actionRouteLoggedIn(context: MainContext) {
    if (
      router.currentRoute.path === '/login' ||
      router.currentRoute.path === '/'
    ) {
      router.push('/main').catch((err) => {
        // console.log(`Logged in router push being unfinished: ${err}.`);
      });
    }
  },
  async removeNotification(
    context: MainContext,
    payload: { notification: AppNotification; timeout: number }
  ) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        commitRemoveNotification(context, payload.notification);
        resolve(true);
      }, payload.timeout);
    });
  },
  async passwordRecovery(context: MainContext, payload: { username: string }) {
    const loadingNotification = {
      content: 'Sending password recovery email',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.passwordRecovery(payload.username),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Password recovery email sent',
        color: 'success',
      });
      await dispatchLogOut(context);
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Incorrect username',
      });
    }
  },
  async resetPassword(
    context: MainContext,
    payload: { password: string; token: string }
  ) {
    const loadingNotification = {
      content: 'Resetting password',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.resetPassword(payload.password, payload.token),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Password successfully reset',
        color: 'success',
      });
      await dispatchLogOut(context);
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error resetting password',
      });
    }
  },
  async actionCreateExperiment(
    context: MainContext,
    payload: IUserExperimentCreate
  ) {
    const loadingNotification = {
      content: 'Saving',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.createExperiment(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetExperiment(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Experiment successfully created',
        color: 'success',
      });
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetExperiments(context: MainContext) {
    try {
      const response = await api.getExperiments(context.state.token);
      if (response) {
        commitSetExperiments(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetExperiment(context: MainContext, experimentID: number) {
    try {
      const response = await api.getExperiment(
        context.state.token,
        experimentID
      );
      if (response) {
        return response.data;
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateExperiment(context: MainContext, [experimentID, payload]) {
    const loadingNotification = {
      content: 'Saving',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateExperiment(context.state.token, experimentID, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetExperiment(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Experiment successfully updated',
        color: 'success',
      });
      return response.data;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Updating Experiment',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionDeleteExperiment(context: MainContext, experimentID: number) {
    const loadingNotification = {
      content: 'Deleting',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.deleteExperiment(context.state.token, experimentID),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitDeleteExperiment(context, response.data.id);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Experiment successfully deleted',
        color: 'success',
      });
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Deleting Experiment',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCondenseAutomateJ5(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Condensing + Automating J5 Design(s)',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standalone_condenseAutomateJ5(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'J5 Design(s) successfully condensed/automated',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      if (error.response.status === 403) {
        commitAddNotification(context, {
          color: 'error',
          content: 'Invalid J5 Username or Password',
        });
      } else {
        commitAddNotification(context, {
          color: 'error',
          content: 'Error condensing + automating J5 Design(s)',
        });
      }
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneAnalyzeZAG(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Analyzing ZAG data',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standalone_analyzeZAG(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'ZAG data successfully analyzed',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error analyzing ZAG data',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreatePCRRedo(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Creating PCR Redo Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standalone_createPCRRedo(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'PCR Redo Instructions successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error creating PCR Redo Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneConsolidatePCRTrials(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Consolidating PCR Trials',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standalone_consolidatePCRTrials(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'PCR Trials successfully consolidated',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error consolidating PCR Trial files',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreateEquivolumeAssembly(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Creating Equivolume Assembly Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standalone_createEquivolumeAssembly(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Equivolume Assembly Instructions successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Creating Equivolume Assembly Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreateColonyPCRInstructions(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Creating Colony PCR Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standalone_createColonyPCRInstructions(
            context.state.token,
            payload
          ),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Colony PCR Instructions successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Creating Colony PCR Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionCreateDesign(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Creating Design',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.createDesign(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetDesign(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Design Created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Creating Design',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetDesigns(context: MainContext) {
    try {
      const response = await api.getDesigns(context.state.token);
      if (response) {
        commitSetDesigns(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetDesign(context: MainContext, designID: number) {
    try {
      const response = await api.getDesign(context.state.token, designID);
      if (response) {
        return response.data;
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionUpdateDesign(context: MainContext, [designID, payload]) {
    const loadingNotification = {
      content: 'Saving',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.updateDesign(context.state.token, designID, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetDesign(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Design successfully updated',
        color: 'success',
      });
      return response.data;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Updating Design',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionDeleteDesign(context: MainContext, designID: number) {
    const loadingNotification = {
      content: 'Deleting',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.deleteDesign(context.state.token, designID),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitDeleteDesign(context, response.data.id);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Design successfully deleted',
        color: 'success',
      });
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Deleting Design',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionExecuteAutomation(
    context: MainContext,
    payload: AutomateSettings
  ) {
    const loadingNotification = {
      content: 'Running downstream automation',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.executeAutomation(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitSetWorkflow(context, response.data);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Downstream automation successful',
        color: 'success',
      });
      return response;
    } catch (error) {
      if (error.response.status === 403) {
        commitRemoveNotification(context, loadingNotification);
        commitAddNotification(context, {
          color: 'error',
          content: 'Invalid J5 Username or Password',
        });
      } else {
        commitRemoveNotification(context, loadingNotification);
        commitAddNotification(context, {
          color: 'error',
          content: 'Error with dowstream automation',
        });
      }
      await dispatchCheckApiError(context, error);
      return { data: 'Error' };
    }
  },
  async actionGetWorkflows(context: MainContext) {
    try {
      const response = await api.getWorkflows(context.state.token);
      if (response) {
        commitSetWorkflows(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetResultZip(context: MainContext, resultZipID: number) {
    const loadingNotification = {
      content: 'Fetching Result Zip File',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = await api.getResultZip(context.state.token, resultZipID);
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Result Zip Downloading',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error fetching result zip file',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionAnalyzePCRs(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Analyzing ZAG data',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.analyzePCRs(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'ZAG data successfully analyzed',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error analyzing ZAG data',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetPCRAnalysis(context: MainContext, workflowID: number) {
    try {
      console.log(workflowID);
      //const response = await api.getPCRAnalysis(context.state.token, workflowID);
      //return response;
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetRuns(context: MainContext, workflowID: number) {
    try {
      const response = await api.getRuns(context.state.token, workflowID);
      if (response) {
        commitSetRuns(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneEquimolarAssemblyandWater(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Creating Equimolar Assembly and Water Transfer Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standaloneEquimolarAssemblyandWater(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content:
          'Equimolar Assembly and Water Transfer Instructions successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content:
          'Error creating Equimolar Assembly and Water Transfer Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetPCRInstructionRun(
    context: MainContext,
    instructionID: number
  ) {
    try {
      const response = await api.getPCRInstructionRuns(
        context.state.token,
        instructionID
      );
      return response;
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetPCRInstructions(context: MainContext, workflowID: number) {
    try {
      const response = await api.getPCRInstructions(
        context.state.token,
        workflowID
      );
      if (response) {
        commitSetActiveInstructions(context, response.data);
      }
    } catch (error) {
      await dispatchCheckApiError(context, error);
    }
  },
  async actionConsolidatePCRTrials(
    context: MainContext,
    [workflowID, platingScheme]
  ) {
    const loadingNotification = {
      content: 'Consolidating PCR Trials',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.createConsolidatePCRWorkflow(
            context.state.token,
            workflowID,
            platingScheme
          ),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Successfully consolidated PCR Trials',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      if (error.response.status === 422) {
        commitAddNotification(context, {
          color: 'error',
          content: 'Error: please report pcr results',
        });
      } else {
        commitAddNotification(context, {
          color: 'error',
          content: 'Error consolidating PCR Trials',
        });
      }
      await dispatchCheckApiError(context, error);
      return { data: 'Error' };
    }
  },
  async actionCreateRedoPCRWorkflow(context: MainContext, runID: number) {
    const loadingNotification = {
      content: 'Creating Redo PCR Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.createRedoPCRWorkflow(context.state.token, runID),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Successfully created Redo PCR Instructions',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Creating Redo PCR Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionGetPossibleAssembly(context: MainContext, workflowID: number) {
    const loadingNotification = {
      content: 'Fetching Possible Assembly Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = await api.getPossibleAssembly(
        context.state.token,
        workflowID
      );
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Possible Assembly Downloading',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      if (error.response.status === 422) {
        commitAddNotification(context, {
          color: 'error',
          content: 'Error: possible assembly instructions not found',
        });
      } else {
        commitAddNotification(context, {
          color: 'error',
          content: 'Error fetching possible assembly instructions',
        });
      }
      await dispatchCheckApiError(context, error);
      return { data: 'Error' };
    }
  },
  async actionReportAssemblyResults(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Reporting Assembly Results',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.reportAssemblyResults(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Assembly results successfully reported',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error reporting assembly results',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionReportSequencingResults(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Reporting Sequencing Results',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.reportSequencingResults(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Sequencing results successfully reported',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error reporting sequencing results',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreateGlycerolStockWorksheet(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Creating Glycerol Stock Worksheet',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standaloneCreateGlycerolStockWorksheet(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Glycerol Stock Worksheet successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error creating glycerol stock worksheet',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreatePlatingInstructions(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Creating Plating Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standaloneCreatePlatingInstructions(payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Plating Instructions successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error creating Plating Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreateNGSForm(context: MainContext, payload: FormData) {
    const loadingNotification = {
      content: 'Creating NGS Submission Form',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standaloneCreateNGSForm(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'NGS Submission Form successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error creating NGS Submission Form',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCreateCherryPicking(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Creating Cherry Picking Instructions',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standaloneCreateCherryPicking(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Cherry Picking Instructions successfully created',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error creating Cherry Picking Instructions',
      });
      await dispatchCheckApiError(context, error);
    }
  },
  async actionStandaloneCondensePlateReaderData(
    context: MainContext,
    payload: FormData
  ) {
    const loadingNotification = {
      content: 'Condensing Plate Reader Data',
      showProgress: true,
      indefinite: true,
    };
    try {
      commitAddNotification(context, loadingNotification);
      const response = (
        await Promise.all([
          api.standaloneCondensePlateReaderData(context.state.token, payload),
          await new Promise((resolve, reject) =>
            setTimeout(() => resolve(), 500)
          ),
        ])
      )[0];
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        content: 'Plate Reader Data Successfully Condensed',
        color: 'success',
      });
      return response;
    } catch (error) {
      commitRemoveNotification(context, loadingNotification);
      commitAddNotification(context, {
        color: 'error',
        content: 'Error Condensing Plate Reader Data',
      });
      await dispatchCheckApiError(context, error);
    }
  },
};

const { dispatch } = getStoreAccessors<MainState | any, State>('');

export const dispatchCheckApiError = dispatch(actions.actionCheckApiError);
export const dispatchCheckLoggedIn = dispatch(actions.actionCheckLoggedIn);
export const dispatchGetUserProfile = dispatch(actions.actionGetUserProfile);
export const dispatchLogIn = dispatch(actions.actionLogIn);
export const dispatchLogOut = dispatch(actions.actionLogOut);
export const dispatchUserLogOut = dispatch(actions.actionUserLogOut);
export const dispatchRemoveLogIn = dispatch(actions.actionRemoveLogIn);
export const dispatchRouteLoggedIn = dispatch(actions.actionRouteLoggedIn);
export const dispatchRouteLogOut = dispatch(actions.actionRouteLogOut);
export const dispatchUpdateUserProfile = dispatch(
  actions.actionUpdateUserProfile
);
export const dispatchRemoveNotification = dispatch(actions.removeNotification);
export const dispatchPasswordRecovery = dispatch(actions.passwordRecovery);
export const dispatchResetPassword = dispatch(actions.resetPassword);
export const dispatchGetExperiments = dispatch(actions.actionGetExperiments);
export const dispatchCreateExperiment = dispatch(
  actions.actionCreateExperiment
);
export const dispatchDeleteExperiment = dispatch(
  actions.actionDeleteExperiment
);
export const dispatchUpdateExperiment = dispatch(
  actions.actionUpdateExperiment
);
export const dispatchCreateDesign = dispatch(actions.actionCreateDesign);
export const dispatchGetDesigns = dispatch(actions.actionGetDesigns);
export const dispatchGetDesign = dispatch(actions.actionGetDesign);
export const dispatchDeleteDesign = dispatch(actions.actionDeleteDesign);
export const dispatchUpdateDesign = dispatch(actions.actionUpdateDesign);
export const dispatchGetWorkflows = dispatch(actions.actionGetWorkflows);
export const dispatchGetResultZip = dispatch(actions.actionGetResultZip);
export const dispatchExecuteAutomation = dispatch(
  actions.actionExecuteAutomation
);
export const dispatchStandaloneCondenseAutomateJ5 = dispatch(
  actions.actionStandaloneCondenseAutomateJ5
);
export const dispatchStandaloneAnalyzeZAG = dispatch(
  actions.actionStandaloneAnalyzeZAG
);
export const dispatchStandaloneCreatePCRRedo = dispatch(
  actions.actionStandaloneCreatePCRRedo
);
export const dispatchStandaloneConsolidatePCRTrials = dispatch(
  actions.actionStandaloneConsolidatePCRTrials
);
export const dispatchStandaloneCreateEquivolumeAssembly = dispatch(
  actions.actionStandaloneCreateEquivolumeAssembly
);
export const dispatchStandaloneCreateColonyPCRInstructions = dispatch(
  actions.actionStandaloneCreateColonyPCRInstructions
);
export const dispatchAnalyzePCRs = dispatch(actions.actionAnalyzePCRs);
export const dispatchGetPCRAnalysis = dispatch(actions.actionGetPCRAnalysis);
export const dispatchStandaloneEquimolarAssemblyandWater = dispatch(
  actions.actionStandaloneEquimolarAssemblyandWater
);
export const dispatchGetRuns = dispatch(actions.actionGetRuns);
export const dispatchGetPCRInstructions = dispatch(
  actions.actionGetPCRInstructions
);
export const dispatchConsolidatePCRTrials = dispatch(
  actions.actionConsolidatePCRTrials
);
export const dispatchCreateRedoPCRWorkflow = dispatch(
  actions.actionCreateRedoPCRWorkflow
);
export const dispatchGetPCRInstructionRuns = dispatch(
  actions.actionGetPCRInstructionRun
);
export const dispatchGetPossibleAssembly = dispatch(
  actions.actionGetPossibleAssembly
);
export const dispatchReportAssemblyResults = dispatch(
  actions.actionReportAssemblyResults
);
export const dispatchReportSequencingResults = dispatch(
  actions.actionReportSequencingResults
);
export const dispatchGetBanner = dispatch(actions.actionGetBanner);
export const dispatchUpdateBanner = dispatch(actions.actionUpdateBanner);
export const dispatchStandaloneCreateGlycerolStockWorksheet = dispatch(
  actions.actionStandaloneCreateGlycerolStockWorksheet
);
export const dispatchStandaloneCreatePlatingInstructions = dispatch(
  actions.actionStandaloneCreatePlatingInstructions
);
export const dispatchStandaloneCreateNGSForm = dispatch(
  actions.actionStandaloneCreateNGSForm
);
export const dispatchStandaloneCreateCherryPicking = dispatch(
  actions.actionStandaloneCreateCherryPicking
);
export const dispatchStandaloneCondensePlateReaderData = dispatch(
  actions.actionStandaloneCondensePlateReaderData
);
