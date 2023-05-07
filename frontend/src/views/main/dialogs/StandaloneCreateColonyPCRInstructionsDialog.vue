<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Create Colony PCR Instructions</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Glycerol Worksheet File"
            placeholder="glycerol_worksheet.csv"
            v-model="glycerolFile"
            required
          ></v-file-input>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload Plasmid Sequences File"
            placeholder="plasmid_sequences.csv"
            v-model="plasmidSequencesFile"
            required
          ></v-file-input>
          <v-text-field
            v-model="forwardPrimerSequence"
            name="forwardPrimerSequence"
            label="Input Forward Primer Sequence"
            placeholder="Forward Primer Sequence"
            type="text"
            required
          ></v-text-field>
          <v-text-field
            v-model="reversePrimerSequence"
            name="reversePrimerSequence"
            label="Input Reverse Primer Sequence"
            placeholder="Reverse Primer Sequence"
            type="text"
            required
          ></v-text-field>
          <v-text-field
            v-model="reactionVolume"
            name="reactionVolume"
            label="Volume of each cPCR reaction (uL)"
            type="number"
            min="1"
            step="1"
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
import { dispatchStandaloneCreateColonyPCRInstructions } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';

@Component
export default class StandaloneCreateColonyPCRInstructionsDialog extends Vue {
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

  // Form variables for Dialog.
  public glycerolFile: File | any = null;
  public plasmidSequencesFile: File | any = null;
  public forwardPrimerSequence: string = '';
  public reversePrimerSequence: string = '';
  public reactionVolume: string = '10';

  // Result variables for Dialog.
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.glycerolFile = null;
    this.plasmidSequencesFile = null;
    this.forwardPrimerSequence = '';
    this.reversePrimerSequence = '';
    this.reactionVolume = '10';
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
        'glycerol_file',
        this.glycerolFile,
        this.glycerolFile.name
      );
      formData.append(
        'plasmid_sequences_file',
        this.plasmidSequencesFile,
        this.plasmidSequencesFile.name
      );
      formData.append('forward_primer', this.forwardPrimerSequence);
      formData.append('reverse_primer', this.reversePrimerSequence);
      formData.append('reaction_volume', this.reactionVolume);
      const response = await dispatchStandaloneCreateColonyPCRInstructions(
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
      this.resultFileName = 'colony_pcr_instructions.zip';
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
