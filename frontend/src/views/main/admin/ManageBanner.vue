<template>
  <v-container fluid>
    <v-card>
      <v-card-title primary-title>
        <div class="headline primary--text">
          View and Update Dashboard Banner
        </div>
      </v-card-title>
      <v-card-text>
        <v-form v-model="valid" ref="form" lazy-validation>
          <v-textarea filled label="Banner" v-model="text" required>
          </v-textarea>
        </v-form>
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
import { readBanner } from '@/store/main/getters';
import { dispatchGetBanner, dispatchUpdateBanner } from '@/store/main/actions';
import { BannerUpdate } from '@/interfaces';

@Component
export default class ManageBanner extends Vue {
  public valid: boolean = true;
  public text: string = '';

  public async mounted() {
    await dispatchGetBanner(this.$store);
    this.reset();
  }

  get banner() {
    return readBanner(this.$store);
  }

  public cancel() {
    this.$router.back();
  }

  public reset() {
    this.$validator.reset();
    if (this.banner) {
      this.text = this.banner.text;
    }
  }

  public async submit() {
    if (await this.$validator.validateAll()) {
      this.updateBanner(this.text);
    }
  }

  public async updateBanner(new_banner_text: string) {
    const newBanner: BannerUpdate = { text: new_banner_text };
    await dispatchUpdateBanner(this.$store, newBanner);
  }
}
</script>
