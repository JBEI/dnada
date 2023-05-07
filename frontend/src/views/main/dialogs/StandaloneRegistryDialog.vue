<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Create Registry Submission Instructions</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".zip"
            label="Upload a J5 Results Zip File"
            placeholder="J5 Zip File"
            v-model="j5File"
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
export default class StandaloneRegistryDialog extends Vue {
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
  public j5File: File | any = null;

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.j5File = null;
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
      console.log('Form is submitted');
      // const formData = new FormData();
      // formData.append('upload_file', this.j5File, this.j5File.name);
      // const response = await dispatchStandaloneParseJ5(this.$store, formData);
      // if (response === undefined) {
      //   throw new Error('One of the params must be provided.');
      // }
      // if (response.data === undefined) {
      //   throw new Error('One of the params must be provided.');
      // }
      // if (response.data === "Error") {
      //   return;
      // }
      // const data: any = response.data;
      // this.resultFile = JSON.stringify(data, null, 2);
      // this.resultFileName = `${stripExtension(this.j5File.name)}-parsed.json`;
      // forceFileDownload(this.resultFile, this.resultFileName);
      // this.resultIsReady = true;
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
