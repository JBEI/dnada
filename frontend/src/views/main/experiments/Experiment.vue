<template>
  <v-container fluid>
    <v-app-bar prominent>
      <v-toolbar-title primary-title>
        <div
          v-if="experimentIsMounted"
          class="headline primary--text text-truncate"
        >
          {{ currentExperiment.name }}
        </div>
        <div
          v-if="experimentIsMounted"
          class="subtitle-2 font-weight-light text-wrap"
        >
          {{ currentExperiment.description }}
        </div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="editExperimentDialog = true">
        <v-icon>mdi-pencil</v-icon>
      </v-btn>
      <v-btn icon @click="handleExperimentDelete">
        <v-icon>mdi-delete</v-icon>
      </v-btn>
      <template v-slot:extension>
        <v-tabs v-model="tab" align-with-title grow show-arrows icons-and-text>
          <v-tab href="#tab-1">
            Step 1: Input Designs
            <v-icon>mdi-animation</v-icon>
          </v-tab>
          <v-tab href="#tab-2">
            Step 2: Run
            <v-icon>mdi-play-circle</v-icon>
          </v-tab>
          <v-tab href="#tab-3">
            Step 3: Workflow
            <v-icon>mdi-sitemap</v-icon>
          </v-tab>
        </v-tabs>
      </template>
    </v-app-bar>
    <v-tabs-items v-model="tab">
      <v-tab-item value="tab-1">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Designs</div>
            <v-spacer></v-spacer>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn
                  v-on="on"
                  @click="uploadDesignDialog = true"
                  color="primary"
                  rounded
                  >Upload</v-btn
                >
              </template>
              <span>Upload raw J5 zip file</span>
            </v-tooltip>
          </v-card-title>
          <v-card-text>
            <div v-if="designIsMounted">
              <v-data-table
                :headers="designHeaders"
                :items="currentDesigns"
                hide-default-footer
                disable-pagination
              >
                <template v-slot:item.id="{ item }">
                  <v-icon class="mr-2" @click="handleDesignEdit(item)"
                    >mdi-pencil</v-icon
                  >
                  <v-icon class="mr-2" @click="handleDesignDelete(item)"
                    >mdi-delete</v-icon
                  >
                </template>
              </v-data-table>
            </div>
          </v-card-text>
        </v-card>
      </v-tab-item>
      <v-dialog v-model="editExperimentDialog" max-width="500px">
        <v-card>
          <v-card-title>
            <span class="headline">Edit Experiment</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="editedExperiment.name"
                    label="Experiment name"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="editedExperiment.description"
                    label="Experiment Description"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancelEditExperiment">Cancel</v-btn>
            <v-btn @click="saveEditExperiment">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-dialog v-model="uploadDesignDialog" max-width="600px">
        <v-card>
          <v-card-title>
            <span class="headline">Upload Design</span>
          </v-card-title>
          <v-card-text>
            <v-form v-model="validDesign" ref="form" lazy-validation>
              <v-text-field
                label="Design Name"
                v-model="newDesign.name"
                required
              ></v-text-field>
              <v-text-field
                label="Design Description"
                v-model="newDesign.description"
                required
              ></v-text-field>
              <v-file-input
                show-size
                accept=".zip"
                label="J5 Zip File"
                v-model="newDesignFile"
              ></v-file-input>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancelDesign">Cancel</v-btn>
            <v-btn @click="resetDesign">Reset</v-btn>
            <v-btn @click="submitDesign" :disabled="!validDesign">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-dialog v-model="editDesignDialog" max-width="500px">
        <v-card>
          <v-card-title>
            <span class="headline">Edit Design</span>
          </v-card-title>
          <v-card-text>
            <v-container>
              <v-row>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="editedDesign.name"
                    label="Design name"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="6" md="4">
                  <v-text-field
                    v-model="editedDesign.description"
                    label="Design Description"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-container>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancelEditDesign">Cancel</v-btn>
            <v-btn @click="saveEditDesign">Save</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-tab-item value="tab-2">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">
              Execute Downstream Automation
            </div>
          </v-card-title>
          <v-card-text>
            <div>
              Click this button to create automation instructions for uploaded
              designs
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn
                  v-on="on"
                  @click="executeProjectAutomation"
                  color="primary"
                  rounded
                  >Execute</v-btn
                >
              </template>
              <span>Run downstream automation</span>
            </v-tooltip>
          </v-card-actions>
        </v-card>
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline">Workflows</div>
          </v-card-title>
          <v-card-text>
            <div>
              Results of downstream automation runs will be displayed here
            </div>
            <div v-if="resultsAreMounted">
              <v-data-table
                :headers="resultHeaders"
                :items="currentResults"
                hide-default-footer
                disable-pagination
              >
                <template v-slot:item.id="{ item }">
                  <v-icon class="mr-2" @click="handleResultDownload(item)"
                    >mdi-download</v-icon
                  >
                  <v-icon class="mr-2" @click="handleResultView(item)"
                    >mdi-sitemap</v-icon
                  >
                </template>
              </v-data-table>
            </div>
          </v-card-text>
        </v-card>
      </v-tab-item>
      <v-tab-item value="tab-3">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Workflow</div>
          </v-card-title>
          <v-card-text>
            <div v-if="JSON.stringify(activeWorkflow) === '{}'">
              Please activate an automation result to view a workflow
            </div>
            <div v-else>
              <v-subheader
                >Viewing workflow for automation result from
                {{ activeWorkflow.created_time }} (workflow_id =
                {{ activeWorkflow.id }})</v-subheader
              >
              <v-card>
                <v-card-title primary-title>
                  <div class="headline primary--text">PCR Subworkflow</div>
                </v-card-title>
                <v-card-text>
                  <v-data-table
                    :headers="pcrInstructionHeaders"
                    :items="currentInstructions"
                    hide-default-footer
                    disable-pagination
                  >
                    <template v-slot:item.category="{ item }">
                      <v-icon
                        class="mr-2"
                        @click="handleInstructionDownload(item)"
                        >mdi-download</v-icon
                      >
                    </template>
                    <template v-slot:item.owner_id="{ item }">
                      <v-icon class="mr-2" @click="handleReportResults(item)"
                        >mdi-upload</v-icon
                      >
                    </template>
                    <template v-slot:item.workflow_id="{ item }">
                      <v-icon class="mr-2" @click="handleViewPCRRun(item)"
                        >mdi-file-download</v-icon
                      >
                    </template>
                  </v-data-table>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        v-on="on"
                        @click="executeConsolidatePCRs"
                        color="primary"
                        rounded
                        >Consolidate</v-btn
                      >
                    </template>
                    <span>Consolidate successful PCR rxns</span>
                  </v-tooltip>
                </v-card-actions>
              </v-card>
              <v-card>
                <v-card-title primary-title>
                  <div class="headline primary--text">Assembly Subworkflow</div>
                </v-card-title>
                <v-card-text>
                  <v-btn @click="downloadPossibleAssembly"
                    >Download Possible Assembly Instructions</v-btn
                  >
                  <v-btn @click="reportAssemblyDialog = true"
                    >Report Assembly Results</v-btn
                  >
                  <v-btn @click="reportSequencingDialog = true"
                    >Report Sequencing Results</v-btn
                  >
                  <!-- <a>Pops up dialog, with either equimolar or equivolume</a> -->
                  <!-- <v-btn>Upload Transformation Result (Qpix picking)</v-btn>
                  <v-btn>Download NGS submission instructions</v-btn>
                  <v-btn>Upload sequencing results</v-btn>
                  <v-btn>Download Cherry-picking instructions</v-btn>-->
                </v-card-text>
                <v-card-actions></v-card-actions>
              </v-card>
            </div>
          </v-card-text>
        </v-card>
      </v-tab-item>
    </v-tabs-items>

    <!-- Dialogs -->
    <v-dialog v-model="reportAssemblyDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline">Report Assembly Results</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="validReportAssemblyForm" ref="form" lazy-validation>
            <v-checkbox
              v-model="reportAssemblySettings.manual"
              label="Uploading manually curated results or QPix data"
            ></v-checkbox>
            <div v-if="reportAssemblySettings.manual">
              <v-file-input
                multiple
                show-size
                accept=".csv"
                label="Upload Manually Curated Results"
                placeholder="construct_worksheet.csv"
                v-model="assembly_results"
                required
              >
                <template v-slot:selection="{ text }">
                  <v-chip label small color="primary">{{ text }}</v-chip>
                </template>
              </v-file-input>
              <v-list
                dense
                rounded
                outlined
                subheader
                v-if="zagPeakFiles.length > 1"
              >
                <v-subheader>
                  Drag the uploaded peak tables below so that they match their
                  correct plate
                </v-subheader>
                <v-list-item-group v-model="assembly_results">
                  <draggable
                    v-model="assembly_results"
                    @start="drag = true"
                    @end="drag = false"
                  >
                    <v-list-item
                      v-for="element in assembly_results"
                      :key="element.name"
                      class="drag-list-group-item"
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-drag</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title
                          >Plate #{{ assembly_results.indexOf(element) + 1 }}:
                          {{ element.name }}</v-list-item-title
                        >
                      </v-list-item-content>
                    </v-list-item>
                  </draggable>
                </v-list-item-group>
              </v-list>
            </div>
            <div v-else>
              <span>Coming soon</span>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelReportAssembly">Cancel</v-btn>
          <v-btn @click="resetReportAssembly">Reset</v-btn>
          <v-btn
            @click="submitReportAssembly"
            :disabled="!validReportAssemblyForm"
            color="primary"
            >Submit</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="reportSequencingDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline">Report Sequencing Results</span>
        </v-card-title>
        <v-card-text>
          <v-form
            v-model="validReportSequencingForm"
            ref="form"
            lazy-validation
          >
            <v-checkbox
              v-model="reportSequencingSettings.manual"
              label="Uploading manually curated results or TBD"
            ></v-checkbox>
            <div v-if="reportSequencingSettings.manual">
              <v-file-input
                show-size
                accept=".csv"
                label="Upload Manually Curated Results"
                placeholder="construct_worksheet.csv"
                v-model="sequencing_result"
                required
              ></v-file-input>
            </div>
            <div v-else>
              <span>Coming soon</span>
            </div>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelReportSequencing">Cancel</v-btn>
          <v-btn @click="resetReportSequencing">Reset</v-btn>
          <v-btn
            @click="submitReportSequencing"
            :disabled="!validReportSequencingForm"
            color="primary"
            >Submit</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="analyzePCRDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline">Analyze ZAG Data</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="validAnalyzeZAGForm" ref="form" lazy-validation>
            <v-checkbox
              v-model="zagAnalysisSettings.isRawZagData"
              label="Uploading raw ZAG data or manual results"
            ></v-checkbox>
            <div v-if="zagAnalysisSettings.isRawZagData">
              <v-file-input
                multiple
                show-size
                accept=".csv"
                label="Upload ZAG Peak Table(s) calculated by ProSize software"
                placeholder="ZAG Peak Table(s)"
                v-model="zagPeakFiles"
                required
              >
                <template v-slot:selection="{ text }">
                  <v-chip label small color="primary">{{ text }}</v-chip>
                </template>
              </v-file-input>
              <v-list
                dense
                rounded
                outlined
                subheader
                v-if="zagPeakFiles.length > 1"
              >
                <v-subheader>
                  Drag the uploaded peak tables below so that they match their
                  correct plate
                </v-subheader>
                <v-list-item-group v-model="zagPeakFiles">
                  <draggable
                    v-model="zagPeakFiles"
                    @start="drag = true"
                    @end="drag = false"
                  >
                    <v-list-item
                      v-for="element in zagPeakFiles"
                      :key="element.name"
                      class="drag-list-group-item"
                    >
                      <v-list-item-icon>
                        <v-icon>mdi-drag</v-icon>
                      </v-list-item-icon>
                      <v-list-item-content>
                        <v-list-item-title
                          >Worksheet #{{ zagPeakFiles.indexOf(element) + 1 }}:
                          {{ element.name }}</v-list-item-title
                        >
                      </v-list-item-content>
                    </v-list-item>
                  </draggable>
                </v-list-item-group>
              </v-list>
              <v-text-field
                v-model="zagAnalysisSettings.tolerance"
                name="tolerance"
                label="Size Tolerance (0 < tol < 1)"
                type="number"
                max="1"
                min="0"
                step="0.1"
              ></v-text-field>
            </div>
            <div v-else>
              <v-file-input
                multiple
                show-size
                accept=".csv"
                label="Upload manually analyzed PCR Results"
                placeholder="pcr_results.csv"
                v-model="zagPeakFiles"
                required
              ></v-file-input>
            </div>
            <v-select
              v-model="zagAnalysisSettings.zagColumnPlate"
              name="zagColumnPlate"
              label="Name of Plate column"
              :items="outputPlateOptions"
            ></v-select>
            <v-select
              v-model="zagAnalysisSettings.zagColumnWell"
              name="zagColumnWell"
              label="Name of Well column"
              :items="outputWellOptions"
            ></v-select>
            <v-select
              v-model="zagAnalysisSettings.polymerase"
              :items="polymeraseOptions"
              label="Polymerase Used"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelAnalyzeZAG">Cancel</v-btn>
          <v-btn @click="resetAnalyzeZAG">Reset</v-btn>
          <v-btn
            @click="submitAnalyzeZAG"
            :disabled="!validAnalyzeZAGForm"
            color="primary"
            >Submit</v-btn
          >
          <v-btn
            @click="downloadAnalyzeZAG"
            :disabled="!activeAnalyzeZAGDownload"
            >Download Result</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import {
  readUserExperiment,
  readUserExperiments,
  readUserDesigns,
  readUserWorkflows,
  readActiveWorkflow,
  readActiveInstructions,
} from '@/store/main/getters';
import {
  dispatchGetExperiments,
  dispatchUpdateExperiment,
  dispatchDeleteExperiment,
  dispatchCheckApiError,
  dispatchGetDesigns,
  dispatchCreateDesign,
  dispatchUpdateDesign,
  dispatchExecuteAutomation,
  dispatchGetWorkflows,
  dispatchGetResultZip,
  dispatchGetPCRAnalysis,
  dispatchAnalyzePCRs,
  dispatchGetPCRInstructions,
  dispatchConsolidatePCRTrials,
  dispatchCreateRedoPCRWorkflow,
  dispatchGetPCRInstructionRuns,
  dispatchGetPossibleAssembly,
  dispatchReportAssemblyResults,
  dispatchReportSequencingResults,
} from '@/store/main/actions';
import {
  IUserExperiment,
  IUserExperimentUpdate,
  IUserDesignCreate,
  IUserDesignUpdate,
  IUserDesign,
  IUserExperimentCreate,
  AutomateSettings,
  IUserWorkflow,
  IUserInstruction,
  IUserRun,
} from '@/interfaces';
import {
  commitSetActiveWorkflow,
  commitAddNotification,
} from '@/store/main/mutations';
import { api } from '@/api';
import { dispatchDeleteDesign } from '@/store/main/actions';
import { forceFileDownload } from '@/utils';
import draggable from 'vuedraggable';

