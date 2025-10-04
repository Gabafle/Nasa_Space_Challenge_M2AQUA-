<script setup>
const icons = [
  'mdi-facebook',
  'mdi-twitter',
  'mdi-linkedin',
  'mdi-instagram',
]
</script>


<template>
  <v-footer class="text-center d-flex flex-column ga-2 py-4" color="#22222">
    <div class="d-flex ga-3">
      <v-btn
        v-for="icon in icons"
        :key="icon"
        :icon="icon"
        density="comfortable"
        variant="text"
        class="btn-footer"
      ></v-btn>
    </div>

    <v-divider class="my-2" thickness="2" width="50"></v-divider>

    <div class="text-caption font-weight-regular opacity-60">
      ©NASA – Exoplanet Data Analysis | Tous droits réservés. Cette application fournit des analyses scientifiques de datasets d’exoplanètes pour la recherche et l’éducation. Les données proviennent de missions NASA et de catalogues publics d’astronomie.
    </div>

    <v-divider></v-divider>

    <div class="date">
      {{ new Date().getFullYear() }} — <strong>AstroMetric</strong>
    </div>
  </v-footer>

</template>

<style scoped>
.btn-footer{
  color: #1DCD9F;
}
.date{
  color: #c4eddd;
}

</style>
