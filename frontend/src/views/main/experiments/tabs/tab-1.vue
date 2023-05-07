<template>
  <div>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Designs</div>
        <v-spacer></v-spacer>
        <v-tooltip top>
          <template v-slot:activator="{ on }">
            <v-btn
              v-on="on"
              @click="uploadDesignDialog = true"
              color="primary"
              rounded
              >Upload</v-btn
            >
          </template>
          <span>Upload raw J5 zip file</span>
        </v-tooltip>
      </v-card-title>
      <v-card-text>
        <div v-if="designIsMounted">
          <v-data-table :headers="designHeaders" :items="currentDesigns">
            <template v-slot:item.id="{ item }">
              <v-icon class="mr-2" @click="handleDesignEdit(item)"
                >mdi-pencil</v-icon
              >
              <v-icon class="mr-2" @click="handleDesignDelete(item)"
                >mdi-delete</v-icon
              >
            </template>
          </v-data-table>
        </div>
      </v-card-text>
    </v-card>

    <!-- Dialogs  -->

    <v-dialog v-model="uploadDesignDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="headline">Upload Design</span>
        </v-card-title>
        <v-card-text>
          <v-form v-model="validDesign" ref="form" lazy-validation>
            <v-text-field
              label="Design Name"
              v-model="newDesign.name"
              required
            ></v-text-field>
            <v-text-field
              label="Design Description"
              v-model="newDesign.description"
              required
            ></v-text-field>
            <v-file-input
              show-size
              accept=".zip"
              label="J5 Zip File"
              v-model="newDesignFile"
            ></v-file-input>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelDesign">Cancel</v-btn>
          <v-btn @click="resetDesign">Reset</v-btn>
          <v-btn @click="submitDesign" :disabled="!validDesign">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="editDesignDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Edit Design</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="editedDesign.name"
                  label="Design name"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-text-field
                  v-model="editedDesign.description"
                  label="Design Description"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancelEditDesign">Cancel</v-btn>
          <v-btn @click="saveEditDesign">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import { readUserDesigns } from '@/store/main/getters';
import {
  dispatchGetDesigns,
  dispatchCreateDesign,
  dispatchUpdateDesign,
  dispatchDeleteDesign,
} from '@/store/main/actions';
import {
  IUserDesignCreate,
  IUserDesignUpdate,
  IUserDesign,
} from '@/interfaces';

@Component
export default class Tab1 extends Vue {
  public designIsMounted: boolean = false;
  public uploadDesignDialog: boolean = false;
  public validDesign: boolean = false;
  public newDesignFile: File | any = null;
  public newDesign = {
    name: '',
    description: '',
    zip_file_name: '',
    condensed: false,
  };
  public designHeaders = [
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
    {
      text: 'Zip File',
      sortable: true,
      value: 'zip_file_name',
      align: 'left',
    },
    {
      text: 'Actions',
      sortable: false,
      value: 'id',
      align: 'left',
    },
  ];
  public editedDesign: IUserDesign = {
    name: '',
    description: '',
    zip_file_name: '',
    condensed: false,
    id: 1,
    owner_id: 1,
    experiment_id: 1,
  };
  public editDesignDialog: boolean = false;

  public async mounted() {
    await dispatchGetDesigns(this.$store);
    this.designIsMounted = true;
  }

  get currentDesigns() {
    return readUserDesigns(this.$store).filter(
      (designs) =>
        designs.experiment_id === +this.$router.currentRoute.params.id &&
        !designs.condensed
    );
  }

  public async handleDesignEdit(design) {
    this.editedDesign = {
      name: design.name,
      description: design.description,
      zip_file_name: design.zip_file_name,
      condensed: design.condensed,
      id: design.id,
      owner_id: design.owner_id,
      experiment_id: design.experiment_id,
    };
    this.editDesignDialog = true;
  }

  public async resetEditDesign() {
    this.editedDesign = {
      name: '',
      description: '',
      zip_file_name: '',
      condensed: false,
      id: 1,
      owner_id: 1,
      experiment_id: 1,
    };
  }

  public async cancelEditDesign() {
    this.editDesignDialog = false;
    this.resetEditDesign();
  }

  public async saveEditDesign() {
    const designUpdate: IUserDesignUpdate = {
      name: this.editedDesign.name,
      description: this.editedDesign.description,
    };
    await dispatchUpdateDesign(this.$store, [
      this.editedDesign.id,
      designUpdate,
    ]);
    await dispatchGetDesigns(this.$store);
    this.cancelEditDesign();
  }

  public async handleDesignDelete(design) {
    await dispatchDeleteDesign(this.$store, design.id);
    await dispatchGetDesigns(this.$store);
  }

  public resetDesign() {
    this.newDesign.name = '';
    this.newDesign.description = '';
    this.newDesign.zip_file_name = '';
    this.newDesignFile = new File(['foo'], 'foo.txt');
    this.$validator.reset();
  }

  public cancelDesign() {
    this.uploadDesignDialog = false;
    this.resetDesign();
  }

  public async submitDesign() {
    if (await this.$validator.validateAll()) {
      const designCreate: IUserDesignCreate = this.newDesign;
      designCreate.zip_file_name = this.newDesignFile.name;
      const formData = new FormData();
      formData.append(
        'design_file',
        this.newDesignFile,
        this.newDesignFile.name
      );
      formData.append('name', designCreate.name);
      formData.append('description', designCreate.description);
      formData.append('zip_file_name', designCreate.zip_file_name);
      formData.append('experiment_id', this.$router.currentRoute.params.id);
      const response = await dispatchCreateDesign(this.$store, formData);
      this.cancelDesign();
    }
  }
}
</script>
