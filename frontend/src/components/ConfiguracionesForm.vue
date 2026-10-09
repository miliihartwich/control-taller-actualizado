<template>
  <div class="parametros-container">
    <h1 class="titulo">Parámetros</h1>

    <!-- Mensajes -->
    <div v-if="mensaje.texto" :class="['mensaje', mensaje.tipo]">
      {{ mensaje.texto }}
      <div v-if="mensaje.tipo === 'confirmacion'">
        <button @click="guardarConfiguracion(mensaje.clave)">Aceptar</button>
        <button @click="cancelarConfirmacion(mensaje.clave)">Cancelar</button>
      </div>
    </div>

    <!-- Factor Fijo -->
    <div class="parametro">
      <label>Factor fijo</label>
      <input 
        type="text" 
        v-model="configuraciones.factor_fijo" 
        @input="validarNumero('factor_fijo')"
        :disabled="!editando.factor_fijo"
      />
      <button v-if="!editando.factor_fijo" @click="iniciarEdicion('factor_fijo')">Editar</button>
      <button v-else @click="confirmarGuardado('factor_fijo')">Guardar</button>
    </div>

    <!-- Costo Fijo por Hora -->
    <div class="parametro">
      <label>Costo fijo por hora</label>
      <input 
        type="text" 
        v-model="configuraciones.costo_fijo_por_hora" 
        @input="validarNumero('costo_fijo_por_hora')"
        :disabled="!editando.costo_fijo_por_hora"
      />
      <button v-if="!editando.costo_fijo_por_hora" @click="iniciarEdicion('costo_fijo_por_hora')">Editar</button>
      <button v-else @click="confirmarGuardado('costo_fijo_por_hora')">Guardar</button>
    </div>

    <div class="botones">
      <button @click="goTo('MenuPage')" class="botones">Menú</button>
      <button @click="goTo('ConsultaCostosPorOrden')" class="botones">Costos por orden</button>      
    </div>
  </div>
</template>

<script>
import { apiFetch } from '@/api';

export default {
  data() {
    return {
      configuraciones: {},          // p.ej. { factor_fijo: "1.5", costo_fijo_por_hora: "120" }
      valoresAnteriores: {},        // guarda valor previo al editar
      editando: { factor_fijo: false, costo_fijo_por_hora: false },
      mensaje: { texto: '', tipo: '', clave: '' },
    };
  },

  mounted() {
    this.obtenerConfiguraciones();
  },

  methods: {
    async obtenerConfiguraciones() {
      try {
        const data = await apiFetch('/configuraciones'); // devuelve objeto { clave: valor }
        if (data?.error) {
          this.mostrarMensaje('Error al obtener configuraciones', 'error');
          return;
        }
        this.configuraciones = data;
      } catch (error) {
        this.mostrarMensaje('Error en la solicitud: ' + error.message, 'error');
      }
    },

    iniciarEdicion(clave) {
      this.valoresAnteriores[clave] = this.configuraciones[clave];
      this.editando[clave] = true;
    },

    confirmarGuardado(clave) {
      this.mensaje = { texto: `¿Seguro desea editar el ${clave.replace('_', ' ')}?`, tipo: 'confirmacion', clave };
    },

    async guardarConfiguracion(clave) {
      try {
        let nuevoValor = this.configuraciones[clave];

        // normalizar a número (admite coma decimal)
        if (typeof nuevoValor === 'string') {
          nuevoValor = nuevoValor.replace(',', '.').trim();
        }
        if (nuevoValor === '' || isNaN(Number(nuevoValor))) {
          this.mostrarMensaje('El valor debe ser numérico', 'error');
          return;
        }

        const data = await apiFetch(`/configuraciones/${clave}`, {
          method: 'PUT',
          body: { valor: nuevoValor }
        });

        if (data?.error) {
          this.mostrarMensaje('Error al actualizar: ' + data.error, 'error');
        } else {
          this.mostrarMensaje('Configuración actualizada con éxito', 'exito');
          this.editando[clave] = false;
        }
      } catch (error) {
        this.mostrarMensaje('Error en la solicitud: ' + error.message, 'error');
      }
    },

    cancelarConfirmacion(clave) {
      this.configuraciones[clave] = this.valoresAnteriores[clave];
      this.editando[clave] = false;
      this.mensaje = { texto: '', tipo: '', clave: '' };
    },

    validarNumero(clave) {
      // Forzar solo dígitos, punto y coma; convertir coma a punto
      const v = String(this.configuraciones[clave] ?? '');
      this.configuraciones[clave] = v.replace(/[^0-9.,]/g, '').replace(',', '.');
    },

    goTo(routeName) {
      this.$router.push({ name: routeName });
    },

    mostrarMensaje(texto, tipo, clave = '') {
      this.mensaje = { texto, tipo, clave };
      if (tipo !== 'confirmacion') {
        setTimeout(() => { this.mensaje.texto = ''; }, 3000);
      }
    }
  }
};
</script>


<style scoped>
.parametros-container {
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

.mensaje.exito {
  background-color: #4caf50;
  color: white;
}

.mensaje.error {
  background-color: #f44336;
  color: white;
}

.mensaje.confirmacion {
  background-color: #ff9800;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mensaje.confirmacion button {
  margin: 5px;
  background-color: white;
  color: black;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}

.parametro {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 10px 0;
}

input {
  flex: 1;
  margin: 0 10px;
  padding: 5px;
}

button {
  background-color: red;
  color: white;
  padding: 5px 10px;
  border: none;
  cursor: pointer;
}

.botones {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
}
</style>
