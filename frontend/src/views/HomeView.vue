<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getCurrentUser } from '../services/user'

const router = useRouter()
const route = useRoute()

const user = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const favoriteCities = ref([
  { name: 'Brasília', uf: 'DF', addedAt: '10/03/2025' },
  { name: 'São Paulo', uf: 'SP', addedAt: '05/03/2025' },
  { name: 'Rio de Janeiro', uf: 'RJ', addedAt: '22/02/2025' },
])

const plannedRoutes = ref([
  { from: 'Brasília', to: 'Ribeirão Preto', date: '12/04/2025', status: 'Confirmada' },
  { from: 'São Paulo', to: 'Belo Horizonte', date: '28/03/2025', status: 'Em análise' },
])

const aiSuggestions = ref([
  {
    from: 'Curitiba',
    to: 'Florianópolis',
    reason: 'Alta demanda prevista para o próximo feriado prolongado.',
  },
])

const displayName = computed(() => {
  if (user.value?.full_name) {
    return user.value.full_name
  }

  if (user.value?.email) {
    return user.value.email.split('@')[0]
  }

  return 'usuário'
})

const handleAuthError = () => {
  localStorage.removeItem('accessToken')
  router.push({ name: 'Login', query: { redirect: route.fullPath } })
}

onMounted(async () => {
  try {
    user.value = await getCurrentUser()
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    errorMessage.value = error.message || 'Não foi possível carregar as informações.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <v-container fluid class="home-page" tag="section">
    <v-row>
      <v-col cols="12">
        <v-card class="home-greeting" rounded="lg" elevation="2">
          <div class="home-greeting__content">
            <div>
              <h1>Bem-vindo, {{ displayName }}!</h1>
              <p>Gerencie suas cidades favoritas, rotas planejadas e sugestões inteligentes em um só lugar.</p>
            </div>
            <v-avatar size="56" color="primary" variant="tonal">
              <v-icon icon="mdi-map-marker-path" size="32" />
            </v-avatar>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4" dense>
      <v-col cols="12" md="4">
        <v-card class="home-card" rounded="lg" elevation="1">
          <v-card-title class="home-card__title">Cidades escolhidas</v-card-title>
          <v-card-subtitle class="home-card__subtitle">Locais que você acompanha mais de perto.</v-card-subtitle>

          <v-divider class="my-4" />

          <v-skeleton-loader v-if="loading" type="list-item-two-line@3" />

          <v-list v-else density="comfortable">
            <v-list-item
              v-for="city in favoriteCities"
              :key="city.name"
              :title="city.name"
              :subtitle="`${city.uf} • adicionado em ${city.addedAt}`"
              prepend-icon="mdi-city-variant-outline"
            />
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="home-card" rounded="lg" elevation="1">
          <v-card-title class="home-card__title">Rotas planejadas</v-card-title>
          <v-card-subtitle class="home-card__subtitle">Itinerários confirmados ou em validação.</v-card-subtitle>

          <v-divider class="my-4" />

          <v-skeleton-loader v-if="loading" type="list-item-three-line@2" />

          <v-list v-else density="comfortable">
            <v-list-item
              v-for="routeItem in plannedRoutes"
              :key="`${routeItem.from}-${routeItem.to}`"
            >
              <template #prepend>
                <v-avatar color="primary" variant="tonal" size="36">
                  <v-icon icon="mdi-route-variant" size="22" />
                </v-avatar>
              </template>

              <v-list-item-title>{{ routeItem.from }} → {{ routeItem.to }}</v-list-item-title>
              <v-list-item-subtitle>
                <span>{{ routeItem.date }}</span>
                <span class="dot" />
                <span>{{ routeItem.status }}</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="home-card" rounded="lg" elevation="1">
          <v-card-title class="home-card__title">Sugestões da IA</v-card-title>
          <v-card-subtitle class="home-card__subtitle">Recomendações inteligentes para novas rotas.</v-card-subtitle>

          <v-divider class="my-4" />

          <v-skeleton-loader v-if="loading" type="list-item" />

          <div v-else class="ai-suggestion" v-for="suggestion in aiSuggestions" :key="`${suggestion.from}-${suggestion.to}`">
            <div class="ai-suggestion__route">{{ suggestion.from }} → {{ suggestion.to }}</div>
            <p>{{ suggestion.reason }}</p>
            <v-alert type="info" variant="tonal" density="comfortable" border="start" class="mt-3">
              Em breve, mostraremos aqui as rotas sugeridas dinamicamente pela IA.
            </v-alert>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="errorMessage" class="mt-4">
      <v-col cols="12">
        <v-alert type="error" variant="tonal" density="comfortable" border="start">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: clamp(2rem, 4vw, 4rem) 1.5rem 4rem;
  background-color: #f8fafc;
}

.home-greeting {
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.12), rgba(59, 130, 246, 0.08));
  border: 1px solid rgba(15, 23, 42, 0.05);
}

.home-greeting__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.home-greeting h1 {
  margin: 0;
  font-size: clamp(1.8rem, 2.5vw, 2.4rem);
  font-weight: 700;
  color: #0f172a;
}

.home-greeting p {
  margin: 0.5rem 0 0;
  color: #475569;
  font-size: 1rem;
}

.home-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: clamp(1.5rem, 3vw, 2rem);
  border: 1px solid rgba(15, 23, 42, 0.05);
}

.home-card__title {
  font-weight: 700;
  font-size: 1.2rem;
  color: #0f172a;
}

.home-card__subtitle {
  color: #64748b;
}

.ai-suggestion {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ai-suggestion__route {
  font-weight: 600;
  color: #115e59;
  font-size: 1.05rem;
}

.dot {
  display: inline-block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: #cbd5f5;
  margin: 0 0.5rem;
}

@media (max-width: 960px) {
  .home-greeting__content {
    flex-direction: column;
    align-items: flex-start;
  }

  .home-page {
    padding-bottom: 2.5rem;
  }
}

@media (max-width: 600px) {
  .home-card {
    padding: 1.5rem 1.25rem;
  }
}
</style>

