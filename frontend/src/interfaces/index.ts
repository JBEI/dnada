export interface IUserProfile {
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  full_name: string;
  id: number;
}

export interface IUserProfileUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface IUserProfileCreate {
  email: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface IUserExperiment {
  name: string;
  description: string;
  id: number;
  owner_id: number;
}

export interface IUserExperimentUpdate {
  name?: string;
  description?: string;
}

export interface IUserExperimentCreate {
  name: string;
  description: string;
}

export interface IUserDesign {
  name: string;
  description: string;
  zip_file_name: string;
  condensed: boolean;
  id: number;
  owner_id: number;
  experiment_id: number;
}

export interface IUserDesignUpdate {
  name?: string;
  description?: string;
  zip_file_name?: string;
  condensed?: boolean;
}

export interface IUserDesignCreate {
  name: string;
  description: string;
  zip_file_name: string;
  condensed: boolean;
}

export interface AutomateSettings {
  experiment_id: number;
}

export interface IUserWorkflow {
  created_time: string;
  id: number;
  owner_id: number;
  experiment_id: number;
  design_id: number;
  resultzip_id: number;
}

export interface IUserWorkflowCreate {
  created_time: string;
}

export interface IUserRun {
  date: string;
  instrument: string;
  raw_data: string;
  run_type: string;
  id: number;
  owner_id: number;
  instruction_id: number;
}

export interface IUserInstruction {
  category: string;
  trial: number;
  data: string;
  id: number;
  owner_id: number;
  workflow_id: number;
}

export interface IUserWorkflowStep {
  name: string;
  number: number;
  title: string;
  status: string;
  id: number;
  owner_id: number;
  workflow_id: number;
}

export interface Banner {
  id: number;
  text: string;
}

export interface BannerUpdate {
  text: string;
}
