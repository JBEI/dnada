<template>
  <div>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">PCR Runs</div>
      </v-card-title>
      <v-card-text>
        <div v-if="runsAreMounted">
          <v-data-table :headers="pcrRunHeaders" :items="currentPCRRuns">
            <template v-slot:item.id="{ item }">
              <v-icon class="mr-2" @click="handlePCRRunEdit(item)"
                >mdi-pencil</v-icon
              >
              <v-icon class="mr-2" @click="handlePCRRunDelete(item)"
                >mdi-delete</v-icon
              >
            </template>
          </v-data-table>
        </div>
      </v-card-text>
    </v-card>
    <!-- Dialogs  -->
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import { readActiveWorkflow, readUserRuns } from '@/store/main/getters';
import { dispatchGetRuns } from '@/store/main/actions';

@Component
export default class Tab4 extends Vue {
  public runsAreMounted: boolean = false;
  public pcrRunHeaders = [
    {
      text: 'Date',
      sortable: true,
      value: 'date',
      align: 'left',
    },
    {
      text: 'Actions',
      sortable: false,
      value: 'id',
      align: 'left',
    },
  ];

  public async mounted() {
    // await dispatchGetRuns(this.$store);
    this.runsAreMounted = true;
  }

  get activeWorkflow() {
    return readActiveWorkflow(this.$store)(
      +this.$router.currentRoute.params.id
    );
  }

  get currentPCRRuns() {
    return readUserRuns(this.$store).filter((runs) => runs.run_type === 'pcr');
  }
}
</script>
