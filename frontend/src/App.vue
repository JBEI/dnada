<template>
  <v-app :style="{ background: $vuetify.theme.themes[theme].background }">
    <v-content v-if="loggedIn === null">
      <v-container fill-height>
        <v-layout align-center justify-center>
          <v-flex>
            <div class="text-center">
              <div class="headline my-5">Loading...</div>
              <v-progress-circular
                size="100"
                indeterminate
                color="primary"
              ></v-progress-circular>
            </div>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
    <router-view v-else />
    <NotificationsManager></NotificationsManager>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import NotificationsManager from '@/components/NotificationsManager.vue';
import { readIsLoggedIn } from './store/main/getters';
import { dispatchCheckLoggedIn } from './store/main/actions';

@Component({
  components: {
    NotificationsManager,
  },
})
export default class App extends Vue {
  get loggedIn() {
    return readIsLoggedIn(this.$store);
  }

  public async created() {
    await dispatchCheckLoggedIn(this.$store);
  }

  get theme() {
    return this.$vuetify.theme.dark ? 'dark' : 'light';
  }
}
</script>
