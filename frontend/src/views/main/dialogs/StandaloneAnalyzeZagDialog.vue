<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Analyze ZAG Data</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
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
                      >Plate #{{ zagPeakFiles.indexOf(element) + 1 }}:
                      {{ element.name }}</v-list-item-title
                    >
                  </v-list-item-content>
                </v-list-item>
              </draggable>
            </v-list-item-group>
          </v-list>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload size worksheet"
            placeholder="Size Worksheet"
            v-model="zagSizeFile"
            required
          ></v-file-input>
          <v-text-field
            v-model="zagAnalysisSettings.zagColumnPlate"
            name="zagColumnPlate"
            label="Name of Plate column"
            type="text"
          ></v-text-field>
          <v-text-field
            v-model="zagAnalysisSettings.zagColumnWell"
            name="zagColumnWell"
            label="Name of Well column"
            type="text"
          ></v-text-field>
          <v-text-field
            v-model="zagAnalysisSettings.zagColumnSize"
            name="zagColumnSize"
            label="Name of Expected Size column"
            type="text"
          ></v-text-field>
          <v-text-field
            v-model="zagAnalysisSettings.tolerance"
            name="tolerance"
            label="Size Tolerance (0 < tol < 1)"
            type="number"
            max="1"
            min="0"
            step="0.1"
          ></v-text-field>
          <v-select
            v-model="zagAnalysisSettings.polymerase"
            :items="polymeraseOptions"
            label="Polymerase Used"
          ></v-select>
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
import { dispatchStandaloneAnalyzeZAG } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';
import draggable from 'vuedraggable';

@Component({
  components: {
    draggable,
  },
})
export default class StandaloneAnalyzeZagDialog extends Vue {
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
  public polymeraseOptions = ['Q5', 'Phusion GC', 'Phusion HF', 'GXL', 'N/A'];
  public zagPeakFiles: File[] = [];
  public zagSizeFile: File | any = null;
  public zagAnalysisSettings = {
    tolerance: '0.50',
    zagColumnPlate: 'OUTPUT_PLATE',
    zagColumnWell: 'OUTPUT_WELL',
    zagColumnSize: 'EXPECTED_SIZE',
    polymerase: 'N/A',
  };

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.zagPeakFiles = [];
    this.zagSizeFile = null;
    this.zagAnalysisSettings = {
      tolerance: '0.50',
      zagColumnPlate: 'OUTPUT_PLATE',
      zagColumnWell: 'OUTPUT_WELL',
      zagColumnSize: 'EXPECTED_SIZE',
      polymerase: 'N/A',
    };
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
      for (const element of this.zagPeakFiles) {
        formData.append('peak_files', element, element.name);
      }
      formData.append('size_file', this.zagSizeFile, this.zagSizeFile.name);
      formData.append('settings', JSON.stringify(this.zagAnalysisSettings));
      const response = await dispatchStandaloneAnalyzeZAG(
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
      this.resultFileName = 'zag-analysis.csv';
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
