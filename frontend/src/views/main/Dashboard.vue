<template>
  <v-container fluid>
    <v-alert
      type="info"
      color="primary"
      dismissible
      prominent
      v-if="banner_mounted && banner.text !== ''"
      >{{ banner.text }}</v-alert
    >
    <v-card flat class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="text-center display-1 primary--text">
          Welcome {{ greetedUser }}
        </div>
      </v-card-title>
    </v-card>
    <v-card class="ma-3 pa-3" v-model="showExperiments">
      <v-card-title primary-title>
        <div class="headline primary--text">Project Mode</div>
      </v-card-title>
      <v-card-text>
        <div class="headline font-weight-light ma-2">
          To begin, create a new experiment or choose an existing experiment
          from the dropdown
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn to="/main/experiments/create" color="primary"
          >Create Experiment</v-btn
        >
        <v-btn icon @click="switchShowExperiments">
          <v-icon>{{
            showExperiments ? 'mdi-chevron-up' : 'mdi-chevron-down'
          }}</v-icon>
        </v-btn>
      </v-card-actions>
      <v-expand-transition>
        <div v-show="showExperiments">
          <v-divider></v-divider>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            filled
            hide-details
          ></v-text-field>
          <v-data-table
            :headers="headers"
            :items="experiments"
            :search="search"
            @click:row="handleExperimentClick"
          ></v-data-table>
        </div>
      </v-expand-transition>
    </v-card>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Standalone Mode</div>
      </v-card-title>
      <v-hover v-slot:default="{ hover }">
        <v-list shaped two-line subheader>
          <v-divider></v-divider>
          <v-subheader
            >These functions are to run individual actions without storing
            anything in DNAda database</v-subheader
          >
          <v-list-item
            @click="condenseAutomateJ5Dialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title
                >Condense and Automate J5 Result Files</v-list-item-title
              >
              <v-list-item-subtitle
                >J5 Zip File(s) -> Instructions for Build</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-divider></v-divider>
          <v-subheader>Downstream Automation Stuff</v-subheader>
          <v-list-item @click="analyzeZagDialog = true" class="standalone">
            <v-list-item-content>
              <v-list-item-title>Analyze ZAG Data</v-list-item-title>
              <v-list-item-subtitle
                >ZAG Peak Table and Target Sizes -> CSV of correct
                wells</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="createPcrRedoDialog = true" class="standalone">
            <v-list-item-content>
              <v-list-item-title
                >Create PCR Redo Instructions</v-list-item-title
              >
              <v-list-item-subtitle
                >PCR Results File -> Next round worksheet and echo
                instructions</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="consolidatePcrDialog = true" class="standalone">
            <v-list-item-content>
              <v-list-item-title>Consolidate PCR Trials</v-list-item-title>
              <v-list-item-subtitle
                >PCR Results File(s) -> Consolidated PCR Results File and Biomek
                Instructions</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="createEquivolumeAssemblyDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title>Create Equivolume Assembly</v-list-item-title>
              <v-list-item-subtitle
                >Glycerol Worksheet, Plasmid Sequences -> cPCR
                Instructions</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="createEquimolarAssemblyandWaterDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title
                >Create Equimolar Assembly Instructions</v-list-item-title
              >
              <v-list-item-subtitle
                >Part Concentration, Assembly Worksheet, and Assembly Parameters
                -> Assembly Instructions</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="createPlatingInstructionsDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title>Create Plating Instructions</v-list-item-title>
              <v-list-item-subtitle
                >Construct Worksheet -> Plating Worksheet</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="createGlycerolStockWorksheetDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title
                >Create Glycerol Stock Worksheet</v-list-item-title
              >
              <v-list-item-subtitle
                >QPix Results, Plating Worksheet -> Glycerol Stock
                Worksheet</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="createColonyPCRInstructionsDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title
                >Create Colony PCR Instructions</v-list-item-title
              >
              <v-list-item-subtitle
                >Glycerol Worksheet, Assembly Worksheet, Parts Worksheet -> cPCR
                instructions</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item @click="createNGSFormDialog = true" class="standalone">
            <v-list-item-content>
              <v-list-item-title>Create NGS Submission Form</v-list-item-title>
              <v-list-item-subtitle
                >Glycerol Stock Worksheet, Registry Worksheet -> NGS Submission
                Form</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-list-item
            @click="createCherryPickingDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title
                >Create Cherry Picking Instructions</v-list-item-title
              >
              <v-list-item-subtitle
                >Submission Worksheet, NGS Results -> Cherry Picking
                Instructions</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
          <v-divider></v-divider>
          <v-subheader>Miscellaneous Toolbox</v-subheader>
          <v-list-item
            @click="condensePlateReaderDataDialog = true"
            class="standalone"
          >
            <v-list-item-content>
              <v-list-item-title>Condense Plate Reader Data</v-list-item-title>
              <v-list-item-subtitle
                >Wide format -> Tall format</v-list-item-subtitle
              >
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </v-hover>
    </v-card>

    <!-- Dialogs -->

    <standalone-condense-automate-j-5-dialog
      :active="condenseAutomateJ5Dialog"
      v-on:update:active="condenseAutomateJ5Dialog = $event"
    ></standalone-condense-automate-j-5-dialog>
    <standalone-analyze-zag-dialog
      :active="analyzeZagDialog"
      v-on:update:active="analyzeZagDialog = $event"
    ></standalone-analyze-zag-dialog>
    <standalone-create-pcr-redo-dialog
      :active="createPcrRedoDialog"
      v-on:update:active="createPcrRedoDialog = $event"
    ></standalone-create-pcr-redo-dialog>
    <standalone-consolidate-pcr-dialog
      :active="consolidatePcrDialog"
      v-on:update:active="consolidatePcrDialog = $event"
    ></standalone-consolidate-pcr-dialog>
    <standalone-create-equivolume-assembly-dialog
      :active="createEquivolumeAssemblyDialog"
      v-on:update:active="createEquivolumeAssemblyDialog = $event"
    ></standalone-create-equivolume-assembly-dialog>
    <standalone-create-equimolar-assembly-and-water-dialog
      :active="createEquimolarAssemblyandWaterDialog"
      v-on:update:active="createEquimolarAssemblyandWaterDialog = $event"
    ></standalone-create-equimolar-assembly-and-water-dialog>
    <standalone-create-glycerol-stock-worksheet-dialog
      :active="createGlycerolStockWorksheetDialog"
      v-on:update:active="createGlycerolStockWorksheetDialog = $event"
    ></standalone-create-glycerol-stock-worksheet-dialog>
    <standalone-create-plating-instructions-dialog
      :active="createPlatingInstructionsDialog"
      v-on:update:active="createPlatingInstructionsDialog = $event"
    ></standalone-create-plating-instructions-dialog>
    <standalone-create-colony-p-c-r-instructions-dialog
      :active="createColonyPCRInstructionsDialog"
      v-on:update:active="createColonyPCRInstructionsDialog = $event"
    ></standalone-create-colony-p-c-r-instructions-dialog>
    <standalone-create-ngs-form-dialog
      :active="createNGSFormDialog"
      v-on:update:active="createNGSFormDialog = $event"
    ></standalone-create-ngs-form-dialog>
    <standalone-create-cherry-picking-dialog
      :active="createCherryPickingDialog"
      v-on:update:active="createCherryPickingDialog = $event"
    ></standalone-create-cherry-picking-dialog>
    <standalone-condense-plate-reader-data-dialog
      :active="condensePlateReaderDataDialog"
      v-on:update:active="condensePlateReaderDataDialog = $event"
    ></standalone-condense-plate-reader-data-dialog>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import {
  readUserProfile,
  readDashboardShowExperiments,
  readUserExperiments,
  readBanner,
} from '@/store/main/getters';
import { commitSetDashboardShowExperiments } from '@/store/main/mutations';
import {
  dispatchGetExperiments,
  dispatchGetBanner,
} from '@/store/main/actions';

