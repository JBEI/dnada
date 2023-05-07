<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Create Equivolume Assembly</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload PCR Results File"
            placeholder="PCR Results File"
            v-model="consolidatedPcrResultsFile"
            required
          ></v-file-input>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Original Assembly Worksheet"
            placeholder="clean_assembly_worksheet.csv"
            v-model="cleanAssemblyFile"
            required
          ></v-file-input>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Original Parts Worksheet"
            placeholder="parts_plate.csv"
            v-model="partsPlateFile"
            required
          ></v-file-input>
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
import { dispatchStandaloneCreateEquivolumeAssembly } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';

@Component
export default class StandaloneCreateEquivolumeAssemblyDialog extends Vue {
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
  public consolidatedPcrResultsFile: File | any = null;
  public cleanAssemblyFile: File | any = null;
  public partsPlateFile: File | any = null;

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.consolidatedPcrResultsFile = null;
    this.cleanAssemblyFile = null;
    this.partsPlateFile = null;
    this.resultIsReady = false;
    this.resultFile = '';
    this.resultFileName = '';
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
        this.consolidatedPcrResultsFile,
        this.consolidatedPcrResultsFile.name
      );
      formData.append(
        'assembly_file',
        this.cleanAssemblyFile,
        this.cleanAssemblyFile.name
      );
      formData.append(
        'parts_file',
        this.partsPlateFile,
        this.partsPlateFile.name
      );
      const response = await dispatchStandaloneCreateEquivolumeAssembly(
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
      this.resultFile = data;
      this.resultFileName = 'equivolume_assembly_instructions.zip';
      forceFileDownload(this.resultFile, this.resultFileName);
      this.resultIsReady = true;
    }
  }

  public async downloadResults() {
    if (this.resultIsReady) {
      forceFileDownload(this.resultFile, this.resultFileName);
    }
  }
}
</script>

<style scoped></style>