@Component({
  components: {
    draggable,
  },
})
export default class UserExperiment extends Vue {
  get currentExperiment() {
    if (this.currentExperimentObject.owner_id === 0) {
      const tmpObject: any = readUserExperiment(this.$store)(
        +this.$router.currentRoute.params.id
      );
      if (tmpObject === undefined) {
        throw new Error('Cannot find this experiment');
      }
      this.currentExperimentObject = tmpObject;
      this.resetEditExperiment();
    }
    return this.currentExperimentObject;
  }

  get currentDesigns() {
    return readUserDesigns(this.$store).filter(
      (designs) =>
        designs.experiment_id === +this.$router.currentRoute.params.id &&
        !designs.condensed
    );
  }

  get currentResults() {
    return readUserWorkflows(this.$store).filter(
      (results) =>
        results.experiment_id === +this.$router.currentRoute.params.id
    );
  }

  get activeWorkflow() {
    return readActiveWorkflow(this.$store)(
      +this.$router.currentRoute.params.id
    );
  }

  set activeWorkflow(value: IUserWorkflow) {
    commitSetActiveWorkflow(this.$store, value);
  }

  get currentInstructions() {
    return readActiveInstructions(this.$store);
  }

  public workflowStatus = {
    step1: false,
    step2: false,
    step3: false,
    step4: false,
    step5: false,
    step6: false,
    step7: false,
    step8: false,
    step9: false,
    step10: false,
    step11: false,
    step12: false,
    step13: false,
    step14: false,
    step15: false,
    step16: false,
    step17: false,
    step18: false,
    step19: false,
  };
  public showPassword: boolean = false;