import StandaloneCondenseAutomateJ5Dialog from '@/views/main/dialogs/StandaloneCondenseAutomateJ5Dialog.vue';
import StandaloneAnalyzeZagDialog from '@/views/main/dialogs/StandaloneAnalyzeZagDialog.vue';
import StandaloneCreatePcrRedoDialog from '@/views/main/dialogs/StandaloneCreatePcrRedoDialog.vue';
import StandaloneConsolidatePcrDialog from '@/views/main/dialogs/StandaloneConsolidatePcrDialog.vue';
import StandaloneCreateEquivolumeAssemblyDialog from '@/views/main/dialogs/StandaloneCreateEquivolumeAssemblyDialog.vue';
import StandaloneCreateEquimolarAssemblyAndWaterDialog from '@/views/main/dialogs/StandaloneCreateEquimolarAssemblyAndWaterDialog.vue';
import StandaloneCreateGlycerolStockWorksheetDialog from '@/views/main/dialogs/StandaloneCreateGlycerolStockWorksheetDialog.vue';
import StandaloneCreatePlatingInstructionsDialog from '@/views/main/dialogs/StandaloneCreatePlatingInstructionsDialog.vue';
import StandaloneCreateColonyPCRInstructionsDialog from '@/views/main/dialogs/StandaloneCreateColonyPCRInstructionsDialog.vue';
import StandaloneCreateNGSFormDialog from '@/views/main/dialogs/StandaloneCreateNGSFormDialog.vue';
import StandaloneCreateCherryPickingDialog from '@/views/main/dialogs/StandaloneCreateCherryPickingDialog.vue';
import StandaloneCondensePlateReaderDataDialog from '@/views/main/dialogs/StandaloneCondensePlateReaderDataDialog.vue';

