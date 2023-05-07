<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Create NGS Submission Form</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Glycerol Stock Worksheet"
            placeholder="glycerol_stock_worksheet.csv"
            v-model="glycerolStockFile"
            required
          ></v-file-input>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Registry Worksheet"
            placeholder="registry_export.csv"
            v-model="registryFile"
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
import { dispatchStandaloneCreateNGSForm } from '@/store/main/actions';
import { forceFileDownload } from '@/utils';

@Component
export default class StandaloneCreateNGSFormDialog extends Vue {
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
  public glycerolStockFile: File | any = null;
  public registryFile: File | any = null;

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.glycerolStockFile = null;
    this.registryFile = null;
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
        'glycerol_stock_file',
        this.glycerolStockFile,
        this.glycerolStockFile.name
      );
      formData.append(
        'registry_file',
        this.registryFile,
        this.registryFile.name
      );
      const response = await dispatchStandaloneCreateNGSForm(
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
      this.resultFileName = 'ngs_submission_form.zip';
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
