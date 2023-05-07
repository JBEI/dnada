import axios, { AxiosResponse } from 'axios';
import { apiUrl } from '@/env';
import {
  IUserProfile,
  IUserProfileUpdate,
  IUserProfileCreate,
  IUserExperiment,
  IUserExperimentCreate,
  IUserExperimentUpdate,
  IUserDesign,
  IUserDesignCreate,
  IUserDesignUpdate,
  AutomateSettings,
  BannerUpdate,
  Banner,
} from './interfaces';

function authHeaders(token: string) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

export const api = {
  async logInGetToken(
    username: string,
    password: string
  ): Promise<AxiosResponse<any>> {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    return axios.post(`${apiUrl}/api/v1/login/access-token`, params);
  },
  async getMe(token: string): Promise<AxiosResponse<any>> {
    return axios.get<IUserProfile>(
      `${apiUrl}/api/v1/users/me`,
      authHeaders(token)
    );
  },
  async updateMe(
    token: string,
    data: IUserProfileUpdate
  ): Promise<AxiosResponse<any>> {
    return axios.put<IUserProfile>(
      `${apiUrl}/api/v1/users/me`,
      data,
      authHeaders(token)
    );
  },
  async getUsers(token: string): Promise<AxiosResponse<any>> {
    return axios.get<IUserProfile[]>(`${apiUrl}/api/v1/users/`, {
      ...authHeaders(token),
      ...{ params: { limit: 2000 } },
    });
  },
  async updateUser(
    token: string,
    userId: number,
    data: IUserProfileUpdate
  ): Promise<AxiosResponse<any>> {
    return axios.put(
      `${apiUrl}/api/v1/users/${userId}`,
      data,
      authHeaders(token)
    );
  },
  async createUser(
    token: string,
    data: IUserProfileCreate
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/users/`, data, authHeaders(token));
  },
  async passwordRecovery(email: string): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/password-recovery/${email}`);
  },
  async resetPassword(
    password: string,
    token: string
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/reset-password`, {
      new_password: password,
      token,
    });
  },
  async uploadFile(token: string, data: FormData): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/uploadfile/`, data);
  },
  async standalone_condenseAutomateJ5(
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/condenseandautomatej5`, data, {
      responseType: 'blob',
    });
  },
  async standalone_analyzeZAG(data: FormData): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/analyzezag`, data);
  },
  async standalone_createPCRRedo(data: FormData): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/createpcrredo`, data);
  },
  async standalone_consolidatePCRTrials(
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/consolidatepcrtrials`, data, {
      responseType: 'blob',
    });
  },
  async standalone_createEquivolumeAssembly(
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/createequivolumeassembly`, data, {
      responseType: 'blob',
    });
  },
  async standalone_createColonyPCRInstructions(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/createcolonypcrinstructions`, data, {
      ...authHeaders(token),
      responseType: 'blob',
    });
  },
  async createExperiment(
    token: string,
    data: IUserExperimentCreate
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/experiments`, data, authHeaders(token));
  },
  async getExperiments(token: string): Promise<AxiosResponse<any>> {
    return axios.get<IUserExperiment[]>(`${apiUrl}/api/v1/experiments`, {
      ...authHeaders(token),
      ...{ params: { limit: 2000 } },
    });
  },
  async getExperiment(
    token: string,
    experimentID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(
      `${apiUrl}/api/v1/experiments/${experimentID}`,
      authHeaders(token)
    );
  },
  async updateExperiment(
    token: string,
    experimentID: number,
    data: IUserExperimentUpdate
  ): Promise<AxiosResponse<any>> {
    return axios.put(
      `${apiUrl}/api/v1/experiments/${experimentID}`,
      data,
      authHeaders(token)
    );
  },
  async deleteExperiment(
    token: string,
    experimentID: number
  ): Promise<AxiosResponse<any>> {
    return axios.delete(
      `${apiUrl}/api/v1/experiments/${experimentID}`,
      authHeaders(token)
    );
  },
  async createDesign(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/designs`, data, authHeaders(token));
  },
  async getDesigns(token: string): Promise<AxiosResponse<any>> {
    return axios.get(`${apiUrl}/api/v1/designs`, authHeaders(token));
  },
  async getDesign(
    token: string,
    designID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(
      `${apiUrl}/api/v1/designs/${designID}`,
      authHeaders(token)
    );
  },
  async updateDesign(
    token: string,
    designID: number,
    data: IUserDesignUpdate
  ): Promise<AxiosResponse<any>> {
    return axios.put(
      `${apiUrl}/api/v1/designs/${designID}`,
      data,
      authHeaders(token)
    );
  },
  async deleteDesign(
    token: string,
    designID: number
  ): Promise<AxiosResponse<any>> {
    return axios.delete(
      `${apiUrl}/api/v1/designs/${designID}`,
      authHeaders(token)
    );
  },
  async executeAutomation(
    token: string,
    data: AutomateSettings
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/workflows`, data, authHeaders(token));
  },
  async getWorkflows(token: string): Promise<AxiosResponse<any>> {
    return axios.get(`${apiUrl}/api/v1/workflows`, {
      ...authHeaders(token),
      ...{ params: { limit: 2000 } },
    });
  },
  async getWorkflow(
    token: string,
    workflowID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(
      `${apiUrl}/api/v1/workflows/${workflowID}`,
      authHeaders(token)
    );
  },
  async getResultZip(
    token: string,
    resultZipID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(`${apiUrl}/api/v1/resultzips/${resultZipID}`, {
      ...authHeaders(token),
      responseType: 'blob',
    });
  },
  async analyzePCRs(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/runs/pcr`, data, authHeaders(token));
  },
  async createRedoPCRWorkflow(
    token: string,
    runID: number
  ): Promise<AxiosResponse<any>> {
    return axios.post(
      `${apiUrl}/api/v1/redopcr/${runID}`,
      {},
      authHeaders(token)
    );
  },
  async createConsolidatePCRWorkflow(
    token: string,
    workflowID: number,
    platingScheme: string
  ): Promise<AxiosResponse<any>> {
    return axios.post(
      `${apiUrl}/api/v1/workflow/${workflowID}/consolidatepcrs?plating_scheme=${platingScheme}`,
      {},
      { ...authHeaders(token), responseType: 'blob' }
    );
  },
  async getPossibleAssembly(
    token: string,
    workflowID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(
      `${apiUrl}/api/v1/workflow/${workflowID}/possibleassembly`,
      { ...authHeaders(token), responseType: 'blob' }
    );
  },
  async getRuns(
    token: string,
    workflowID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(`${apiUrl}/api/v1/runs/${workflowID}`, authHeaders(token));
  },
  async getPCRInstructions(
    token: string,
    workflowID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(`${apiUrl}/api/v1/instructions/pcr`, {
      ...authHeaders(token),
      ...{ params: { limit: 2000, workflow_id: workflowID } },
    });
  },
  async getPCRInstructionRuns(
    token: string,
    instructionID: number
  ): Promise<AxiosResponse<any>> {
    return axios.get(
      `${apiUrl}/api/v1/instructions/${instructionID}/run`,
      authHeaders(token)
    );
  },
  async standaloneEquimolarAssemblyandWater(
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(
      `${apiUrl}/api/v1/standalone_equimolar_assembly_and_water_transfer`,
      data,
      { responseType: 'blob' }
    );
  },
  async reportAssemblyResults(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(
      `${apiUrl}/api/v1/runs/assembly`,
      data,
      authHeaders(token)
    );
  },
  async reportSequencingResults(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(
      `${apiUrl}/api/v1/runs/sequencing`,
      data,
      authHeaders(token)
    );
  },
  async standaloneCreateGlycerolStockWorksheet(
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/glycerolstock`, data);
  },
  async standaloneCreatePlatingInstructions(
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/plating`, data);
  },
  async standaloneCreateNGSForm(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/ngsform`, data, {
      ...authHeaders(token),
      responseType: 'blob',
    });
  },
  async standaloneCreateCherryPicking(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(`${apiUrl}/api/v1/cherrypicking`, data, {
      ...authHeaders(token),
      responseType: 'blob',
    });
  },
  async standaloneCondensePlateReaderData(
    token: string,
    data: FormData
  ): Promise<AxiosResponse<any>> {
    return axios.post(
      `${apiUrl}/api/v1/condenseplatereaderdata`,
      data,
      authHeaders(token)
    );
  },
  async getBanner(token: string): Promise<AxiosResponse<Banner>> {
    return axios.get<Banner>(`${apiUrl}/api/v1/banner`, authHeaders(token));
  },
  async updateBanner(
    token: string,
    data: BannerUpdate
  ): Promise<AxiosResponse<Banner>> {
    return axios.put<Banner>(
      `${apiUrl}/api/v1/banner`,
      data,
      authHeaders(token)
    );
  },
};
