import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { md3 } from 'vuetify/blueprints'

export default createVuetify({
  blueprint: md3,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#2563eb',
          secondary: '#7c3aed',
          background: '#f1f5f9',
          surface: '#ffffff',
          error: '#ef4444',
          success: '#10b981',
        },
      },
    },
  },
})

