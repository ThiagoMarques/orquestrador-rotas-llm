<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { createCity, deleteCity, listCities, updateCity } from '../services/cities'
import { sendGeminiMessage } from '../services/ai'
import { listRoutes, getRouteById, downloadRouteCsv, deleteRoutes } from '../services/routes'
import { getCurrentUser } from '../services/user'

const router = useRouter()
const route = useRoute()

const user = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const cities = ref([])
const citiesLoading = ref(true)
const cityDialog = ref(false)
const cityFormRef = ref(null)
const cityFormLoading = ref(false)
const cityForm = reactive({ id: null, name: '', state: '' })
const deleteDialog = ref(false)
const cityToDelete = ref(null)
const snackbar = reactive({ show: false, text: '', color: 'success' })
const chatMessage = ref('')
const chatResponse = ref('')
const chatLoading = ref(false)
const routes = ref([])
const routesLoading = ref(true)
const routeDetailDialog = ref(false)
const selectedRoute = ref(null)
const routeDetailLoading = ref(false)
const selectionMode = ref(false)
const selectedRouteIds = ref([])

const hasMinimumCities = computed(() => cities.value.length >= 2)

const aiSuggestions = ref([
  {
    from: 'Curitiba',
    to: 'Florianópolis',
    reason: 'Alta demanda prevista para o próximo feriado prolongado.',
  },
])

const sendChatMessage = async () => {
  if (!hasMinimumCities.value) {
    snackbar.text = 'Adicione pelo menos duas cidades para planejar uma rota.'
    snackbar.color = 'warning'
    snackbar.show = true
    return
  }

  if (!chatMessage.value.trim()) {
    return
  }

  chatLoading.value = true
  chatResponse.value = ''

  try {
    const { response } = await sendGeminiMessage(chatMessage.value)
    chatResponse.value = response
    chatMessage.value = ''
    await loadRoutes()
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    snackbar.text = error.message || 'Não foi possível obter a resposta da IA.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    chatLoading.value = false
  }
}

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

const resetCityForm = () => {
  cityForm.id = null
  cityForm.name = ''
  cityForm.state = ''
}

const openCreateCity = () => {
  resetCityForm()
  cityDialog.value = true
}

const openEditCity = (city) => {
  cityForm.id = city.id
  cityForm.name = city.name
  cityForm.state = city.state
  cityDialog.value = true
}

const submitCityForm = async () => {
  const validation = await cityFormRef.value?.validate?.()
  if (validation && validation.valid === false) {
    return
  }

  if (!cityForm.name || !cityForm.state) {
    return
  }

  const payload = {
    name: cityForm.name.trim(),
    state: cityForm.state.trim().toUpperCase(),
  }

  cityFormLoading.value = true
  try {
    if (cityForm.id) {
      await updateCity(cityForm.id, payload)
      snackbar.text = 'Cidade atualizada com sucesso.'
    } else {
      await createCity(payload)
      snackbar.text = 'Cidade cadastrada com sucesso.'
    }
    snackbar.color = 'success'
    snackbar.show = true
    cityDialog.value = false
    await loadCities()
    resetCityForm()
  } catch (error) {
    snackbar.text = error.message || 'Não foi possível salvar a cidade.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    cityFormLoading.value = false
  }
}

const confirmDeleteCity = (city) => {
  cityToDelete.value = city
  deleteDialog.value = true
}

const performDeleteCity = async () => {
  if (!cityToDelete.value) {
    return
  }

  try {
    await deleteCity(cityToDelete.value.id)
    snackbar.text = 'Cidade removida com sucesso.'
    snackbar.color = 'success'
    snackbar.show = true
    await loadCities()
  } catch (error) {
    snackbar.text = error.message || 'Não foi possível remover a cidade.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    deleteDialog.value = false
    cityToDelete.value = null
  }
}

const loadCities = async () => {
  citiesLoading.value = true
  try {
    cities.value = await listCities()
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    snackbar.text = error.message || 'Não foi possível carregar suas cidades.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    citiesLoading.value = false
  }
}

const loadRoutes = async () => {
  routesLoading.value = true
  try {
    routes.value = await listRoutes()
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    snackbar.text = error.message || 'Não foi possível carregar as rotas planejadas.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    routesLoading.value = false
  }
}

const openRouteDetail = async (routeSummary) => {
  routeDetailDialog.value = true
  routeDetailLoading.value = true
  selectedRoute.value = null

  try {
    const detail = await getRouteById(routeSummary.id)
    selectedRoute.value = detail
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    snackbar.text = error.message || 'Não foi possível carregar detalhes da rota.'
    snackbar.color = 'error'
    snackbar.show = true
    routeDetailDialog.value = false
  } finally {
    routeDetailLoading.value = false
  }
}

