<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Consolidate PCR Trials</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            multiple
            show-size
            accept=".csv"
            label="Upload PCR Result Worksheet Files"
            placeholder="PCR Result File(s)"
            v-model="pcrTrialFiles"
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
            v-if="pcrTrialFiles.length > 1"
          >
            <v-subheader>
              Drag the uploaded PCR Result Worksheets below so that they match
              their correct trial
            </v-subheader>
            <v-list-item-group v-model="pcrTrialFiles">
              <draggable
                v-model="pcrTrialFiles"
                @start="drag = true"
                @end="drag = false"
              >
                <v-list-item
                  v-for="element in pcrTrialFiles"
                  :key="element.name"
                  class="drag-list-group-item"
                >
                  <v-list-item-icon>
                    <v-icon>mdi-drag</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title
                      >Trial #{{ pcrTrialFiles.indexOf(element) + 1 }}:
                      {{ element.name }}</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
              </draggable>
            </v-list-item-group>
          </v-list>
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
import { dispatchStandaloneConsolidatePCRTrials } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';
import draggable from 'vuedraggable';

@Component({
  components: {
    draggable,
  },
})
export default class StandaloneConsolidatePcrDialog extends Vue {
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
  public pcrTrialFiles: File[] = [];

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.pcrTrialFiles = [];
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
      for (const element of this.pcrTrialFiles) {
        formData.append('pcr_trial_files', element, element.name);
      }
      const response = await dispatchStandaloneConsolidatePCRTrials(
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
      this.resultFileName = 'consolidate_pcr_trial_results.zip';
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
