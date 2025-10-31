<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { register } from '../services/auth'

const form = reactive({ fullName: '', email: '', password: '', confirmPassword: '' })
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const formRef = ref(null)
const router = useRouter()

const passwordsMatch = () => form.password === form.confirmPassword

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

  if (!passwordsMatch()) {
    errorMessage.value = 'As senhas precisam ser iguais.'
    return
  }

  resetFeedback()
  loading.value = true

  try {
    await register({ email: form.email, password: form.password, fullName: form.fullName })
    successMessage.value = 'Conta criada com sucesso!'
    await router.push({ name: 'Login', query: { registered: 1 } })
  } catch (error) {
    errorMessage.value = error.message || 'Não foi possível criar a conta.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-container fluid class="register-page" tag="section">
    <v-row class="fill-height" align="center" justify="center" no-gutters>
      <v-col cols="12" sm="10" md="7" lg="6">
        <v-card class="register-card" rounded="lg" elevation="2">
          <div class="register-card__logo">
            <v-avatar size="40" color="primary" variant="tonal">
              <v-icon icon="mdi-account-plus" size="26" />
            </v-avatar>
          </div>

          <header class="register-card__header">
            <h1 class="register-card__title">Crie sua conta</h1>
          </header>

          <v-form ref="formRef" class="register-card__form" @submit.prevent="handleSubmit">
            <v-text-field
              v-model.trim="form.fullName"
              label="Nome completo"
              autocomplete="name"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
            />

            <v-text-field
              v-model.trim="form.email"
              type="email"
              label="E-mail"
              autocomplete="email"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
              class="mt-4"
              required
            />

            <v-text-field
              v-model="form.password"
              type="password"
              label="Senha"
              autocomplete="new-password"
              minlength="8"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
              class="mt-4"
              required
            />

            <v-text-field
              v-model="form.confirmPassword"
              type="password"
              label="Confirmar senha"
              autocomplete="new-password"
              minlength="8"
              density="comfortable"
              variant="outlined"
              :disabled="loading"
              class="mt-4"
              :error="!!form.confirmPassword && !passwordsMatch()"
              :error-messages="
                form.confirmPassword && !passwordsMatch() ? ['As senhas precisam ser iguais.'] : []
              "
              required
            />

            <v-btn class="mt-6" color="primary" block size="large" type="submit" :loading="loading">
              Registrar
            </v-btn>
          </v-form>

          <div class="register-card__feedback mt-6">
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

          <footer class="register-card__footer mt-6">
            <span>Já possui conta?</span>
            <v-btn :to="{ name: 'Login' }" variant="text" color="primary" density="compact" class="text-capitalize">
              Entrar
            </v-btn>
          </footer>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  padding: clamp(2rem, 4vw, 4rem) 1.5rem;
  background-color: #f8fafc;
}

.register-card {
  padding: clamp(2.8rem, 4vw, 4rem);
  border-radius: 16px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background-color: #fff;
  box-shadow:
    0 18px 45px rgba(15, 23, 42, 0.08),
    0 4px 18px rgba(15, 23, 42, 0.04);
}

.register-card__logo {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.register-card__title {
  margin: 0;
  font-size: clamp(1.8rem, 2.4vw, 2.4rem);
  font-weight: 700;
  color: #0f172a;
  text-align: center;
}

.register-card__header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.register-card__form {
  display: flex;
  flex-direction: column;
}

.register-card__feedback :deep(.v-alert) {
  margin: 0;
}

.register-card__footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.95rem;
  color: #475569;
}

@media (max-width: 600px) {
  .register-page {
    padding: 1.5rem 1rem;
  }

  .register-card {
    padding: 2rem 1.5rem;
  }
}
</style>

