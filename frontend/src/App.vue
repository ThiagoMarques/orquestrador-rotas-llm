<template>
  <v-app>
    <v-main>
      <RouterView />
    </v-main>
  </v-app>
</template>

<style scoped>
:global(html, body, #app) {
  height: 100%;
  margin: 0;
}

:global(.v-application) {
  min-height: 100vh;
}

:global(.v-application .v-main) {
  min-height: 100vh;
}
</style>
