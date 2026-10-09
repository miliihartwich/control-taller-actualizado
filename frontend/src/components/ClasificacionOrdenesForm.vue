<template>
  <div class="clasificacionordenes-container">
    <h1 class="titulo">Clasificación de órdenes</h1>

    <!-- Mensajes -->
    <div v-if="mensaje.texto" :class="['mensaje', mensaje.tipo]">
      {{ mensaje.texto }}
      <div v-if="mensaje.tipo === 'confirmacion'">
        <button @click="guardarConfiguracion(mensaje.clave)">Aceptar</button>
        <button @click="cancelarConfirmacion(mensaje.clave)">Cancelar</button>
      </div>
    </div>

    <!-- División -->
    <div class="clasificador">
      <button v-if="!editando.division" @click="iniciarEdicion('division')">Nueva División</button>
      <div v-else>
        <label>División</label>
        <input type="text" v-model="clasificacion_ordenes.division" />
        <button @click="confirmarGuardado('division')">Guardar</button>
      </div>
    </div>

    <!-- Tipo -->
    <div class="parametro">
      <button v-if="!editando.tipo" @click="iniciarEdicion('tipo')">Nuevo Tipo</button>
      <div v-else>
        <label>División</label>
        <select v-model="clasificacion_ordenes.divisionSeleccionada" v-if="divisiones.length > 0">
          <option v-for="(division, index) in divisiones" :key="index" :value="division">
            {{ division }}
          </option>
        </select>
        <label>Tipo</label>
        <input type="text" v-model="clasificacion_ordenes.tipo" />
        <button @click="confirmarGuardado('tipo')">Guardar</button>
      </div>
    </div>

    
      <button @click="goTo('MenuPage')" class="botones">Menú</button>
    
  </div>
</template>

<script>
import { apiFetch } from '@/api'; // <-- usa tu helper

export default {
  data() {
    return {
      clasificacion_ordenes: { division: '', tipo: '', divisionSeleccionada: '' },
      editando: { division: false, tipo: false },
      mensaje: { texto: '', tipo: '', clave: '' },
      divisiones: [] // Almacenará las divisiones disponibles
    };
  },
  mounted() {
    this.obtenerDivisiones(); // Cargar divisiones al montar el componente
  },
  methods: {
    // Método para cargar divisiones desde el backend
    async obtenerDivisiones() {
      try {
        const data = await apiFetch('/divisiones');
        this.divisiones = data; // <- data directo (no response.data)
      } catch (error) {
        console.error('Error al cargar las divisiones:', error.message);
      }
    },
    iniciarEdicion(clave) {
      this.editando[clave] = true;
    },

    confirmarGuardado(clave) {
      this.mensaje = {
        texto: `¿Seguro que deseas guardar la nueva clasificación de ${clave}?`,
        tipo: 'confirmacion',
        clave: clave,
      };
    },

    async guardarConfiguracion(clave) {
      if (clave === 'division') {
        await this.guardarDivision();
      } else if (clave === 'tipo') {
        await this.guardarTipo();
      }
    },

    async guardarDivision() {
      if (!this.clasificacion_ordenes.division.trim()) {
        this.mostrarError('El nombre de la división no puede estar vacío');
        return;
      }
      await this.enviarDatos('agregar_division', { nombre: this.clasificacion_ordenes.division });
      this.mostrarMensaje('División guardada con éxito', 'exito');
      this.limpiarCampos('division');
      await this.obtenerDivisiones(); // <-- refresca lista
    },

    async guardarTipo() {
      if (!this.clasificacion_ordenes.tipo.trim()) {
        this.mostrarError('El nombre del tipo no puede estar vacío');
        return;
      }
      if (!this.clasificacion_ordenes.divisionSeleccionada) {
        this.mostrarError('Debes seleccionar una división');
        return;
      }
      await this.enviarDatos('agregar_tipo', { nombre: this.clasificacion_ordenes.tipo, division: this.clasificacion_ordenes.divisionSeleccionada });
      this.mostrarMensaje('Tipo guardado con éxito', 'exito');
      this.limpiarCampos('tipo');
    },

    async enviarDatos(endpoint, datos) {
      try {
        await apiFetch(`/${endpoint}`, { method: 'POST', body: datos /* , auth: true */ });
      } catch (error) {
        this.mostrarError(error.message || 'Error al guardar');
      }
    },


    mostrarMensaje(texto, tipo) {
      this.mensaje = { texto, tipo };
      setTimeout(() => {
        this.mensaje = { texto: '', tipo: '' };
      }, 3000);
    },

    mostrarError(texto) {
      this.mostrarMensaje(texto, 'error');
    },

    limpiarCampos(clave) {
      this.clasificacion_ordenes[clave] = '';
      this.editando[clave] = false;
    },

    cancelarConfirmacion(clave) {
      this.mensaje = { texto: '', tipo: '', clave: '' };
      this.editando[clave] = false;
    },
    goTo(routeName) {
        this.$router.push({ name: routeName });
      },
  },
};
</script>

<style scoped>
.clasificacionordenes-container {
  width: 400px;
  margin: 20px auto;
  text-align: center;
}

.titulo {
  background-color: #a84d4d;
  color: white;
  padding: 10px;
  font-weight: bold;
}

.mensaje {
  padding: 10px;
  margin: 10px 0;
  font-weight: bold;
  border-radius: 5px;
}

.parametro, .clasificador {
  margin: 10px 0;
}

button {
  background-color: red;
  color: white;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
  margin: 5px;
}

.mensaje.exito {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.mensaje.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
