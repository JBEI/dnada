<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline"
          >Create Equimolar Assembly and Water Transfer</span
        >
        <span class="headline">Instructions</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Assembly Worksheet File"
            placeholder="Assembly Worksheet File"
            v-model="AssemblyWorksheetandWaterFile"
            required
          ></v-file-input>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Quant Worksheet File"
            placeholder="Quant Worksheet File"
            v-model="QuantWorksheetandWaterFile"
            required
          ></v-file-input>
          <v-text-field
            v-model="max_fmol"
            name="max_fmol"
            label="Max part concentration per reaction (fmol)"
            type="number"
          ></v-text-field>
          <v-text-field
            v-model="max_vol"
            name="max_vol"
            label="Desired Final Assembly Volume of Parts + Water (uL)"
            type="number"
          ></v-text-field>
          <v-text-field
            v-model="max_part_percentage"
            name="max_part_percentage"
            label="Max Part Percentage in Parts + Water Volume (0 - 1)"
            type="number"
            max="1"
            min="0"
            step="0.1"
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
import { dispatchStandaloneEquimolarAssemblyandWater } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';

@Component
export default class StandaloneCreateEquimolarAssemblyAndWaterDialog extends Vue {
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
  public AssemblyWorksheetandWaterFile: File | any = null;
  public QuantWorksheetandWaterFile: File | any = null;
  public max_fmol: string = '100';
  public max_vol: string = '5';
  public max_part_percentage: string = '1';

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.AssemblyWorksheetandWaterFile = null;
    this.QuantWorksheetandWaterFile = null;
    this.max_fmol = '100';
    this.max_vol = '5';
    this.max_part_percentage = '1';
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
        'assembly_worksheet',
        this.AssemblyWorksheetandWaterFile,
        this.AssemblyWorksheetandWaterFile.name
      );
      formData.append(
        'quant_worksheet',
        this.QuantWorksheetandWaterFile,
        this.QuantWorksheetandWaterFile.name
      );
      formData.append('max_vol', this.max_vol);
      formData.append('max_fmol', this.max_fmol);
      formData.append('max_part_percentage', this.max_part_percentage);
      const response = await dispatchStandaloneEquimolarAssemblyandWater(
        this.$store,
        formData
      );
      if (response === undefined) {
        throw new Error('One of the files must be provided.');
      }
      if (response.data === undefined) {
        throw new Error('One of the files must be provided.');
      }
      const data: any = response.data;
      this.resultFile = data;
      this.resultFileName = 'equimolar_assembly_instructions.zip';
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