  public currentExperimentObject: IUserExperiment = {
    name: '',
    description: '',
    id: 0,
    owner_id: 0,
  };
  public experimentIsMounted: boolean = false;
  public designIsMounted: boolean = false;
  public resultsAreMounted: boolean = false;
  public tab: string = 'tab-1';
  public uploadDesignDialog: boolean = false;
  public validDesign: boolean = false;
  public newDesignFile: File | any = null;
  public newDesign = {
    name: '',
    description: '',
    zip_file_name: '',
    condensed: false,
  };
  public workflowStep: number = 1;

  public designHeaders = [
    {
      text: 'Name',
      sortable: true,
      value: 'name',
      align: 'left',
    },
    {
      text: 'Description',
      sortable: true,
      value: 'description',
      align: 'left',
    },
    {
      text: 'Zip File',
      sortable: true,
      value: 'zip_file_name',
      align: 'left',
    },
    {
      text: 'Actions',
      sortable: false,
      value: 'id',
      align: 'left',
    },
  ];

  public resultHeaders = [
    {
      text: 'Created At',
      sortable: true,
      value: 'created_time',
      align: 'left',
    },
    {
      text: 'Actions',
      sortable: true,
      value: 'id',
      align: 'left',
    },
  ];

  public editedExperiment: IUserExperiment = {
    name: '',
    description: '',
    id: 0,
    owner_id: 0,
  };
  public editExperimentDialog: boolean = false;

