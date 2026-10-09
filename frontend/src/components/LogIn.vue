<!-- src/components/LogIn.vue -->
<template>
  <div class="login">
    <div class="header">
      <h1>Iniciar sesión</h1>
    </div>

    <div class="form-container">
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="login" autocomplete="on">
        <div class="input-group">
          <label for="username">Usuario</label>
          <input
            type="text"
            v-model.trim="username"
            id="username"
            placeholder="Ingrese su usuario"
            autocomplete="username"
            :disabled="cargando"
            @keyup.enter="login"
            required
          />
        </div>

        <div class="input-group">
          <label for="password">Contraseña</label>
          <input
            type="password"
            v-model="password"
            id="password"
            placeholder="Ingrese su contraseña"
            autocomplete="current-password"
            :disabled="cargando"
            @keyup.enter="login"
            required
          />
<div class="buttons-container">
  <button type="submit" class="btn" :disabled="cargando">
    {{ cargando ? 'Ingresando…' : 'Iniciar sesión' }}
  </button>

  <router-link to="/" class="btn" :class="{ disabled: cargando }">
    Volver
  </router-link>
</div>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { login as apiLogin } from '@/api';
import { setCurrentUser, clearCurrentUser } from '@/sessionStore';

export default {
  name: 'LoginPage',
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
      cargando: false,
    };
  },
  methods: {
    async login() {
      this.errorMessage = '';

      if (!this.username || !this.password) {
        this.errorMessage = 'Por favor, complete todos los campos.';
        return;
      }

      this.cargando = true;

      try {
        // (opcional) limpiar sesión previa antes de loguear
        clearCurrentUser();

        // LOGIN REAL
        const data = await apiLogin({
          usuario: this.username,
          contrasena: this.password,
        });

        const rolLower = (data?.rol || '').toString().trim().toLowerCase();
        const cedula = data?.cedula ?? '';

        // ✅ CLAVE: setear sesión en el store
        setCurrentUser({ ...data, rol: rolLower });

        // Persistencia mínima
        try {
          localStorage.setItem('usuario', this.username);
          localStorage.setItem('rol', rolLower);
          localStorage.setItem('cedula', String(cedula));
        } catch {}

        // Navegación por rol
        const isOperario = rolLower === 'operario';
        const target = isOperario ? { name: 'IntervencionOperario' } : { name: 'MenuPage' };

        await this.$router.push(target);

        // Fallback por si el router no navega por alguna razón
        if (window.location.pathname === '/login') {
          window.location.assign(isOperario ? '/intervencion-operario' : '/menu');
        }

      } catch (error) {
        this.errorMessage =
          error?.status === 401
            ? 'Usuario o contraseña inválidos.'
            : error?.message || 'No se pudo conectar con el servidor.';
      } finally {
        this.cargando = false;
        this.password = '';
      }
    },
  },
};
</script>




<style scoped>
.login {
  text-align: center;
}

.header {
  background-color: rgba(214, 15, 15, 0.8);
  padding: 40px;
  color: white;
}

h1 {
  margin: 0;
  font-size: 3rem;
}

.form-container {
  margin-top: 30px;
  padding: 20px;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  font-size: 1.2rem;
  margin-bottom: 8px;
  display: block;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 5px;
}

.forgot-password-link {
  display: block;
  margin-top: 10px;
  color: rgba(214, 15, 15, 0.8);
  text-decoration: none;
  font-size: 1rem;
}

.forgot-password-link:hover {
  text-decoration: underline;
}

.buttons-container {
  margin-top: 30px;
}

.btn {
  background-color: rgba(214, 15, 15, 0.8);
  color: white;
  font-size: 1.2rem;
  padding: 15px 40px;
  margin: 10px;
  border: none;
  cursor: pointer;
  width: 200px;
}

.btn:hover {
  background-color: rgba(43, 0, 255);
}

.error-message {
  color: red;
  margin-bottom: 15px;
  font-size: 1.1rem;
  font-weight: bold;
}
</style>
