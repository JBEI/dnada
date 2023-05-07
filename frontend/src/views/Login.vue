<template>
  <v-content>
    <v-container fluid fill-height class="login">
      <v-row align="center" justify="center">
        <v-col cols="auto">
          <div>
            <h1 class="white--text display-1">Welcome to {{ appName }}</h1>
            <h3 class="white--text headline">
              An app to help you build plasmids
            </h3>
          </div>
        </v-col>
        <v-col cols="auto">
          <v-card min-width="300" class="elevation-12">
            <v-toolbar color="primary">
              <v-toolbar-title class="white--text">Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-card-text>
              <v-form @keyup.enter="submit">
                <v-text-field
                  @keyup.enter="submit"
                  v-model="email"
                  prepend-icon="mdi-account"
                  name="username"
                  label="Username"
                  type="text"
                ></v-text-field>
                <v-text-field
                  @keyup.enter="submit"
                  v-model="password"
                  prepend-icon="mdi-lock"
                  name="password"
                  label="Password"
                  id="password"
                  type="password"
                ></v-text-field>
              </v-form>
              <div v-if="loginError">
                <v-alert
                  :value="loginError"
                  transition="fade-transition"
                  type="error"
                  >Incorrect email or password</v-alert
                >
              </div>
              <v-flex class="caption text-right">
                <router-link to="/recover-password"
                  >Forgot your password?</router-link
                >
              </v-flex>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn @click.prevent="submit">Login</v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-content>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { api } from '@/api';
import { appName } from '@/env';
import { readLoginError } from '@/store/main/getters';
import { dispatchLogIn } from '@/store/main/actions';

@Component
export default class Login extends Vue {
  public email: string = '';
  public password: string = '';
  public appName = appName;

  public get loginError() {
    return readLoginError(this.$store);
  }

  public submit() {
    dispatchLogIn(this.$store, {
      username: this.email,
      password: this.password,
    });
  }
}
</script>

<style>
.login {
  background-image: url('~@/assets/wave-background.svg');
  background-size: cover;
}
</style>