  public editedDesign: IUserDesign = {
    name: '',
    description: '',
    zip_file_name: '',
    condensed: false,
    id: 1,
    owner_id: 1,
    experiment_id: 1,
  };
  public editDesignDialog: boolean = false;

  public async mounted() {
    await dispatchGetExperiments(this.$store);
    this.experimentIsMounted = true;
    await dispatchGetDesigns(this.$store);
    this.designIsMounted = true;
    await dispatchGetWorkflows(this.$store);
    this.resultsAreMounted = true;
  }

  public async resetEditExperiment() {
    this.editedExperiment = {
      name: this.currentExperimentObject.name,
      description: this.currentExperimentObject.description,
      id: +this.$router.currentRoute.params.id,
      owner_id: this.currentExperimentObject.owner_id,
    };
  }

  public async handleExperimentEdit(experiment) {
    this.resetEditExperiment();
    this.editExperimentDialog = true;
  }

  public async cancelEditExperiment() {
    this.editExperimentDialog = false;
    this.resetEditExperiment();
  }

  public async saveEditExperiment() {
    const ExperimentUpdate: IUserExperimentUpdate = {
      name: this.editedExperiment.name,
      description: this.editedExperiment.description,
    };
    await dispatchUpdateExperiment(this.$store, [
      this.editedExperiment.id,
      ExperimentUpdate,
    ]);
    this.currentExperimentObject.owner_id = 0; // force  a refresh
    await dispatchGetExperiments(this.$store);
    Vue.nextTick();
    this.cancelEditExperiment();
  }

