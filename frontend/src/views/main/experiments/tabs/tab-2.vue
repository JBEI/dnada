<template>
  <div>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Create Build Workflow</div>
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
              >Create</v-btn
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
        <div>Available workflows will be displayed here</div>
        <div v-if="resultsAreMounted">
          <v-data-table :headers="resultHeaders" :items="currentResults">
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

    <!-- Dialogs  -->
  </div>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import { Store } from 'vuex';
import { readUserWorkflows, readActiveWorkflow } from '@/store/main/getters';
import {
  dispatchExecuteAutomation,
  dispatchGetWorkflows,
  dispatchGetResultZip,
} from '@/store/main/actions';
import { AutomateSettings, IUserWorkflow, IUserExperiment } from '@/interfaces';
import { commitSetActiveWorkflow } from '@/store/main/mutations';
import { forceFileDownload } from '@/utils';

@Component
export default class Tab2 extends Vue {
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
  @Prop({ required: true }) public currentExperimentObject;

  public resultsAreMounted: boolean = false;
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

  public async mounted() {
    await dispatchGetWorkflows(this.$store);
    this.resultsAreMounted = true;
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
    // this.tab = 'tab-3';
    this.$emit('changeToTab', 'tab-3');
  }
}
</script>