@Component({
  components: {
    StandaloneCondenseAutomateJ5Dialog,
    StandaloneAnalyzeZagDialog,
    StandaloneCreatePcrRedoDialog,
    StandaloneConsolidatePcrDialog,
    StandaloneCreateEquivolumeAssemblyDialog,
    StandaloneCreateEquimolarAssemblyAndWaterDialog,
    StandaloneCreateGlycerolStockWorksheetDialog,
    StandaloneCreatePlatingInstructionsDialog,
    StandaloneCreateColonyPCRInstructionsDialog,
    StandaloneCreateNGSFormDialog,
    StandaloneCreateCherryPickingDialog,
    StandaloneCondensePlateReaderDataDialog,
  },
})
export default class Dashboard extends Vue {
  // Standalone Dialog Variables
  public condenseJ5Dialog: boolean = false;
  public automateJ5Dialog: boolean = false;
  public condenseAutomateJ5Dialog: boolean = false;
  public analyzeZagDialog: boolean = false;
  public createPcrRedoDialog: boolean = false;
  public consolidatePcrDialog: boolean = false;
  public createEquivolumeAssemblyDialog: boolean = false;
  public createEquimolarAssemblyDialog: boolean = false;
  public createEquimolarAssemblyandWaterDialog: boolean = false;
  public createGlycerolStockWorksheetDialog: boolean = false;
  public createPlatingInstructionsDialog: boolean = false;
  public createColonyPCRInstructionsDialog: boolean = false;
  public createNGSFormDialog: boolean = false;
  public createCherryPickingDialog: boolean = false;
  public condensePlateReaderDataDialog: boolean = false;

  // Variables for Experiment dropdown
  public banner_mounted: boolean = false;
  public search: string = '';
  public headers = [
    {
      text: 'Name',
      sortable: true,
      value: 'name',
      align: 'left',
    },
    {
      text: 'Description',
      sortable: true,
      value: 'description',
      align: 'left',
    },
  ];

  public async mounted() {
    await dispatchGetExperiments(this.$store);
    await dispatchGetBanner(this.$store);
    this.banner_mounted = true;
  }

  get greetedUser() {
    const userProfile = readUserProfile(this.$store);
    if (userProfile && userProfile.email) {
      if (userProfile.full_name) {
        return userProfile.full_name;
      } else {
        return userProfile.email;
      }
    }
  }

  get showExperiments() {
    return readDashboardShowExperiments(this.$store);
  }

  set showExperiments(value) {
    commitSetDashboardShowExperiments(this.$store, value);
  }

  get experiments() {
    return readUserExperiments(this.$store);
  }

  get banner() {
    return readBanner(this.$store);
  }

  public switchShowExperiments() {
    commitSetDashboardShowExperiments(
      this.$store,
      !readDashboardShowExperiments(this.$store)
    );
  }

  public handleExperimentClick(experiment) {
    this.$router
      .push({
        name: 'main-experiment',
        params: { id: experiment.id },
      })
      .catch((err) => {
        throw new Error(`Problem handling something: ${err}.`);
      });
  }
}
</script>

<style scoped>
.standalone {
  margin: 5px;
  border-radius: 4px;
}
.standalone:hover {
  background: rgba(0, 217, 255, 0.473);
}
.standalone:active {
  background: rgb(0, 255, 255);
}
.drag-list-group-item {
  cursor: move;
}
.drag-list-group-item i {
  cursor: move;
}
</style>
