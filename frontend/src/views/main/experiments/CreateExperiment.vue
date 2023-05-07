<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Create Experiment</div>
      </v-card-title>
      <v-card-text>
        <template>
          <v-form
            v-model="valid"
            ref="form"
            lazy-validation
            @keyup.enter="submit"
          >
            <v-text-field
              label="Name"
              v-model="name"
              required
              @keyup.enter="submit"
            ></v-text-field>
            <v-text-field
              label="Description"
              v-model="description"
              required
              @keyup.enter="submit"
            ></v-text-field>
          </v-form>
        </template>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="cancel">Cancel</v-btn>
        <v-btn @click="reset">Reset</v-btn>
        <v-btn @click="submit" :disabled="!valid">Save</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import {
  IUserExperiment,
  IUserExperimentUpdate,
  IUserExperimentCreate,
} from '@/interfaces';
import {
  dispatchGetExperiments,
  dispatchCreateExperiment,
} from '@/store/main/actions';

@Component
export default class CreateExperiment extends Vue {
  public valid = false;
  public name: string = '';
  public description: string = '';

  public async mounted() {
    await dispatchGetExperiments(this.$store);
    this.reset();
  }

  public reset() {
    this.name = '';
    this.description = '';
    this.$validator.reset();
  }

  public cancel() {
    this.$router.back();
  }

  public async submit() {
    if (await this.$validator.validateAll()) {
      const updatedExperimentIUserExperiment: IUserExperimentCreate = {
        name: '',
        description: '',
      };
      if (this.name) {
        updatedExperimentIUserExperiment.name = this.name;
      }
      if (this.description) {
        updatedExperimentIUserExperiment.description = this.description;
      }
      await dispatchCreateExperiment(
        this.$store,
        updatedExperimentIUserExperiment
      );
      this.$router.push('/main/dashboard').catch((err) => {
        throw new Error(`Problem handling something: ${err}.`);
      });
    }
  }
}
</script>
