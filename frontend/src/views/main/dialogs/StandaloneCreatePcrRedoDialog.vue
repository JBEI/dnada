<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Create PCR Redo Instructions</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload PCR Results File"
            placeholder="PCR Results File"
            v-model="pcrResultsFile"
            required
          ></v-file-input>
          <v-text-field
            v-model="pcrRedoSettings.pcrResultColumn"
            name="pcrResult"
            label="Name of Result column"
            type="text"
          ></v-text-field>
          <v-select
            v-model="pcrRedoSettings.pcrOutputPlateColumn"
            :items="outputPlateOptions"
            label="Name of Output Plate column"
          ></v-select>
          <v-select
            v-model="pcrRedoSettings.pcrOutputWellColumn"
            :items="outputWellOptions"
            label="Name of Output Well column"
          ></v-select>
          <v-text-field
            v-model="pcrRedoSettings.pcrRedoTrial"
            name="pcrTrial"
            label="PCR Trial"
            type="number"
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="cancelStandaloneDialog">Cancel</v-btn>
        <v-btn @click="resetStandaloneDialog">Reset</v-btn>
        <v-btn @click="submitForm" :disabled="!validForm" color="primary"
          >Submit</v-btn
        >
        <v-btn @click="downloadResults" :disabled="!resultIsReady"
          >Download Result</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Vue, Prop } from 'vue-property-decorator';
import { Store } from 'vuex';
import { dispatchStandaloneCreatePCRRedo } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';

@Component
export default class StandaloneCreatePcrRedoDialog extends Vue {
  // Common variables for Dialog
  @Prop(Boolean) active: boolean = false;
  get standaloneDialog() {
    return this.active;
  }
  set standaloneDialog(value) {
    this.$emit('update:active', value);
  }

  public validForm: boolean = false;
  public resultIsReady: boolean = false;

  // Form variables for Dialog
  public pcrResultsFile: File | any = null;
  public pcrRedoSettings = {
    pcrResultColumn: 'GOOD',
    pcrOutputPlateColumn: 'OUTPUT_PLATE',
    pcrOutputWellColumn: 'OUTPUT_WELL',
    pcrRedoTrial: 2,
  };
  public outputPlateOptions = ['OUTPUT_PLATE', 'REDO_PLATE'];
  public outputWellOptions = ['OUTPUT_WELL', 'REDO_WELL'];

  // Result variables for Dialog
  public resultWorksheetFile: string = '';
  public resultWorksheetFileName: string = '';
  public resultEchoFile: string = '';
  public resultEchoFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.pcrResultsFile = null;
    this.pcrRedoSettings = {
      pcrResultColumn: 'GOOD',
      pcrOutputPlateColumn: 'OUTPUT_PLATE',
      pcrOutputWellColumn: 'OUTPUT_WELL',
      pcrRedoTrial: 2,
    };
    this.resultIsReady = false;
    this.resultWorksheetFile = '';
    this.resultWorksheetFileName = '';
    this.resultEchoFile = '';
    this.resultEchoFileName = '';
    this.$validator.reset();
  }

  public cancelStandaloneDialog() {
    this.standaloneDialog = false;
    this.resetStandaloneDialog();
  }

  public async submitForm() {
    if (await this.$validator.validateAll()) {
      const formData = new FormData();
      formData.append(
        'pcr_results_file',
        this.pcrResultsFile,
        this.pcrResultsFile.name
      );
      formData.append('settings', JSON.stringify(this.pcrRedoSettings));
      const response = await dispatchStandaloneCreatePCRRedo(
        this.$store,
        formData
      );
      if (response === undefined) {
        throw new Error('One of the params must be provided.');
      }
      if (response.data === undefined) {
        throw new Error('One of the params must be provided.');
      }
      const data: any = response.data;
      this.resultWorksheetFile = data.worksheet;
      this.resultWorksheetFileName = 'redo_pcr_worksheet.csv';
      forceFileDownload(this.resultWorksheetFile, this.resultWorksheetFileName);
      this.resultEchoFile = data.echo_instructions;
      this.resultEchoFileName = 'redo_pcr_echo_instructions.csv';
      forceFileDownload(this.resultEchoFile, this.resultEchoFileName);
      this.resultIsReady = true;
    }
  }

  public async downloadResults() {
    if (this.resultIsReady) {
      forceFileDownload(this.resultWorksheetFile, this.resultWorksheetFileName);
      forceFileDownload(this.resultEchoFile, this.resultEchoFileName);
    }
  }
}
</script>

<style scoped></style>