  public async handleExperimentDelete() {
    await dispatchDeleteExperiment(
      this.$store,
      +this.$router.currentRoute.params.id
    );
    this.$router.push({ name: 'main' }).catch((err) => {
      throw new Error(`Problem handling something: ${err}.`);
    });
  }

  public async handleDesignEdit(design) {
    this.editedDesign = {
      name: design.name,
      description: design.description,
      zip_file_name: design.zip_file_name,
      condensed: design.condensed,
      id: design.id,
      owner_id: design.owner_id,
      experiment_id: design.experiment_id,
    };
    this.editDesignDialog = true;
  }

  public async resetEditDesign() {
    this.editedDesign = {
      name: '',
      description: '',
      zip_file_name: '',
      condensed: false,
      id: 1,
      owner_id: 1,
      experiment_id: 1,
    };
  }

  public async cancelEditDesign() {
    this.editDesignDialog = false;
    this.resetEditDesign();
  }

  public async saveEditDesign() {
    const designUpdate: IUserDesignUpdate = {
      name: this.editedDesign.name,
      description: this.editedDesign.description,
    };
    await dispatchUpdateDesign(this.$store, [
      this.editedDesign.id,
      designUpdate,
    ]);
    await dispatchGetDesigns(this.$store);
    this.cancelEditDesign();
  }

