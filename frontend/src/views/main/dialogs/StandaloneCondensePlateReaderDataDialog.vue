<template>
  <v-dialog v-model="standaloneDialog" max-width="600px">
    <v-card>
      <v-card-title>
        <span class="headline">Condense Plate Reader Data</span>
      </v-card-title>
      <v-card-text>
        <v-form v-model="validForm" ref="form" lazy-validation>
          <v-file-input
            show-size
            accept=".csv,.txt"
            label="Upload a Plate Reader File"
            placeholder="plate_reader.csv or plate_reader.txt"
            v-model="plateReaderFile"
            required
          ></v-file-input>
          <v-file-input
            show-size
            accept=".csv"
            label="Upload a Plate Map File"
            placeholder="plate_map.csv"
            v-model="plateMapFile"
            required
          ></v-file-input>
          <v-menu
            v-model="menu"
            :close-on-content-click="false"
            :nudge-right="40"
            transition="scale-transition"
            offset-y
            min-width="auto"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="startDate"
                label="Select date experiment was started"
                prepend-icon="mdi-calendar"
                readonly
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="startDate"
              no-title
              @input="menu = false"
            ></v-date-picker>
          </v-menu>
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
import { dispatchStandaloneCondensePlateReaderData } from '@/store/main/actions';
import { forceFileDownload, stripExtension } from '@/utils';

@Component
export default class StandaloneCondensePlateReaderDataDialog extends Vue {
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
  public plateReaderFile: File | any = null;
  public plateMapFile: File | any = null;
  public startDate: string = new Date().toISOString().substr(0, 10);
  public menu: boolean = false;

  // Result variables for Dialog
  public resultFile: string = '';
  public resultFileName: string = '';

  // Functions for Dialog
  public resetStandaloneDialog() {
    this.plateReaderFile = null;
    this.plateMapFile = null;
    this.startDate = new Date().toISOString().substr(0, 10);
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
        'plate_reader_file',
        this.plateReaderFile,
        this.plateReaderFile.name
      );
      formData.append(
        'plate_map_file',
        this.plateMapFile,
        this.plateMapFile.name
      );
      formData.append('start_date', this.startDate);
      const response = await dispatchStandaloneCondensePlateReaderData(
        this.$store,
        formData
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
      const data: any = response.data;
      this.resultFile = data;
      this.resultFileName = `${stripExtension(
        this.plateReaderFile.name
      )}-tall.csv`;
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
