<template>
  <v-app>
    <v-main>
      <Header/>
      <router-view />
      <Footer></Footer>
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
  //
import Header from "@/components/Header.vue";
</script>