  public async handleDesignDelete(design) {
    await dispatchDeleteDesign(this.$store, design.id);
    await dispatchGetDesigns(this.$store);
  }

  public resetDesign() {
    this.newDesign.name = '';
    this.newDesign.description = '';
    this.newDesign.zip_file_name = '';
    this.newDesign.condensed = false;
    this.newDesignFile = null;
    this.$validator.reset();
  }

  public cancelDesign() {
    this.uploadDesignDialog = false;
    this.resetDesign();
  }

  public async submitDesign() {
    if (await this.$validator.validateAll()) {
      const designCreate: IUserDesignCreate = this.newDesign;
      designCreate.zip_file_name = this.newDesignFile.name;
      const formData = new FormData();
      formData.append(
        'design_file',
        this.newDesignFile,
        this.newDesignFile.name
      );
      formData.append('name', designCreate.name);
      formData.append('description', designCreate.description);
      formData.append('zip_file_name', designCreate.zip_file_name);
      formData.append('experiment_id', this.$router.currentRoute.params.id);
      const response = await dispatchCreateDesign(this.$store, formData);
      this.cancelDesign();
    }
  }

  public async executeProjectAutomation() {
    const automateSettings: AutomateSettings = {
      experiment_id: +this.$router.currentRoute.params.id,
    };
    const response = await dispatchExecuteAutomation(
      this.$store,
      automateSettings
    );
    await dispatchGetWorkflows(this.$store);
  }

  public async handleResultDownload(result: IUserWorkflow) {
    const response = await dispatchGetResultZip(
      this.$store,
      result.resultzip_id
    );
    if (response === undefined) {
      throw new Error('One of the params must be provided.');
    }
    if (response.data === undefined) {
      throw new Error('One of the params must be provided.');
    }
    const data: any = response.data;
    const resultZipDownload = data;
    const resultZipNameDownload = `${this.currentExperimentObject.name
      .split(' ')
      .join('_')}-instructions.zip`;
    forceFileDownload(resultZipDownload, resultZipNameDownload);
  }

  public async handleResultView(result: IUserWorkflow) {
    this.activeWorkflow = result;
    await dispatchGetPCRInstructions(this.$store, this.activeWorkflow.id);
    this.tab = 'tab-3';
  }

  // Variables for Analyze ZAG Standalone
  public analyzePCRDialog: boolean = false;
  public validAnalyzeZAGForm: boolean = false;
  public zagPeakFiles: File[] = [];
  public zagAnalysisSettings = {
    isRawZagData: true,
    tolerance: '0.50',
    zagColumnPlate: 'OUTPUT_PLATE',
    zagColumnWell: 'OUTPUT_WELL',
    polymerase: 'N/A',
    instructionID: 0,
    trial: 0,
  };
  public activeAnalyzeZAGDownload: boolean = false;
  public zagResultsFile: string = '';
  public zagResultsFileName: string = '';
  public polymeraseOptions = ['Q5', 'Phusion GC', 'Phusion HF', 'GXL', 'N/A'];
  public outputPlateOptions = ['OUTPUT_PLATE', 'REDO_PLATE'];
  public outputWellOptions = ['OUTPUT_WELL', 'REDO_WELL'];