const handleDownloadCsv = async (routeId) => {
  try {
    const blob = await downloadRouteCsv(routeId)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `rota-${routeId}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    snackbar.text = error.message || 'Não foi possível baixar o CSV da rota.'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

const formatDate = (value) => {
  if (!value) {
    return 'Data a definir'
  }

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) {
    return value
  }

  return parsed.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value
  if (!selectionMode.value) {
    selectedRouteIds.value = []
  }
}

const toggleRouteSelection = (routeId) => {
  if (!selectionMode.value) {
    return
  }

  const index = selectedRouteIds.value.indexOf(routeId)
  if (index >= 0) {
    selectedRouteIds.value.splice(index, 1)
  } else {
    selectedRouteIds.value.push(routeId)
  }
}

const removeSelectedRoutes = async () => {
  if (!selectedRouteIds.value.length) {
    snackbar.text = 'Selecione ao menos uma rota para excluir.'
    snackbar.color = 'warning'
    snackbar.show = true
    return
  }

  try {
    await deleteRoutes(selectedRouteIds.value)
    snackbar.text = 'Rotas removidas com sucesso.'
    snackbar.color = 'success'
    snackbar.show = true
    selectionMode.value = false
    selectedRouteIds.value = []
    await loadRoutes()
  } catch (error) {
    if (error.status === 401) {
      handleAuthError()
      return
    }

    snackbar.text = error.message || 'Não foi possível remover as rotas selecionadas.'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

watch(cityDialog, (isOpen) => {
  if (!isOpen) {
    cityFormRef.value?.resetValidation?.()
    resetCityForm()
  }
})

watch(
  () => cityForm.state,
  (value) => {
    if (!value) {
      return
    }

    const formatted = value.toUpperCase().slice(0, 2)
    if (formatted !== value) {
      cityForm.state = formatted
    }
  }
)

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

  await loadCities()
  await loadRoutes()
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
          <v-card-title class="home-card__title">
            <span class="material-icons home-card__icon">location_city</span>
            Cidades escolhidas
          </v-card-title>
          <v-card-subtitle class="home-card__subtitle">Locais que você acompanha mais de perto.</v-card-subtitle>

          <v-divider class="my-4" />

          <v-skeleton-loader v-if="citiesLoading" type="list-item-two-line@3" />

          <v-list v-else-if="cities.length" density="comfortable">
            <v-list-item v-for="city in cities" :key="city.id">
              <template #prepend>
                <v-avatar color="primary" variant="tonal" size="36">
                  <v-icon icon="mdi-city-variant-outline" size="22" />
                </v-avatar>
              </template>

              <v-list-item-title>{{ city.name }}</v-list-item-title>
              <v-list-item-subtitle>{{ city.state }}</v-list-item-subtitle>

              <template #append>
                <div class="city-actions">
                  <button class="city-actions__icon" type="button" @click="openEditCity(city)">
                    <span class="material-icons">edit</span>
                  </button>
                  <button
                    class="city-actions__icon city-actions__icon--danger"
                    type="button"
                    @click="confirmDeleteCity(city)"
                  >
                    <span class="material-icons">delete</span>
                  </button>
                </div>
              </template>
            </v-list-item>
          </v-list>

          <div v-else class="empty-state">
            <v-icon icon="mdi-map-marker-plus" color="primary" size="32" class="mb-3" />
            <p>Nenhuma cidade cadastrada ainda.</p>
            <v-btn color="primary" variant="tonal" @click="openCreateCity">Cadastrar cidade</v-btn>
          </div>

          <v-card-actions class="mt-auto pt-4" v-if="cities.length">
            <v-btn block color="primary" variant="tonal" @click="openCreateCity">Cadastrar cidade</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="home-card" rounded="lg" elevation="1">
          <v-card-title class="home-card__title">
            <span class="material-icons home-card__icon">route</span>
            Rotas planejadas
          </v-card-title>
          <v-card-subtitle class="home-card__subtitle">Itinerários confirmados ou em validação.</v-card-subtitle>

          <v-divider class="my-4" />

          <v-skeleton-loader v-if="routesLoading" type="list-item-three-line@2" />

          <v-list v-else-if="routes.length" density="comfortable">
            <v-list-item
              v-for="routeItem in routes"
              :key="routeItem.id"
              class="planned-route-item"
              @click="selectionMode ? toggleRouteSelection(routeItem.id) : openRouteDetail(routeItem)"
            >
              <template #prepend>
                <v-avatar color="primary" variant="tonal" size="36">
                  <v-icon icon="mdi-route-variant" size="22" />
                </v-avatar>
                <v-checkbox-btn
                  v-if="selectionMode"
                  :model-value="selectedRouteIds.includes(routeItem.id)"
                  class="ml-2"
                  @click.stop="toggleRouteSelection(routeItem.id)"
                />
              </template>

              <v-list-item-title>{{ routeItem.itinerary }}</v-list-item-title>
              <v-list-item-subtitle>
                <span>{{ formatDate(routeItem.travel_date) }}</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>

          <div v-else class="empty-state">
            <v-icon icon="mdi-map-search-outline" color="primary" size="32" class="mb-3" />
            <p>Nenhuma rota planejada ainda. Envie uma mensagem no chat para gerar sugestões.</p>
          </div>

          <v-card-actions class="pt-4" v-if="routes.length">
            <v-btn
              variant="tonal"
              color="primary"
              @click="toggleSelectionMode"
            >
              {{ selectionMode ? 'Cancelar seleção' : 'Selecionar rotas' }}
            </v-btn>
            <v-btn
              v-if="selectionMode"
              color="error"
              variant="text"
              :disabled="!selectedRouteIds.length"
              @click="removeSelectedRoutes"
            >
              Remover selecionadas
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card class="home-card" rounded="lg" elevation="1">
          <v-card-title class="home-card__title">
            <span class="material-icons home-card__icon">psychology</span>
            Sugestões da IA
          </v-card-title>
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

    <v-row v-if="chatLoading || chatResponse" class="mt-6">
      <v-col cols="12">
        <v-card class="ai-response" rounded="lg" elevation="1">
          <div v-if="chatLoading" class="ai-response__loading">
            <span class="material-icons chat-loader">autorenew</span>
            <span>Consultando o Gemini...</span>
          </div>
          <div v-else class="ai-response__content">
            <h3>Resposta da IA</h3>
            <p>{{ chatResponse }}</p>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="!hasMinimumCities" class="mt-8">
      <v-col cols="12">
        <v-alert type="warning" variant="tonal" density="comfortable" border="start">
          Cadastre pelo menos duas cidades no card "Cidades escolhidas" para planejar rotas com a IA.
        </v-alert>
      </v-col>
    </v-row>

    <v-row class="mt-6">
      <v-col cols="12">
        <v-card class="chat-input" rounded="xl" elevation="2">
          <div class="chat-input__wrapper">
            <v-textarea
              v-model="chatMessage"
              class="chat-input__textarea"
              variant="plain"
              rows="2"
              auto-grow
              hide-details
              placeholder="Digite sua mensagem..."
              base-color="transparent"
              :readonly="!hasMinimumCities"
            />

            <v-btn
              color="primary"
              class="chat-input__send"
              rounded="xl"
              :loading="chatLoading"
              :disabled="!hasMinimumCities || !chatMessage.trim() || chatLoading"
              @click="sendChatMessage"
            >
              Enviar
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="cityDialog" max-width="480">
      <v-card>
        <v-card-title class="text-h6">
          {{ cityForm.id ? 'Editar cidade' : 'Cadastrar cidade' }}
        </v-card-title>

        <v-card-text>
          <v-form ref="cityFormRef" @submit.prevent="submitCityForm">
            <v-text-field
              v-model.trim="cityForm.name"
              label="Nome da cidade"
              placeholder="Ex.: Brasília"
              :rules="[(v) => !!v || 'Informe o nome da cidade.']"
              :disabled="cityFormLoading"
              variant="outlined"
              density="comfortable"
            />

            <v-text-field
              v-model.trim="cityForm.state"
              label="UF"
              placeholder="Ex.: DF"
              class="mt-4"
              :rules="[
                (v) => !!v || 'Informe a UF.',
                (v) => !v || v.length === 2 || 'Informe apenas 2 caracteres.',
              ]"
              :disabled="cityFormLoading"
              variant="outlined"
              density="comfortable"
              maxlength="2"
              counter="2"
            />
          </v-form>
        </v-card-text>

        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="cityDialog = false" :disabled="cityFormLoading">Cancelar</v-btn>
          <v-btn color="primary" :loading="cityFormLoading" @click="submitCityForm">
            {{ cityForm.id ? 'Salvar' : 'Cadastrar' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="routeDetailDialog" max-width="560">
      <v-card>
        <v-card-title class="text-h6">
          {{ selectedRoute?.itinerary || 'Detalhes da rota' }}
        </v-card-title>

        <v-card-text>
          <div v-if="routeDetailLoading" class="route-detail__loading">
            <span class="material-icons chat-loader">autorenew</span>
            <span>Carregando detalhes...</span>
          </div>

          <div v-else-if="selectedRoute">
            <p class="route-detail__summary">{{ selectedRoute.summary }}</p>

            <v-table class="route-detail__table" density="compact">
              <tbody>
                <tr>
                  <th>Data prevista</th>
                  <td>{{ formatDate(selectedRoute.travel_date) }}</td>
                </tr>
                <tr>
                  <th>Distância</th>
                  <td>{{ selectedRoute.distance_km || '—' }}</td>
                </tr>
                <tr>
                  <th>Tempo de viagem</th>
                  <td>{{ selectedRoute.travel_time || '—' }}</td>
                </tr>
                <tr>
                  <th>Custo estimado</th>
                  <td>{{ selectedRoute.cost_brl || '—' }}</td>
                </tr>
                <tr>
                  <th>Tipo de viagem</th>
                  <td>{{ selectedRoute.trip_type || '—' }}</td>
                </tr>
                <tr>
                  <th>Transporte</th>
                  <td>{{ selectedRoute.transport_type || '—' }}</td>
                </tr>
                <tr>
                  <th>Hospedagem</th>
                  <td>{{ selectedRoute.lodging || '—' }}</td>
                </tr>
                <tr>
                  <th>Alimentação</th>
                  <td>{{ selectedRoute.food || '—' }}</td>
                </tr>
                <tr>
                  <th>Atividade</th>
                  <td>{{ selectedRoute.activity || '—' }}</td>
                </tr>
                <tr>
                  <th>Gasto estimado</th>
                  <td>{{ selectedRoute.estimated_spend_brl || '—' }}</td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </v-card-text>

        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="routeDetailDialog = false">Fechar</v-btn>
          <v-btn
            v-if="selectedRoute"
            color="primary"
            variant="tonal"
            @click="handleDownloadCsv(selectedRoute.id)"
          >
            Baixar CSV
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="deleteDialog" max-width="420">
      <v-card>
        <v-card-title class="text-h6">Remover cidade</v-card-title>
        <v-card-text>
          Tem certeza que deseja remover "{{ cityToDelete?.name }}"?
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn variant="text" @click="deleteDialog = false">Cancelar</v-btn>
          <v-btn color="error" @click="performDeleteCity">Remover</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="4000">
      {{ snackbar.text }}
    </v-snackbar>
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
  padding: clamp(1.5rem, 3vw, 2.25rem);
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

.home-card__icon {
  margin-right: 0.5rem;
  font-size: 22px;
  color: #2563eb;
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

.empty-state {
  padding: 1rem 0 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.75rem;
  color: #64748b;
}

.city-actions {
  display: flex;
  gap: 0.35rem;
  align-items: center;
}

.city-actions__icon {
  background-color: rgba(59, 130, 246, 0.1);
  border: none;
  border-radius: 50%;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #1d4ed8;
  transition: background-color 0.2s ease;
}

.city-actions__icon:hover {
  background-color: rgba(59, 130, 246, 0.2);
}

.city-actions__icon span {
  font-size: 18px;
  line-height: 18px;
}

.city-actions__icon--danger {
  background-color: rgba(239, 68, 68, 0.12);
  color: #dc2626;
}

.city-actions__icon--danger:hover {
  background-color: rgba(239, 68, 68, 0.2);
}

.chat-input {
  border: 1px solid rgba(15, 23, 42, 0.06);
  background-color: #ffffff;
}

.chat-input__wrapper {
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  padding: 1.25rem;
}

.chat-input__textarea {
  flex: 1;
  padding: 0;
}

.chat-input__textarea :deep(.v-field) {
  padding: 0;
}

.chat-input__textarea :deep(textarea) {
  padding: 0;
  padding-top: 1.25rem;
  font-size: 1rem;
  line-height: 1.5;
}

.chat-input__textarea :deep(textarea::placeholder) {
  color: #94a3b8;
  opacity: 1;
}

.chat-input__send {
  min-width: 120px;
  padding: 0.75rem 1.25rem;
}

.ai-response {
  border: 1px solid rgba(15, 23, 42, 0.06);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(45, 212, 191, 0.08));
  padding: clamp(1.5rem, 2.8vw, 2rem);
}

.planned-route-item {
  cursor: pointer;
}

.planned-route-item:hover {
  background-color: rgba(59, 130, 246, 0.08);
}

.route-detail__loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.route-detail__summary {
  margin: 0 0 1rem;
  color: #1f2937;
  line-height: 1.6;
}

.route-detail__table th {
  text-align: left;
  color: #475569;
  font-weight: 600;
  padding-right: 1rem;
  white-space: nowrap;
}

.route-detail__table td {
  color: #0f172a;
}

.ai-response__loading,
.ai-response__content {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.ai-response__content {
  flex-direction: column;
  align-items: flex-start;
}

.ai-response__content h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #0f172a;
}

.ai-response__content p {
  margin: 0;
  color: #1f2937;
  white-space: pre-wrap;
  line-height: 1.6;
}

.chat-loader {
  font-size: 28px;
  color: #2563eb;
  animation: chat-spin 1.2s linear infinite;
}

@keyframes chat-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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

