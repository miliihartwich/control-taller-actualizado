<template>
  <div class="register">
    <div class="header">
      <h1>REGISTRARSE</h1>
    </div>

    <div class="form-container">
      <div class="input-group">
        <label for="username">Usuario</label>
        <input type="text" id="username" v-model="usuario" placeholder="Escriba aquí..." />
      </div>

      <div class="input-group">
        <label for="contrasena">Contraseña</label>
        <input type="password" id="contrasena" v-model="contrasena" placeholder="Escriba aquí..." />
      </div>

      <div class="input-group">
        <label for="confirm-password">Repita contraseña</label>
        <input type="password" id="confirm-password" v-model="confirmContrasena" placeholder="Escriba aquí..." />
      </div>

      <div class="input-group">
        <label for="empleado">Empleado</label>
        <select id="empleado" v-model="empleado">
          <option value="" disabled>Elija una opción...</option>
          <option
            v-for="e in empleadosOrdenados"
            :key="e.cedula"
            :value="String(e.cedula)"
          >
            {{ e.nombre }} — {{ e.cedula }}
          </option>
        </select>
        <small v-if="empleados.length === 0">No hay empleados para mostrar.</small>
      </div>

      <div class="buttons-container">
        <button class="btn" @click="registrar">REGISTRARME</button>
        <router-link to="/"><button class="btn">Volver</button></router-link>
      </div>

      <div v-if="mensaje" :class="['mensaje', tipoMensaje]">{{ mensaje }}</div>

    </div>
  </div>
</template>

<script>
import { apiGet, apiPost } from '@/api';

export default {
  name: 'RegisterPage',
  data() {
    return {
      usuario: '',
      rol: 'operario',
      contrasena: '',
      confirmContrasena: '',
      empleado: '',      // cédula como string
      empleados: [],     // [{cedula, nombre}]
      mensaje: '',
      tipoMensaje: ''
    };
  },

  computed: {
    empleadosOrdenados() {
      return [...this.empleados].sort((a, b) => a.nombre.localeCompare(b.nombre));
    },
  },

  methods: {
    async fetchEmpleados() {
      this.mensaje = '';
      this.tipoMensaje = '';
      try {
        // -> llama a /api/obtener_empleados por el proxy
        const data = await apiGet('/obtener_empleados');
        const lista = Array.isArray(data) ? data : (data?.empleados || []);
        this.empleados = lista
          .map(e => ({ cedula: e.cedula, nombre: e.nombre }))
          .filter(e => e.cedula != null && e.nombre);

        if (!this.empleados.length) {
          this.mensaje = 'No hay empleados para mostrar.';
          this.tipoMensaje = 'error';
        }
      } catch (e) {
        console.error('fetchEmpleados ERROR:', e);
        this.mensaje = 'No se pudo cargar la lista de empleados.';
        this.tipoMensaje = 'error';
      }
    },

    async registrar() {
      this.mensaje = '';
      this.tipoMensaje = '';

      if (!this.usuario || !this.contrasena || !this.confirmContrasena || !this.empleado) {
        this.mensaje = 'Todos los campos son obligatorios.'; this.tipoMensaje = 'error'; return;
      }
      if (this.contrasena !== this.confirmContrasena) {
        this.mensaje = 'Las contraseñas no coinciden.'; this.tipoMensaje = 'error'; return;
      }

      try {
        // -> llama a /api/registrar_usuario (el helper agrega /api)
        const resp = await apiPost('/registrar_usuario', {
          usuario: this.usuario,
          rol: this.rol,
          contrasena: this.contrasena,
          cedula: Number(this.empleado),
        });

        this.mensaje = resp?.message || 'Usuario registrado exitosamente';
        this.tipoMensaje = 'exito';
        this.usuario = ''; this.rol = 'operario'; this.contrasena = '';
        this.confirmContrasena = ''; this.empleado = '';
      } catch (e) {
        console.error('registrar ERROR:', e);
        this.mensaje = e.message || 'Error al registrar usuario';
        this.tipoMensaje = 'error';
      }
    }
  },

  mounted() {
    this.fetchEmpleados();
  }
};
</script>


<style scoped>
.register {
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

input, select {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-top: 5px;
}

.buttons-container {
  display: flex;
  justify-content: center;
  gap: 20px; /* Espacio entre botones */
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
  text-align: center; /* Asegura que el texto esté centrado */
  display: flex;
  align-items: center;
  justify-content: center; /* Centra el texto horizontalmente */
}

.btn:hover {
  background-color: rgba(43, 0, 255);
}

.mensaje {
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  text-align: center;
  font-weight: bold;
}

.exito {
  background-color: #4caf50 !important;
  color: white !important;
}

.error {
  background-color: #f44336 !important;
  color: white !important;
}

</style>