  // Functions for Analyze ZAG Dialog
  public resetAnalyzeZAG() {
    this.zagPeakFiles = [];
    this.activeAnalyzeZAGDownload = false;
    this.zagResultsFile = '';
    this.zagResultsFileName = '';
    this.zagAnalysisSettings = {
      isRawZagData: true,
      tolerance: '0.50',
      zagColumnPlate: 'OUTPUT_PLATE',
      zagColumnWell: 'OUTPUT_WELL',
      polymerase: 'N/A',
      instructionID: 0,
      trial: 0,
    };
    this.$validator.reset();
  }

  public cancelAnalyzeZAG() {
    this.analyzePCRDialog = false;
    this.resetAnalyzeZAG();
  }

  public async submitAnalyzeZAG() {
    if (await this.$validator.validateAll()) {
      const formData = new FormData();
      for (const element of this.zagPeakFiles) {
        formData.append('peak_files', element, element.name);
      }
      formData.append('settings', JSON.stringify(this.zagAnalysisSettings));
      const response = await dispatchAnalyzePCRs(this.$store, formData);
      if (response === undefined) {
        throw new Error('One of the params must be provided.');
      }
      if (response.data === undefined) {
        throw new Error('One of the params must be provided.');
      }
      const run: IUserRun = response.data;
      this.zagResultsFile = run.raw_data;
      this.zagResultsFileName = `zag-analysis-T${this.zagAnalysisSettings.trial}.csv`;
      this.activeAnalyzeZAGDownload = true;
      await dispatchCreateRedoPCRWorkflow(this.$store, run.id);
      await dispatchGetPCRInstructions(this.$store, this.activeWorkflow.id);
    }
  }

  public async downloadAnalyzeZAG() {
    if (this.activeAnalyzeZAGDownload) {
      forceFileDownload(this.zagResultsFile, this.zagResultsFileName);
    }
  }

  // Functions for PCR Module
  public pcrInstructionHeaders = [
    {
      text: 'DB ID',
      sortable: false,
      value: 'id',
      align: 'center',
    },
    {
      text: 'Trial',
      sortable: true,
      value: 'trial',
      align: 'left',
    },
    {
      text: 'Download Instructions',
      sortable: false,
      value: 'category',
      align: 'center',
    },
    {
      text: 'Report Results',
      sortable: false,
      value: 'owner_id',
      align: 'center',
    },
    {
      text: 'View Results',
      sortable: false,
      value: 'workflow_id',
      align: 'center',
    },
  ];

  public async handleInstructionDownload(instruction: IUserInstruction) {
    forceFileDownload(
      instruction.data,
      `${instruction.category}_T${instruction.trial}.csv`
    );
  }

  public async handleReportResults(instruction: IUserInstruction) {
    this.zagAnalysisSettings.instructionID = instruction.id;
    this.zagAnalysisSettings.trial = instruction.trial;
    this.analyzePCRDialog = true;
  }

  public async executeConsolidatePCRs() {
    var platingScheme: string = 'biomek';
    const response = await dispatchConsolidatePCRTrials(this.$store, [
      this.activeWorkflow.id,
      platingScheme,
    ]);
    if (response === undefined) {
      throw new Error('One of the params must be provided.');
    }
    if (response.data === undefined) {
      throw new Error('One of the params must be provided.');
    }
    if (response.data === 'Error') {
      return;
    }
    const instruction: any = response.data;
    forceFileDownload(instruction, 'consolidate_pcr_instructions.zip');
  }

