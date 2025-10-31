<script setup>
import { reactive, ref } from 'vue'

import { login } from '../services/auth'

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const formRef = ref(null)

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
    successMessage.value = 'Login realizado com sucesso!'
  } catch (error) {
    errorMessage.value = error.message || 'Não foi possível realizar o login.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container fluid class="login-wrapper" tag="section">
    <v-row class="fill-height" align="center" justify="center">
      <v-col cols="12" md="8" lg="6" xl="5">
        <v-card class="login-card" rounded="xl">
          <v-card-title class="text-h5 text-md-h4 font-weight-bold mb-6">Login</v-card-title>

          <v-form ref="formRef" @submit.prevent="handleSubmit">
            <v-text-field
              v-model.trim="form.email"
              type="email"
              label="E-mail"
              autocomplete="email"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
              prepend-inner-icon="mdi-email-outline"
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
              prepend-inner-icon="mdi-lock-outline"
              class="mt-4"
              required
            />

            <v-btn class="mt-6" color="primary" block size="large" type="submit" :loading="loading">
              Entrar
            </v-btn>
          </v-form>

          <div class="mt-6">
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
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(2rem, 4vw, 4rem) 1.5rem;
  background:
    linear-gradient(135deg, rgba(167, 243, 208, 0.78), rgba(74, 222, 128, 0.85)),
    url('https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1920&q=80') center/cover no-repeat;
}

.login-card {
  padding: clamp(2rem, 4vw, 3.25rem);
  background-color: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
}

.login-card :deep(.v-card-title) {
  padding-inline: 0;
}

.login-card :deep(.v-form) {
  display: flex;
  flex-direction: column;
}

@media (max-width: 600px) {
  .login-wrapper {
    padding: 1.5rem 1rem;
  }
}
</style>

