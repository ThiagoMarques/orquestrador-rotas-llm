<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { login } from '../services/auth'

const form = reactive({ email: '', password: '', remember: false })
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const formRef = ref(null)
const router = useRouter()
const route = useRoute()

const resetFeedback = () => {
  errorMessage.value = ''
  successMessage.value = ''
}

const handleSubmit = async () => {
  if (loading.value) {
    return
  }

  await formRef.value?.validate?.()

  if (!form.email || !form.password) {
    errorMessage.value = 'Preencha e-mail e senha para continuar.'
    return
  }

  resetFeedback()
  loading.value = true

  try {
    const token = await login({ email: form.email, password: form.password })
    localStorage.setItem('accessToken', token)

    const redirectPath = (route.query.redirect && String(route.query.redirect)) || '/home'
    await router.push(redirectPath)
  } catch (error) {
    errorMessage.value = error.message || 'Não foi possível realizar o login.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container fluid class="login-page" tag="section">
    <v-row class="fill-height" align="center" justify="center" no-gutters>
      <v-col cols="12" sm="10" md="7" lg="6">
        <v-card class="login-card" rounded="lg" elevation="2">
          <div class="login-card__logo">
            <v-avatar size="40" color="primary" variant="tonal">
              <v-icon icon="mdi-vuetify" size="28" />
            </v-avatar>
          </div>

          <header class="login-card__header">
            <h1 class="login-card__title">Entre na sua conta</h1>
          </header>

          <v-form ref="formRef" class="login-card__form" @submit.prevent="handleSubmit">
            <v-text-field
              v-model.trim="form.email"
              type="email"
              label="E-mail"
              autocomplete="email"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
              required
            />

            <v-text-field
              v-model="form.password"
              type="password"
              label="Senha"
              autocomplete="current-password"
              minlength="6"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
              class="mt-4"
              required
            />

            <div class="login-card__actions mt-4">
              <v-btn variant="text" color="primary" class="text-capitalize" density="compact" type="button">
                Esqueceu a senha?
              </v-btn>
            </div>

            <v-btn class="mt-6" color="primary" block size="large" type="submit" :loading="loading">
              Entrar
            </v-btn>
          </v-form>

          <div class="login-card__feedback mt-6">
            <v-alert
              v-if="errorMessage"
              type="error"
              variant="tonal"
              density="comfortable"
              border="start"
            >
              {{ errorMessage }}
            </v-alert>

            <v-alert
              v-else-if="successMessage"
              type="success"
              variant="tonal"
              density="comfortable"
              border="start"
            >
              {{ successMessage }}
            </v-alert>
          </div>

          <footer class="login-card__footer mt-6">
            <span>Não tem uma conta?</span>
            <v-btn variant="text" color="primary" density="compact" class="text-capitalize" type="button">
              Cadastre-se
            </v-btn>
          </footer>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: clamp(2rem, 4vw, 4rem) 1.5rem;
  background-color: #f8fafc;
}

.login-card {
  padding: clamp(2.8rem, 4vw, 4rem);
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background-color: #fff;
  box-shadow:
    0 18px 45px rgba(15, 23, 42, 0.08),
    0 4px 18px rgba(15, 23, 42, 0.04);
}

.login-card__logo {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.login-card__title {
  margin: 0;
  font-size: clamp(1.8rem, 2.4vw, 2.4rem);
  font-weight: 700;
  color: #0f172a;
  text-align: center;
}

.login-card__header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.login-card__form {
  display: flex;
  flex-direction: column;
}

.login-card__actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-card__feedback :deep(.v-alert) {
  margin: 0;
}

.login-card__footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.95rem;
  color: #475569;
}

@media (max-width: 600px) {
  .login-page {
    padding: 1.5rem 1rem;
  }

  .login-card {
    padding: 2rem 1.5rem;
  }

  .login-card__actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>