  public async handleViewPCRRun(instruction: IUserInstruction) {
    const response = await dispatchGetPCRInstructionRuns(
      this.$store,
      instruction.id
    );
    if (response === undefined) {
      throw new Error('One of the params must be provided.');
    }
    if (response.data === undefined) {
      throw new Error('One of the params must be provided.');
    }
    const data: IUserRun[] = response.data;
    if (data.length == 0) {
      commitAddNotification(this.$store, {
        content: 'No Results Available',
        color: 'error',
        indefinite: true,
        showProgress: true,
      });
    } else {
      forceFileDownload(
        data[0].raw_data,
        `zag-analysis-T${instruction.trial}.csv`
      );
    }
  }

  public async downloadPossibleAssembly() {
    const response = await dispatchGetPossibleAssembly(
      this.$store,
      this.activeWorkflow.id
    );
    if (response === undefined) {
      throw new Error('One of the params must be provided.');
    }
    if (response.data === undefined) {
      throw new Error('One of the params must be provided.');
    }
    if (response.data === 'Error') {
      return;
    }
    const instruction: any = response.data;
    forceFileDownload(instruction, 'possible_assembly_instructions.zip');
  }

  // Variables for Report Assembly Results
  public reportAssemblyDialog: boolean = false;
  public validReportAssemblyForm: boolean = false;
  public assembly_results: File[] = [];
  public reportAssemblySettings = {
    manual: true,
    workflowID: 0,
  };
  public activeReportAssemblyDownload: boolean = false;

  // Functions for Report Assembly Dialog
  public resetReportAssembly() {
    this.assembly_results = [];
    this.reportAssemblySettings = {
      manual: true,
      workflowID: 0,
    };
    this.$validator.reset();
  }

  public cancelReportAssembly() {
    this.reportAssemblyDialog = false;
    this.resetReportAssembly();
  }

  public async submitReportAssembly() {
    if (await this.$validator.validateAll()) {
      const formData = new FormData();
      for (const element of this.assembly_results) {
        formData.append('assembly_files', element, element.name);
      }
      this.reportAssemblySettings.workflowID = this.activeWorkflow.id;
      for (let [key, value] of Object.entries(this.reportAssemblySettings)) {
        formData.append(key, JSON.stringify(value));
      }
      // formData.append('settings', JSON.stringify(this.reportAssemblySettings));
      const response = await dispatchReportAssemblyResults(
        this.$store,
        formData
      );
      if (response === undefined) {
        throw new Error('One of the params must be provided.');
      }
      if (response.data === undefined) {
        throw new Error('One of the params must be provided.');
      }
      this.reportAssemblyDialog = false;
    }
  }

  // Variables for Report Sequencing Results
  public reportSequencingDialog: boolean = false;
  public validReportSequencingForm: boolean = false;
  public sequencing_result: File | any = null;
  public reportSequencingSettings = {
    manual: true,
    workflowID: 0,
  };

  // Functions for Report Sequencing Dialog
  public resetReportSequencing() {
    this.sequencing_result = null;
    this.reportSequencingSettings = {
      manual: true,
      workflowID: 0,
    };
    this.$validator.reset();
  }

  public cancelReportSequencing() {
    this.reportSequencingDialog = false;
    this.resetReportSequencing();
  }

  public async submitReportSequencing() {
    if (await this.$validator.validateAll()) {
      const formData = new FormData();
      formData.append(
        'sequencing_file',
        this.sequencing_result,
        this.sequencing_result.name
      );
      this.reportSequencingSettings.workflowID = this.activeWorkflow.id;
      for (let [key, value] of Object.entries(this.reportSequencingSettings)) {
        formData.append(key, JSON.stringify(value));
      }
      // formData.append('settings', JSON.stringify(this.reportSequencingSettings));
      const response = await dispatchReportSequencingResults(
        this.$store,
        formData
      );
      if (response === undefined) {
        throw new Error('One of the params must be provided.');
      }
      if (response.data === undefined) {
        throw new Error('One of the params must be provided.');
      }
    }
    this.reportSequencingDialog = false;
  }
}
</script>
